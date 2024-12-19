#!/bin/bash
set -euo pipefail

# Configuración
LOG_FILE="/app/logs/secret-rotation.log"
ROTATION_INTERVAL=86400  # 24 horas en segundos
MAX_RETRIES=3
RETRY_DELAY=5

# Función de logging
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$LOG_FILE"
}

# Función para rotar un secreto en Docker Swarm
rotate_docker_secret() {
    local secret_name="$1"
    local service_name="$2"
    local new_value="$(openssl rand -base64 32)"
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        # Crear nuevo secreto con timestamp
        local timestamp=$(date +%s)
        local new_secret_name="${secret_name}_${timestamp}"

        if echo "$new_value" | docker secret create "$new_secret_name" - > /dev/null; then
            # Actualizar servicio para usar el nuevo secreto
            if docker service update \
                --secret-rm "$secret_name" \
                --secret-add source="$new_secret_name",target="$secret_name" \
                "$service_name" > /dev/null; then

                # Eliminar secreto antiguo
                docker secret rm "$secret_name" > /dev/null 2>&1 || true

                log_message "INFO" "Secreto $secret_name rotado exitosamente"
                return 0
            fi
        fi

        retries=$((retries + 1))
        log_message "WARN" "Intento $retries fallido, reintentando en $RETRY_DELAY segundos..."
        sleep $RETRY_DELAY
    done

    log_message "ERROR" "No se pudo rotar el secreto $secret_name después de $MAX_RETRIES intentos"
    return 1
}

# Función para rotar un secreto en Vault
rotate_vault_secret() {
    local secret_path="$1"
    local new_value="$(openssl rand -base64 32)"
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf \
            -H "X-Vault-Token: $VAULT_TOKEN" \
            -X POST \
            -d "{\"data\":{\"value\":\"$new_value\"}}" \
            "${VAULT_ADDR}/v1/${secret_path}" > /dev/null; then

            log_message "INFO" "Secreto Vault $secret_path rotado exitosamente"
            return 0
        fi

        retries=$((retries + 1))
        log_message "WARN" "Intento $retries fallido, reintentando en $RETRY_DELAY segundos..."
        sleep $RETRY_DELAY
    done

    log_message "ERROR" "No se pudo rotar el secreto Vault $secret_path después de $MAX_RETRIES intentos"
    return 1
}

# Función principal de rotación
rotate_secrets() {
    local secrets_to_rotate=(
        "POSTGRES_PASSWORD"
        "API_KEY"
        "JWT_SECRET"
        "ENCRYPTION_KEY"
    )

    for secret in "${secrets_to_rotate[@]}"; do
        log_message "INFO" "Iniciando rotación de $secret"

        if [ -n "${VAULT_ADDR:-}" ]; then
            rotate_vault_secret "secret/data/$secret"
        else
            rotate_docker_secret "$secret" "attendance-backend"
        fi
    done
}

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Ejecutar rotación de secretos
rotate_secrets