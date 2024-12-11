#!/bin/bash
set -e

# Detener y eliminar recursos existentes
echo "Limpiando recursos existentes..."
docker service rm test-postgres-encrypted || true
docker secret rm encrypt_key || true
docker rmi test-postgres-encrypted || true

# Generar una clave de cifrado segura
ENCRYPT_KEY=$(openssl rand -base64 32)
echo "La clave de cifrado generada es: $ENCRYPT_KEY"

# Crear el secreto para Docker Swarm
echo "$ENCRYPT_KEY" | docker secret create encrypt_key -

# Construir la imagen
docker build -t test-postgres-encrypted -f dockerfile_pg_container_acl_encrypt_decrypt_test .

# Inicializar Swarm si es necesario
if ! docker info | grep -q "Swarm: active"; then
    docker swarm init
fi

# Crear el servicio con la variable de entorno
docker service create --name test-postgres-encrypted \
    --secret source=encrypt_key,target=/run/secrets/encrypt_key \
    -e POSTGRES_ENCRYPT_KEY="$ENCRYPT_KEY" \
    -e POSTGRES_USER=test_user \
    -e POSTGRES_PASSWORD=test_password \
    -e POSTGRES_DB=test_db \
    -p 5432:5432 \
    test-postgres-encrypted

echo "Esperando que el servicio esté listo..."
sleep 30

echo "Verificando la base de datos..."
docker exec $(docker ps -q --filter name=test-postgres-encrypted) psql -U postgres -c "SELECT current_database(), version();"
echo "Listo. Puedes probar la conexión con psql -h localhost -U postgres -d test_db"