#!/bin/bash
set -e

echo "=== Iniciando script de configuración de PostgreSQL con encriptación ==="

# Detener y eliminar recursos existentes
echo "=== Limpiando recursos existentes... ==="
echo "- Eliminando servicio anterior si existe..."
docker service rm test-postgres-encrypted || true
echo "- Eliminando secreto anterior si existe..."
docker secret rm encrypt_key || true
echo "- Eliminando imagen anterior si existe..."
docker rmi test-postgres-encrypted || true

# Generar una clave de cifrado segura
echo "=== Generando nueva clave de cifrado... ==="
ENCRYPT_KEY=$(openssl rand -base64 32)
echo "La clave de cifrado generada es: $ENCRYPT_KEY"

# Crear el secreto para Docker Swarm
echo "=== Creando secreto en Docker Swarm... ==="
echo "$ENCRYPT_KEY" | docker secret create encrypt_key -
echo "- Secreto creado exitosamente"

# Construir la imagen
echo "=== Construyendo imagen Docker... ==="
docker build -t test-postgres-encrypted -f dockerfile_pg_container_acl_encrypt_decrypt_test .
echo "- Imagen construida exitosamente"

# Inicializar Swarm si es necesario
echo "=== Verificando Docker Swarm... ==="
if ! docker info | grep -q "Swarm: active"; then
    echo "- Swarm no está activo, inicializando..."
    docker swarm init
else
    echo "- Swarm ya está activo"
fi

# Crear el servicio con la variable de entorno
echo "=== Creando servicio en Docker Swarm... ==="
docker service create --name test-postgres-encrypted \
    --secret source=encrypt_key,target=/run/secrets/encrypt_key \
    -e POSTGRES_USER=test_user \
    -e POSTGRES_PASSWORD=test_password \
    -e POSTGRES_DB=test_db \
    -p 5432:5432 \
    test-postgres-encrypted

echo "=== Esperando que el servicio esté listo... ==="
echo "- Esperando 60 segundos para asegurar inicialización completa..."
sleep 60

# Verificar que el servicio está funcionando
echo "=== Verificando estado del servicio... ==="
echo "- Lista de servicios:"
docker service ls
echo "- Estado del servicio test-postgres-encrypted:"
docker service ps test-postgres-encrypted

echo "=== Verificando la base de datos... ==="
CONTAINER_ID=$(docker ps -q --filter name=test-postgres-encrypted)
if [ -z "$CONTAINER_ID" ]; then
    echo "ERROR: No se encontró el contenedor en ejecución"
    exit 1
fi
echo "- ID del contenedor: $CONTAINER_ID"

# Esperar hasta que PostgreSQL esté listo para aceptar conexiones
echo "=== Esperando que PostgreSQL esté listo para aceptar conexiones... ==="
until docker exec $CONTAINER_ID pg_isready; do
    echo "- PostgreSQL aún no está listo... esperando 5 segundos"
    sleep 5
done

echo "=== Verificando conexiones de base de datos... ==="
echo "- Intentando conexión con el usuario test_user..."
if docker exec $CONTAINER_ID psql -U test_user -d test_db -c "\l"; then
    echo "  - Conexión exitosa con test_user"
else
    echo "  - Error al conectar con test_user"
fi

echo "- Intentando conexión con el usuario postgres..."
if docker exec $CONTAINER_ID psql -U postgres -c "\l"; then
    echo "  - Conexión exitosa con postgres"
else
    echo "  - Error al conectar con postgres"
fi

echo "=== Verificando configuración de encriptación... ==="
echo "- Intentando verificar la clave de encriptación..."
docker exec $CONTAINER_ID psql -U test_user -d test_db -c "SELECT CASE WHEN get_encryption_key() IS NOT NULL THEN 'Clave de encriptación configurada correctamente' ELSE 'Error en la clave de encriptación' END;"

echo "=== Verificación de logs del contenedor... ==="
echo "- Últimas 20 líneas de log del servicio:"
docker service logs --tail 20 test-postgres-encrypted

echo "=== Script completado ==="
echo "Para conectarse a la base de datos use:"
echo "psql -h localhost -U test_user -d test_db"