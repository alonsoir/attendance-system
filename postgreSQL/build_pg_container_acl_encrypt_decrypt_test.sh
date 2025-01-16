#!/bin/bash
set -e

# Este script crea una imagen de Docker con PostgreSQL configurado para encriptación de datos con
# claves autogestionadas.
# Con el paso del tiempo voy añadiendo más funcionalidades.
# Ahora mismo, hay encriptación de datos, SSL, particionado de tablas, seguridad, informes, procedimientos almacenados,
# acl.
# También se añade un cronjob para realizar copias de seguridad de la base de datos.

IMAGE_NAME="test-postgres-full-citus"

SERVICE_NAME="test-postgres-full-citus"
SECRET_NAME="postgres_encrypt_key"

echo "=== Iniciando configuración de PostgreSQL con encriptación autogestionada ==="

# Limpiar recursos existentes
echo "=== Limpiando recursos antiguos... ==="
if docker images | grep -q "$IMAGE_NAME"; then
    echo "- Eliminando imagen existente..."
    docker rmi -f "$IMAGE_NAME"
fi

if docker secret ls | grep -q "$SECRET_NAME"; then
    echo "- Eliminando secreto existente..."
    docker secret rm "$SECRET_NAME"
fi

echo "=== Construyendo nueva imagen... ==="
docker build -t "$IMAGE_NAME" -f Dockerfile .

# Verificar Swarm
echo "=== Verificando Docker Swarm... ==="
if ! docker info | grep -q "Swarm: active"; then
    echo "- Inicializando Docker Swarm..."
    docker swarm init
else
    echo "- Swarm ya está activo"
fi

# Crear servicio temporal para extraer clave
echo "=== Creando servicio temporal PostgreSQL... ==="
docker service create --name "$SERVICE_NAME" \
    -e POSTGRES_USER=test_user \
    -e POSTGRES_PASSWORD=test_password \
    -e POSTGRES_DB=test_db \
    "$IMAGE_NAME"

# Esperar que el servicio esté listo
echo "=== Esperando que el servicio esté completamente listo... ==="
until docker service ps "$SERVICE_NAME" | grep -q "Running"; do
    echo "- Servicio aún no está listo..."
    sleep 2
done
echo "- Servicio está listo"

# Extraer clave de encriptación
echo "=== Extrayendo clave de encriptación... ==="
container_id=$(docker ps -q --filter "name=${SERVICE_NAME}")
if [ -n "$container_id" ]; then
    echo "- Contenedor encontrado: $container_id"

    echo "- Esperando que PostgreSQL esté listo..."
    until docker exec "$container_id" pg_isready -U test_user; do
        echo "  PostgreSQL aún no está listo..."
        sleep 2
    done

    echo "- Extrayendo clave de encriptación..."
    encrypt_key=$(docker exec "$container_id" psql -U test_user -d test_db -t -c \
        "SELECT key_value FROM encryption_config WHERE key_name = 'main_key';")

    if [ -n "$encrypt_key" ]; then
        echo "- Guardando clave en Docker Secrets..."
        echo "$encrypt_key" | docker secret create "$SECRET_NAME" -
        echo "- Clave guardada exitosamente en Docker Secrets"

        # La transferencia al Vault se delega al init-swarm.sh
        echo "- Clave disponible en Docker Secrets, lista para transferencia al Vault"
    else
        echo "ERROR: No se pudo extraer la clave de encriptación"
        exit 1
    fi
else
    echo "ERROR: No se encontró el contenedor"
    exit 1
fi

# Limpiar servicio temporal
echo "=== Limpiando servicio temporal... ==="
docker service rm "$SERVICE_NAME"

echo "=== Configuración completada exitosamente ==="
