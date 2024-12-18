#!/bin/bash

# Nombre del stack
STACK_NAME="attendance_cluster"
COMPOSE_FILE="docker-compose.yml"

# Función para inicializar Docker Swarm
initialize_swarm() {
  echo "### Inicializando Docker Swarm..."

  # Verificar si el nodo ya es parte de un swarm
  if docker info --format '{{.Swarm.LocalNodeState}}' | grep -q 'active'; then
    echo "El nodo ya es parte de un swarm."
  else
    docker swarm init 2>&1 | tee -a swarm_init.log

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
    docker swarm leave --force 2>&1 | tee -a swarm_init.log
    docker swarm init 2>&1 | tee -a swarm_init.log

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
  docker stack deploy -c "${COMPOSE_FILE}" "${STACK_NAME}" 2>&1 | tee -a stack_deploy.log

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
  docker stack services "${STACK_NAME}" 2>&1 | tee -a services_status.log
}

# Función para listar nodos
check_nodes() {
  echo "### Listando los nodos del clúster..."
  docker node ls 2>&1 | tee -a nodes_list.log
}

# Función para listar contenedores activos
list_containers() {
  echo "### Listando contenedores activos..."
  docker ps 2>&1 | tee -a active_containers.log
}

# Función principal
main() {
  initialize_swarm
  deploy_stack
  echo
  check_services
  echo
  check_nodes
  echo
  list_containers
  echo "### El clúster ha sido inicializado y verificado correctamente."
}

# Ejecutar el script
main
