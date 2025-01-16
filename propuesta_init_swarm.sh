#!/bin/bash
set -e

# Variables
COMPOSE_FILE="docker-compose.yml"
VAULT_SERVICE="vault"
SECRETS=("postgres_encrypt_key")
VAULT_TOKEN="attendance_root_token"
VAULT_ADDR="http://127.0.0.1:8200"

echo "=== Inicializando Docker Swarm ==="

# Limpiar estado previo
if docker info | grep -q "Swarm: active"; then
    echo "- Docker Swarm ya está activo. Reinicializando..."
    docker swarm leave --force
fi
docker swarm init

# Limpiar secretos antiguos
echo "=== Limpiando secretos antiguos... ==="
for secret in "${SECRETS[@]}"; do
    if docker secret ls | grep -q "$secret"; then
        echo "- Eliminando secreto $secret..."
        docker secret rm "$secret"
    fi
done

# Construir imágenes
echo "=== Construyendo imágenes... ==="
docker compose -f "$COMPOSE_FILE" build

# Levantar servicios
echo "=== Levantando servicios... ==="
docker compose -f "$COMPOSE_FILE" up -d

# Verificar que Vault esté listo
echo "=== Verificando estado del servicio Vault... ==="
until docker ps | grep -q "$VAULT_SERVICE"; do
    echo "- Esperando que Vault se levante..."
    sleep 2
done

echo "- Esperando que Vault esté completamente listo..."
until curl -s "$VAULT_ADDR/v1/sys/health" | grep -q "\"initialized\":true"; do
    echo "- Vault aún no está listo..."
    sleep 5
done
echo "- Vault está listo."

# Transferir secretos a Vault
echo "=== Transfiriendo secretos a Vault... ==="
for secret in "${SECRETS[@]}"; do
    echo "- Recuperando secreto $secret de Docker Secrets..."
    secret_value=$(docker secret inspect "$secret" -f '{{ .Spec.Data }}' | base64 --decode)
    if [ -n "$secret_value" ]; then
        echo "- Transfiriendo $secret a Vault..."
        curl -s --header "X-Vault-Token: $VAULT_TOKEN" \
            --request POST \
            --data "{\"data\": {\"value\": \"$secret_value\"}}" \
            "$VAULT_ADDR/v1/secret/data/$secret"
        echo "- Secreto $secret transferido a Vault."
    else
        echo "ERROR: No se pudo recuperar el secreto $secret."
    fi
done

# Mostrar logs de los servicios
echo "=== Mostrando logs de servicios... ==="
docker compose -f "$COMPOSE_FILE" logs -f
