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

wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    echo "Esperando a que $service ($host:$port) esté disponible..."
    while ! nc -z "$host" "$port"; do
        sleep 1
    done
    echo "$service está disponible"
}

# Verificar y obtener secretos de Vault
fetch_vault_secrets() {
    log_message "INFO" "Obteniendo secretos para el frontend de Vault..."

    if [ -z "${VAULT_ADDR:-}" ] || [ -z "${VAULT_TOKEN:-}" ]; then
        log_message "ERROR" "Variables de Vault no configuradas"
        return 1
    fi
    # Verificar que Vault está accesible
    vault_health_url="$VAULT_ADDR/v1/sys/health"
    log_message "INFO" "Verificando ruta de estado de Vault: $vault_health_url"
    if ! curl -sf -o /dev/null "$vault_health_url"; then
        log_message "ERROR" "No se puede conectar a Vault"
        return 1
    fi
    # Obtener secretos de Vault
    /app/scripts/fetch-vault-secrets.sh || return 1

    log_message "INFO" "Secretos obtenidos exitosamente"
    return 0
}

# Función principal
main() {
    log_message "INFO" "Iniciando servicio frontend..."
    # Esperar por el backend
    wait_for_service "back" "8000" "Backend API"
    wait_for_service "vault" "8200" "Vault"

    # Obtener secretos de Vault
    if ! fetch_vault_secrets; then
        log_message "ERROR" "Error al obtener secretos"
    fi

    # Iniciar nginx
    log_message "INFO" "Iniciando nginx..."
    exec nginx -g "daemon off;"
}

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Ejecutar función principal
main