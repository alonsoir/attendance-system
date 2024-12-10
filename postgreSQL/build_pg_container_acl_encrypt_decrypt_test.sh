#!/bin/bash

# Detener y eliminar el servicio si está corriendo
docker service rm test-postgres-encrypted

# Eliminar la imagen anterior si no está en uso
docker rmi test-postgres-encrypted || true

# Generar una clave de cifrado segura
ENCRYPT_KEY=$(openssl rand -base64 32)

echo "La clave de cifrado generada es: $ENCRYPT_KEY"
echo "Asegúrate de guardar esta clave en un lugar seguro."

# Construir la imagen de nuevo con los cambios en el Dockerfile
docker build -t test-postgres-encrypted -f dockerfile_pg_container_acl_encrypt_decrypt_test .

# Esperar a que la imagen se construya
echo "Esperando 20 segundos a que la imagen test-postgres-encrypted esté completamente construida..."
sleep 20

# Verificar si Docker Swarm ya está inicializado
if ! docker info | grep -q "Swarm: active"; then
  docker swarm init
fi

# Crear un secreto para la clave de cifrado si no existe
if ! docker secret ls | grep -q "encrypt_key"; then
  echo "$ENCRYPT_KEY" | docker secret create encrypt_key -
fi

# Crear un servicio en Docker Swarm
docker service create --name test-postgres-encrypted \
  --secret encrypt_key \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_password \
  -e POSTGRES_DB=test_db \
  -p 5432:5432 \
  test-postgres-encrypted

# Esperar a que el servicio esté listo
echo "Esperando 40 segundos a que PostgreSQL esté completamente iniciado..."
sleep 40

# Verificar la versión de PostgreSQL
echo "Verificando la versión de PostgreSQL..."
POSTGRES_VERSION=$(docker exec -it $(docker service ps -q test-postgres-encrypted) psql -U postgres -c "SHOW server_version;" | grep -o '[0-9]*\.[0-9]*')
if [ "$POSTGRES_VERSION" != "15.0" ]; then
  echo "Error: La versión de PostgreSQL no es la esperada (15.0). Versión actual: $POSTGRES_VERSION"
  exit 1
fi

# Verificar extensiones cargadas
echo "Verificando extensiones cargadas..."
EXTENSIONS=$(docker exec -it $(docker service ps -q test-postgres-encrypted) psql -U postgres -c "SELECT extname FROM pg_extension;" | tr -d '| ')
if ! echo "$EXTENSIONS" | grep -q "pgcrypto"; then
  echo "Error: La extensión pgcrypto no está cargada."
  exit 1
fi
if ! echo "$EXTENSIONS" | grep -q "uuid-ossp"; then
  echo "Error: La extensión uuid-ossp no está cargada."
  exit 1
fi

# Verificar procedimientos almacenados
echo "Verificando procedimientos almacenados..."
PROCEDURES=$(docker exec -it $(docker service ps -q test-postgres-encrypted) psql -U postgres -d test_db -c "\df" | awk '{print $2}')
if ! echo "$PROCEDURES" | grep -q "get_encrypted_schools"; then
  echo "Error: El procedimiento almacenado get_encrypted_schools no existe."
  exit 1
fi
if ! echo "$PROCEDURES" | grep -q "create_encrypted_school"; then
  echo "Error: El procedimiento almacenado create_encrypted_school no existe."
  exit 1
fi
if ! echo "$PROCEDURES" | grep -q "update_encrypted_school"; then
  echo "Error: El procedimiento almacenado update_encrypted_school no existe."
  exit 1
fi
if ! echo "$PROCEDURES" | grep -q "delete_school"; then
  echo "Error: El procedimiento almacenado delete_school no existe."
  exit 1
fi

echo "Verificación de la imagen de PostgreSQL completada satisfactoriamente."

# Detener y eliminar el servicio
docker service rm test-postgres-encrypted

# Eliminar el nodo de Docker Swarm
docker swarm leave --force
