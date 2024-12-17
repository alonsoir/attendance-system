#!/bin/bash
set -euo pipefail

# Configuración
LOG_FILE="/var/log/nginx/entrypoint.log"
MAX_RETRIES=5
RETRY_DELAY=2

# Función de logging
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

# Función de limpieza
cleanup() {
    local exit_code=$?
    log_message "INFO" "Deteniendo el servicio frontend (código de salida: $exit_code)"
    exit $exit_code
}

# Configurar trap para limpieza
trap cleanup EXIT
trap 'trap - EXIT; cleanup' INT TERM

# Verificar y obtener secretos de Vault
fetch_vault_secrets() {
    log_message "INFO" "Obteniendo secretos de Vault..."

    if [ -z "${VAULT_ADDR:-}" ] || [ -z "${VAULT_TOKEN:-}" ]; then
        log_message "ERROR" "Variables de Vault no configuradas"
        return 1
    }

    /app/scripts/fetch-vault-secrets.sh || return 1

    log_message "INFO" "Secretos obtenidos exitosamente"
    return 0
}

# Función principal
main() {
    log_message "INFO" "Iniciando servicio frontend..."

    # Obtener secretos de Vault
    if ! fetch_vault_secrets; then
        log_message "ERROR" "Error al obtener secretos"
        exit 1
    }

    # Iniciar nginx
    log_message "INFO" "Iniciando nginx..."
    exec nginx -g "daemon off;"
}

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Ejecutar función principal
main