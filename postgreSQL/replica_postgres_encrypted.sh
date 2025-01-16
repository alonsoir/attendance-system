#!/bin/bash
set -e

echo "=== Escalado de servicio PostgreSQL ==="

# Función para obtener información del servicio
get_service_info() {
    local service_name=$1
    local replicas=$(docker service ls --filter "name=$service_name" --format "{{.Replicas}}")
    local ports=$(docker service inspect $service_name --format '{{range .Endpoint.Ports}}{{.PublishedPort}}{{end}}')
    echo "$service_name ($ports) - Réplicas actuales: $replicas"
}

# Listar servicios PostgreSQL existentes
echo "Servicios PostgreSQL disponibles:"
echo "ID  SERVICIO (PUERTO) - RÉPLICAS"
count=1
while read -r service; do
    # Verificar si es un servicio PostgreSQL mediante la imagen
    if docker service inspect $service --format '{{.Spec.TaskTemplate.ContainerSpec.Image}}' | grep -qi 'postgres'; then
        echo "$count  $(get_service_info $service)"
        ((count++))
    fi
done < <(docker service ls --format "{{.Name}}")

if [ "$count" -eq 1 ]; then
    echo "No se encontraron servicios PostgreSQL"
    exit 0
fi

# Solicitar selección
echo -e "\n¿Qué servicio desea escalar? (Introduzca el número o 'q' para salir)"
read selection

if [ "$selection" = "q" ]; then
    echo "Operación cancelada"
    exit 0
fi

# Validar selección
if ! [[ "$selection" =~ ^[0-9]+$ ]] || [ "$selection" -lt 1 ] || [ "$selection" -ge "$count" ]; then
    echo "Selección inválida"
    exit 1
fi

# Obtener nombre del servicio seleccionado
service_name=$(docker service ls --format "{{.Name}}" | while read service; do
    if docker service inspect $service --format '{{.Spec.TaskTemplate.ContainerSpec.Image}}' | grep -qi 'postgres'; then
        echo $service
    fi
done | sed -n "${selection}p")

# Obtener réplicas actuales
current_replicas=$(docker service ls --filter "name=$service_name" --format "{{.Replicas}}" | cut -d'/' -f1)

echo -e "\nServicio seleccionado: $service_name"
echo "Réplicas actuales: $current_replicas"

# Solicitar número de réplicas
echo -e "\n¿Cuántas réplicas desea? (número >= 0)"
read replicas

# Validar número de réplicas
if ! [[ "$replicas" =~ ^[0-9]+$ ]]; then
    echo "Número de réplicas inválido (debe ser un número entero >= 0)"
    exit 1
fi

# Aviso especial si se establece a 0 réplicas
if [ "$replicas" -eq 0 ]; then
    echo -e "\n¡ATENCIÓN! Establecer 0 réplicas:"
    echo "- El servicio seguirá existiendo pero sin contenedores activos"
    echo "- La configuración y los secrets asociados se mantendrán"
    echo "- El puerto seguirá reservado"
    echo "- Puede volver a escalarlo más tarde para reactivarlo"
fi

# Confirmar acción
echo -e "\nVa a escalar el servicio $service_name de $current_replicas a $replicas réplicas"
read -p "¿Está seguro? (s/n): " confirm
if [ "$confirm" != "s" ]; then
    echo "Operación cancelada"
    exit 0
fi

# Escalar servicio
echo "Escalando servicio..."
docker service scale "$service_name=$replicas"

echo "=== Escalado completado ==="
# Mostrar estado final
echo -e "\nEstado final del servicio:"
docker service ls --filter "name=$service_name"