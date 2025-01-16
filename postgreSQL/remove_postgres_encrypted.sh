#!/bin/bash
set -e

echo "=== Iniciando descubrimiento y retirada de servicios PostgreSQL ==="

# Función para obtener información detallada de un servicio
get_service_info() {
    local service_name=$1
    local port=$(docker service inspect $service_name --format '{{range .Endpoint.Ports}}{{.PublishedPort}}{{end}}')
    local image=$(docker service inspect $service_name --format '{{.Spec.TaskTemplate.ContainerSpec.Image}}')
    local created=$(docker service inspect $service_name --format '{{.CreatedAt}}')
    echo "$service_name:$port:$image:$created"
}

# Función para verificar transacciones pendientes
check_pending_transactions() {
    local container_id=$1
    local count=$(docker exec $container_id psql -U test_user -d test_db -t -c \
        "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND pid != pg_backend_pid();")
    echo $count
}

# Descubrir todos los servicios PostgreSQL
echo "Descubriendo servicios PostgreSQL..."
postgres_services=$(docker service ls --format '{{.Name}}' | while read service; do
    # Verificar si es un servicio PostgreSQL mediante la imagen
    if docker service inspect $service --format '{{.Spec.TaskTemplate.ContainerSpec.Image}}' | grep -qi 'postgres'; then
        get_service_info $service
    fi
done)

if [ -z "$postgres_services" ]; then
    echo "No se encontraron servicios PostgreSQL"
    exit 0
fi

# Mostrar servicios encontrados
echo -e "\nServicios PostgreSQL encontrados:"
echo -e "ID\tNOMBRE\tPUERTO\tIMAGEN\tCREADO"
count=1
while IFS=: read -r name port image created; do
    echo -e "$count\t$name\t$port\t$image\t$created"
    ((count++))
done <<< "$postgres_services"

# Preguntar al operador qué servicio retirar
echo -e "\n¿Qué servicio desea retirar? (Introduzca el número o 'q' para salir)"
read selection

if [ "$selection" = "q" ]; then
    echo "Operación cancelada"
    exit 0
fi

# Validar selección
if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -gt "$count" ]; then
    echo "Selección inválida"
    exit 1
fi

# Obtener información del servicio seleccionado
selected_service=$(echo "$postgres_services" | sed -n "${selection}p")
IFS=: read -r service_name port image created <<< "$selected_service"

echo -e "\n=== Procesando servicio seleccionado ==="
echo "Nombre: $service_name"
echo "Puerto: $port"
echo "Imagen: $image"
echo "Creado: $created"

# Obtener confirmación
read -p "¿Está seguro de que desea retirar este servicio? (s/n): " confirm
if [ "$confirm" != "s" ]; then
    echo "Operación cancelada"
    exit 0
fi

# Obtener ID del contenedor
container_id=$(docker ps -q --filter name=$service_name)
if [ -n "$container_id" ]; then
    # Verificar transacciones pendientes
    pending=$(check_pending_transactions $container_id)
    if [ "$pending" -gt "0" ]; then
        echo "ADVERTENCIA: Hay $pending transacciones activas"
        read -p "¿Desea esperar y reintentar? (s/n): " wait_response
        if [ "$wait_response" = "s" ]; then
            echo "Esperando a que finalicen las transacciones..."
            while [ "$(check_pending_transactions $container_id)" -gt "0" ]; do
                echo "- Aún hay transacciones pendientes..."
                sleep 5
            done
        else
            echo "Operación cancelada"
            exit 0
        fi
    fi
fi

# Retirar el servicio
echo "Retirando servicio $service_name..."
docker service rm $service_name

# Buscar y eliminar secrets asociados
echo "Buscando secrets asociados..."
docker secret ls --format '{{.Name}}' | while read secret; do
    if [[ "$secret" =~ ${service_name/postgres/encrypt_key} ]]; then
        echo "Eliminando secret: $secret"
        docker secret rm $secret
    fi
done

echo "=== Servicio retirado exitosamente ==="