#!/bin/bash

# Eliminar contenedores existentes
docker rm -f consul vault db || echo "No se encontraron contenedores con esos nombres"

# Eliminar red existente
docker network rm vault-consul-network || echo "La red vault-consul-network no existe"

# Eliminar volúmenes existentes
docker volume rm consul-data vault-data db-data || echo "Los volúmenes consul-data y vault-data no existen"

echo "Contenedores, redes y volúmenes eliminados correctamente"
