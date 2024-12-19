#!/bin/bash
set -euo pipefail

# Configuración
MAX_RETRIES=5
RETRY_DELAY=2
LOG_FILE="/var/log/nginx/vault-secrets.log"

# Función de logging
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

# Función para obtener secretos de Vault
fetch_secret() {
    local secret_path="$1"
    local key="$2"
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf \
            -H "X-Vault-Token: $VAULT_TOKEN" \
            "$VAULT_ADDR/v1/$secret_path" > /dev/null; then

            local value=$(curl -sf \
                -H "X-Vault-Token: $VAULT_TOKEN" \
                "$VAULT_ADDR/v1/$secret_path" | jq -r ".data.data.$key")

            if [ "$value" != "null" ]; then
                echo "$value"
                return 0
            fi
        fi

        retries=$((retries + 1))
        log_message "WARN" "Intento $retries fallido para $key, reintentando en $RETRY_DELAY segundos..."
        sleep $RETRY_DELAY
    done

    log_message "ERROR" "No se pudo obtener el secreto $key después de $MAX_RETRIES intentos"
    return 1
}

# Función principal
main() {
    log_message "INFO" "Iniciando obtención de secretos del frontend..."

    # Verificar variables de entorno requeridas
    if [ -z "${VAULT_ADDR:-}" ] || [ -z "${VAULT_TOKEN:-}" ]; then
        log_message "ERROR" "VAULT_ADDR o VAULT_TOKEN no están configurados"
        exit 1
    }

    # Lista de secretos necesarios para el frontend
    declare -A secrets=(
        ["VITE_API_URL"]="secret/data/frontend/api"
        ["FRONTEND_PORT"]="secret/data/frontend/config"
        ["WHATSAPP_CALLBACK_TOKEN"]="secret/data/frontend/whatsapp"
        ["WHATSAPP_META_API_KEY"]="secret/data/frontend/whatsapp"
    )

    # Crear archivo de entorno temporal
    local env_file="/usr/share/nginx/html/env-config.js"
    echo "window._env_ = {" > "$env_file"

    # Obtener cada secreto
    for key in "${!secrets[@]}"; do
        local path="${secrets[$key]}"
        local value

        if value=$(fetch_secret "$path" "$key"); then
            log_message "INFO" "Secreto $key obtenido exitosamente"
            # Escapar valores para JavaScript
            value=$(echo "$value" | sed 's/"/\\"/g')
            echo "  $key: \"$value\"," >> "$env_file"
        else
            log_message "ERROR" "Error obteniendo secreto $key"
            exit 1
        fi
    done

    echo "};" >> "$env_file"
    log_message "INFO" "Archivo de configuración generado exitosamente"

    # Verificar permisos
    chmod 444 "$env_file"
    log_message "INFO" "Permisos establecidos correctamente"
}

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Manejar errores
trap 'log_message "ERROR" "Script interrumpido por error"' ERR

# Ejecutar función principal
main

log_message "INFO" "Script completado exitosamente"