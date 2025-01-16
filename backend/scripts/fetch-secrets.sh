#!/bin/bash
set -euo pipefail

# Configuración
MAX_RETRIES=5
RETRY_DELAY=5
LOG_FILE="/app/logs/secrets.log"

# Función de logging
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$LOG_FILE"
}

# Función para obtener secretos de Vault
fetch_from_vault() {
    local secret_path="$1"
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if [ -z "${VAULT_TOKEN:-}" ]; then
            log_message "ERROR" "VAULT_TOKEN no está configurado"
            return 1
        fi

        response=$(curl -sf \
            -H "X-Vault-Token: $VAULT_TOKEN" \
            -X GET \
            "${VAULT_ADDR}/v1/${secret_path}" 2>/dev/null)

        if [ $? -eq 0 ]; then
            echo "$response" | jq -r '.data.data'
            return 0
        fi

        retries=$((retries + 1))
        log_message "WARN" "Intento $retries fallido, reintentando en $RETRY_DELAY segundos..."
        sleep $RETRY_DELAY
    done

    log_message "ERROR" "No se pudo obtener el secreto después de $MAX_RETRIES intentos"
    return 1
}

# Función para obtener secretos de Docker
fetch_from_docker_secret() {
    local secret_name="$1"
    if [ -f "/run/secrets/$secret_name" ]; then
        cat "/run/secrets/$secret_name"
        return 0
    fi
    return 1
}

# Función principal para obtener secretos
get_secret() {
    local secret_name="$1"
    local secret_value=""

    # Intentar obtener de Vault primero
    if [ -n "${VAULT_ADDR:-}" ]; then
        log_message "INFO" "Intentando obtener $secret_name de Vault"
        secret_value=$(fetch_from_vault "secret/data/$secret_name" || echo "")
    fi

    # Si no está en Vault, intentar Docker secrets
    if [ -z "$secret_value" ]; then
        log_message "INFO" "Intentando obtener $secret_name de Docker secrets"
        secret_value=$(fetch_from_docker_secret "$secret_name" || echo "")
    fi

    # Verificar si se obtuvo el secreto
    if [ -n "$secret_value" ]; then
        echo "$secret_value"
        log_message "INFO" "Secreto $secret_name obtenido exitosamente"
        return 0
    fi

    log_message "ERROR" "No se pudo obtener el secreto $secret_name"
    return 1
}

# Función de limpieza
cleanup() {
    log_message "INFO" "Limpiando recursos..."
    # Añadir aquí la lógica de limpieza necesaria
}

trap cleanup EXIT

# Verificar que el directorio de logs existe
mkdir -p "$(dirname "$LOG_FILE")"