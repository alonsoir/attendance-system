#!/bin/bash

# Nombre del stack
STACK_NAME="attendance_cluster"

# Función para eliminar el stack
remove_stack() {
  echo "### Eliminando el stack '${STACK_NAME}'..."
  docker stack rm "${STACK_NAME}" 2>&1 | tee -a stack_remove.log

  if [ $? -eq 0 ]; then
    echo "Stack '${STACK_NAME}' eliminado correctamente."
  else
    echo "Error al eliminar el stack '${STACK_NAME}'."
    exit 1
  fi
}

# Función para salir de Docker Swarm
leave_swarm() {
  echo "### Cerrando el clúster Docker Swarm..."
  docker swarm leave --force 2>&1 | tee -a swarm_leave.log

  if [ $? -eq 0 ]; then
    echo "Clúster Docker Swarm cerrado correctamente."
  else
    echo "Error al cerrar el clúster Docker Swarm."
    exit 1
  fi
}

# Función principal
main() {
  remove_stack
  echo
  leave_swarm
  echo "### El clúster ha sido cerrado correctamente."
}

# Ejecutar el script
main
