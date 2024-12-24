#!/bin/bash

docker stop consul vault vault-init db || echo "No se encontraron contenedores con esos nombres"
# Eliminar contenedores existentes
docker rm -f consul vault vault-init db || echo "No se encontraron contenedores con esos nombres"

# Eliminar redes existente
docker network rm vault-consul-network || echo "La red vault-consul-network no existe"

docker network rm attendance_system_default || echo "La red attendance_system_default no existe"

docker network rm none || echo "La red none no existe"

docker network rm bridge || echo "La red bridge no existe"

docker network rm host || echo "La red host no existe"

docker network rm docker_gwbridge || echo "La red docker_gwbridge no existe"

docker network rm ingress || echo "La red ingress no existe"

# Eliminar volúmenes existentes
docker volume rm consul-data vault-data db-data || echo "Los volúmenes consul-data y vault-data no existen"

echo "Contenedores, redes y volúmenes eliminados correctamente"
