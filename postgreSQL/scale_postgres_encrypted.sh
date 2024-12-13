#!/bin/bash
set -e

echo "=== Iniciando despliegue de PostgreSQL con encriptación autogestionada ==="

# Función para generar nombre aleatorio
generate_random_name() {
    # Generar un prefijo aleatorio de 8 caracteres
    prefix=$(cat /dev/urandom | tr -dc 'a-z' | fold -w 8 | head -n 1)
    # Añadir timestamp para unicidad
    suffix=$(date +%s | sha256sum | base64 | head -c 6)
    echo "pg-${prefix}-${suffix}"
}

# Función para encontrar un puerto aleatorio disponible
find_random_port() {
    while true; do
        # Generar puerto aleatorio entre 10000 y 65000
        local port=$(( RANDOM % 55000 + 10000 ))

        # Verificar si el puerto está en uso por servicios Docker
        if docker service ls --format "{{.Ports}}" | grep -q ":$port->"; then
            continue
        fi

        # Verificar si el puerto está en uso localmente
        if netstat -tna | grep -q ":$port "; then
            continue
        fi

        # Si llegamos aquí, el puerto está libre
        echo $port
        break
    done
}

# Generar nombres aleatorios para servicio y secret
SERVICE_NAME=$(generate_random_name)
SECRET_NAME="${SERVICE_NAME/pg/key}"

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

# Encontrar puerto aleatorio disponible
PORT=$(find_random_port)
echo "=== Configuración del servicio ==="
echo "Nombre del servicio: $SERVICE_NAME"
echo "Nombre del secret  : $SECRET_NAME"
echo "Puerto asignado   : $PORT"

# Solicitar confirmación
read -p "¿Desea continuar con este despliegue? (s/n): " confirm
if [ "$confirm" != "s" ]; then
    echo "Operación cancelada"
    exit 0
fi

# Crear nueva instancia del servicio
echo -e "\n=== Creando nueva instancia PostgreSQL ==="
docker service create --name $SERVICE_NAME \
    -e POSTGRES_USER=test_user \
    -e POSTGRES_PASSWORD=test_password \
    -e POSTGRES_DB=test_db \
    -p $PORT:5432 \
    --label "service.type=postgresql" \
    --label "service.created=$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    test-postgres-encrypted

# Esperar que el servicio esté listo
echo "=== Esperando que el servicio esté completamente listo... ==="
wait_service_ready $SERVICE_NAME

# Extraer y guardar la clave en Docker Secrets
echo "=== Extrayendo y guardando la clave de encriptación... ==="
container_id=$(docker ps -q --filter name=$SERVICE_NAME)
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
        echo "$encrypt_key" | docker secret create $SECRET_NAME -
        echo "- Clave guardada exitosamente"

        # Añadir etiquetas al servicio para mejor seguimiento
        docker service update --label-add "secret.name=$SECRET_NAME" $SERVICE_NAME > /dev/null 2>&1
    else
        echo "ERROR: No se pudo extraer la clave de encriptación"
        exit 1
    fi
else
    echo "ERROR: No se encontró el contenedor"
    exit 1
fi

echo -e "\n=== Resumen del despliegue ==="
echo "Servicio:"
docker service inspect $SERVICE_NAME --format "ID: {{.ID}}\nNombre: {{.Spec.Name}}\nPuerto: $PORT\nCreado: {{.CreatedAt}}"
echo -e "\nSecret:"
docker secret ls --filter "name=$SECRET_NAME" --format "ID: {{.ID}}\nNombre: {{.Name}}\nCreado: {{.CreatedAt}}"

echo -e "\n=== Despliegue completado exitosamente ==="
echo "Para conectarse al servicio:"
echo "psql -h localhost -p $PORT -U test_user -d test_db"