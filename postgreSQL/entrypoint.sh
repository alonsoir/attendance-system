#!/bin/bash
set -e

# Leer el secreto de Docker Swarm
if [ -f "/run/secrets/encrypt_key" ]; then
    export POSTGRES_ENCRYPT_KEY=$(cat /run/secrets/encrypt_key)
else
    echo "Error: No se encontró el secreto encrypt_key"
    exit 1
fi

# Iniciar PostgreSQL usando el entrypoint oficial
exec docker-entrypoint.sh postgres