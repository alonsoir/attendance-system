#!/bin/bash

# Nombre del stack y configuración
STACK_NAME="attendance_cluster"
COMPOSE_FILE="docker-compose.yml"
LOG_DIR="logs"

# Crear directorio de logs si no existe
mkdir -p ${LOG_DIR}

# Función para limpiar el entorno previo
cleanup_environment() {
    echo "### Limpiando entorno previo..."

    # Eliminar stack previo si existe
    if docker stack ls | grep -q "${STACK_NAME}"; then
        echo "Eliminando stack previo..."
        docker stack rm "${STACK_NAME}" 2>&1 | tee -a "${LOG_DIR}/cleanup.log"
        # Esperar a que el stack se elimine completamente
        while docker stack ls | grep -q "${STACK_NAME}"; do
            sleep 1
        done
    fi

    # Eliminar contenedores relacionados
    echo "Eliminando contenedores previos..."
    containers=$(docker ps -a --filter name="${STACK_NAME}" -q)
    if [ ! -z "$containers" ]; then
        docker rm -f $containers 2>&1 | tee -a "${LOG_DIR}/cleanup.log"
    fi

    # Eliminar imágenes previas
    echo "Eliminando imágenes previas..."
    images=("backend-attendance" "frontend-attendance" "test-postgres-encrypted")
    for img in "${images[@]}"; do
        if docker images | grep -q "$img"; then
            docker rmi -f $(docker images "$img" -q) 2>&1 | tee -a "${LOG_DIR}/cleanup.log"
        fi
    done

    # Eliminar volúmenes relacionados
    echo "Eliminando volúmenes previos..."
    volumes=$(docker volume ls --filter name="${STACK_NAME}" -q)
    if [ ! -z "$volumes" ]; then
        docker volume rm $volumes 2>&1 | tee -a "${LOG_DIR}/cleanup.log"
    fi

    # Limpiar redes huérfanas
    echo "Limpiando redes..."
    docker network prune -f 2>&1 | tee -a "${LOG_DIR}/cleanup.log"

    echo "Limpieza completada"
}

# Función para construir las imágenes Docker
build_images() {
    echo "### Construyendo imágenes Docker..."

    echo "Construyendo imagen del backend..."
    docker build -t backend-attendance:latest -f ./backend/Dockerfile . 2>&1 | tee -a "${LOG_DIR}/build_backend.log"
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        echo "Error construyendo imagen del backend."
        exit 1
    fi

    echo "Construyendo imagen del frontend..."
    docker build -t frontend-attendance:latest -f ./frontend/Dockerfile ./frontend 2>&1 | tee -a "${LOG_DIR}/build_frontend.log"
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        echo "Error construyendo imagen del frontend."
        exit 1
    fi

    echo "Construyendo imagen de PostgreSQL..."
    (cd ./postgresql && ./build_pg_container_acl_encrypt_decrypt_test.sh) 2>&1 | tee -a "${LOG_DIR}/build_postgres.log"
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        echo "Error construyendo imagen de PostgreSQL."
        exit 1
    fi

    # Listar imágenes construidas
    echo "Imágenes construidas:"
    docker images | grep -E 'backend-attendance|frontend-attendance|test-postgres-encrypted' 2>&1 | tee -a "${LOG_DIR}/build_images.log"
}

# Función para inicializar Docker Swarm
initialize_swarm() {
    echo "### Inicializando Docker Swarm..."

    # Verificar si el nodo ya es parte de un swarm
    if docker info --format '{{.Swarm.LocalNodeState}}' | grep -q 'active'; then
        echo "El nodo ya es parte de un swarm."
    else
        docker swarm init --advertise-addr 127.0.0.1 2>&1 | tee -a "${LOG_DIR}/swarm_init.log"

        if [ $? -eq 0 ]; then
            echo "Docker Swarm inicializado correctamente."
        else
            echo "Error al inicializar Docker Swarm."
            exit 1
        fi
    fi

    # Verificar si el nodo es un manager
    if docker info --format '{{.Swarm.ControlAvailable}}' | grep -q 'true'; then
        echo "El nodo es un manager en el swarm."
    else
        echo "El nodo no es un manager en el swarm. Intentando promover el nodo a manager..."
        docker swarm leave --force 2>&1 | tee -a "${LOG_DIR}/swarm_init.log"
        docker swarm init --advertise-addr 127.0.0.1 2>&1 | tee -a "${LOG_DIR}/swarm_init.log"

        if [ $? -eq 0 ]; then
            echo "El nodo ha sido promovido a manager correctamente."
        else
            echo "Error al promover el nodo a manager."
            exit 1
        fi
    fi
}

# Función para desplegar el stack
deploy_stack() {
    echo "### Desplegando el stack '${STACK_NAME}'..."
    docker stack deploy -c "${COMPOSE_FILE}" "${STACK_NAME}" 2>&1 | tee -a "${LOG_DIR}/stack_deploy.log"

    if [ $? -eq 0 ]; then
        echo "Stack '${STACK_NAME}' desplegado correctamente."
    else
        echo "Error al desplegar el stack '${STACK_NAME}'."
        exit 1
    fi
}

# Función para verificar el estado de los servicios
check_services() {
    echo "### Comprobando el estado de los servicios..."
    docker stack services "${STACK_NAME}" 2>&1 | tee -a "${LOG_DIR}/services_status.log"
}

# Función para listar nodos
check_nodes() {
    echo "### Listando los nodos del clúster..."
    docker node ls 2>&1 | tee -a "${LOG_DIR}/nodes_list.log"
}

# Función para listar contenedores activos
list_containers() {
    echo "### Listando contenedores activos..."
    docker ps 2>&1 | tee -a "${LOG_DIR}/active_containers.log"
}

# Función para mostrar logs de servicios
show_service_logs() {
    echo "### Mostrando logs de los servicios..."

    # Esperar un poco para que los servicios inicien y generen logs
    sleep 10

    services=$(docker service ls --format "{{.ID}}:{{.Name}}" | grep "${STACK_NAME}")
    for service in $services; do
        IFS=':' read -r id name <<< "$service"
        echo -e "\n### Logs del servicio ${name} (ID: ${id}):"
        docker service logs ${id} --tail 1000 2>&1 | tee -a "${LOG_DIR}/${name}_logs.log" || echo "No hay logs disponibles para ${name}"
    done
}

# Función principal
main() {
    cleanup_environment
    build_images
    initialize_swarm
    deploy_stack
    echo
    check_services
    echo
    check_nodes
    echo
    list_containers
    show_service_logs
    echo "### El clúster ha sido inicializado y verificado correctamente."
}

# Ejecutar el script
main