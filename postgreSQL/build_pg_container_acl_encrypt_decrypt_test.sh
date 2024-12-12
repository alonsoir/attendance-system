#!/bin/bash
set -e

echo "=== Iniciando configuración de PostgreSQL con encriptación autogestionada ==="

# Función para esperar que un servicio se elimine
wait_service_removal() {
    local service_name=$1
    local max_attempts=30
    local attempt=1

    while docker service ls | grep -q "$service_name"; do
        echo "- Intento $attempt: Esperando que el servicio $service_name se elimine..."
        if [ $attempt -ge $max_attempts ]; then
            echo "ERROR: Timeout esperando que el servicio se elimine"
            exit 1
        fi
        sleep 2
        ((attempt++))
    done
    echo "- Servicio $service_name eliminado correctamente"
}

# Función para esperar que una imagen se elimine
wait_image_removal() {
    local image_name=$1
    local max_attempts=30
    local attempt=1

    while docker images | grep -q "$image_name"; do
        echo "- Intento $attempt: Esperando que la imagen $image_name se elimine..."
        if [ $attempt -ge $max_attempts ]; then
            echo "ERROR: Timeout esperando que la imagen se elimine"
            exit 1
        fi
        sleep 2
        ((attempt++))
    done
    echo "- Imagen $image_name eliminada correctamente"
}

# Función para esperar que el servicio esté listo
wait_service_ready() {
    local service_name=$1
    local max_attempts=60
    local attempt=1

    while true; do
        if docker service ls | grep "$service_name" | grep -q "1/1"; then
            echo "- Servicio $service_name está listo"
            return 0
        fi

        if [ $attempt -ge $max_attempts ]; then
            echo "ERROR: Timeout esperando que el servicio esté listo"
            exit 1
        fi

        echo "- Intento $attempt: Esperando que el servicio esté listo..."
        sleep 2
        ((attempt++))
    done
}

# Limpiar recursos existentes
echo "=== Limpiando recursos antiguos... ==="
echo "- Eliminando servicio anterior si existe..."
if docker service ls | grep -q "test-postgres-encrypted"; then
    docker service rm test-postgres-encrypted
    wait_service_removal "test-postgres-encrypted"
fi

echo "- Eliminando imagen anterior si existe..."
if docker images | grep -q "test-postgres-encrypted"; then
    docker rmi -f test-postgres-encrypted
    wait_image_removal "test-postgres-encrypted"
fi

echo "- Eliminando secretos antiguos si existen..."
if docker secret ls | grep -q "postgres_encrypt_key"; then
    docker secret rm postgres_encrypt_key || true
fi

# Construir imagen
echo "=== Construyendo nueva imagen... ==="
docker build -t test-postgres-encrypted -f dockerfile_pg_container_acl_encrypt_decrypt_test .

# Verificar Swarm
echo "=== Verificando Docker Swarm... ==="
if ! docker info | grep -q "Swarm: active"; then
    echo "- Inicializando Docker Swarm..."
    docker swarm init
else
    echo "- Swarm ya está activo"
fi

# Crear servicio
echo "=== Creando servicio PostgreSQL... ==="
docker service create --name test-postgres-encrypted \
    -e POSTGRES_USER=test_user \
    -e POSTGRES_PASSWORD=test_password \
    -e POSTGRES_DB=test_db \
    -p 5432:5432 \
    test-postgres-encrypted

# Esperar que el servicio esté listo
echo "=== Esperando que el servicio esté completamente listo... ==="
wait_service_ready "test-postgres-encrypted"

# Extraer y guardar la clave en Docker Secrets
echo "=== Extrayendo y guardando la clave de encriptación... ==="
container_id=$(docker ps -q --filter name=test-postgres-encrypted)
if [ -n "$container_id" ]; then
    echo "- Contenedor encontrado: $container_id"

    # Esperar que PostgreSQL esté listo
    echo "- Esperando que PostgreSQL esté listo..."
    until docker exec $container_id pg_isready -U test_user; do
        echo "  PostgreSQL aún no está listo..."
        sleep 2
    done

    echo "- Extrayendo clave de encriptación..."
    encrypt_key=$(docker exec $container_id psql -U test_user -d test_db -t -c \
        "SELECT key_value FROM encryption_config WHERE key_name = 'main_key';")

    if [ -n "$encrypt_key" ]; then
        echo "- Guardando clave en Docker Secrets..."
        echo "$encrypt_key" | docker secret create postgres_encrypt_key -
        echo "- Clave guardada exitosamente en Docker Secrets"

        echo "- Verificando secret creado:"
        docker secret ls | grep postgres_encrypt_key
    else
        echo "ERROR: No se pudo extraer la clave de encriptación"
        exit 1
    fi
else
    echo "ERROR: No se encontró el contenedor"
    exit 1
fi

echo "=== Verificando estado final... ==="
echo "- Estado del servicio:"
docker service ls
echo "- Estado de los secretos:"
docker secret ls

echo "=== Configuración completada exitosamente ==="