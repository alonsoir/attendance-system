#!/bin/bash
set -e

wait_for_service() {
    local host=$1
    local port=$2
    echo "Esperando a que $host:$port esté disponible..."
    while ! nc -z "$host" "$port"; do
        echo "Esperando a que $host:$port..."
        sleep 2
    done
}

# Verificar dependencias
wait_for_service "$POSTGRES_SERVER" "$POSTGRES_PORT"
wait_for_service "$REDIS_HOST" "$REDIS_PORT"

# Iniciar el backend
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
