#!/bin/bash
set -euo pipefail

# Configuración
MAX_RETRIES=30
RETRY_DELAY=2
LOG_FILE="/tmp/entrypoint.log"

# Función de logging
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

# Función para limpiar al salir
cleanup() {
    local exit_code=$?
    log_message "INFO" "Deteniendo el servicio (código de salida: $exit_code)"
    # Aquí puedes añadir cualquier limpieza necesaria
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

# Función para verificar y obtener secretos de Vault
fetch_vault_secrets() {
    log_message "INFO" "Obteniendo secretos para el backend de Vault..."

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

    # Cargar secretos usando el script dedicado
    if ! /app/scripts/fetch-secrets.sh; then
        log_message "ERROR" "Error al obtener secretos de Vault"
        return 1
    fi

    log_message "INFO" "Secretos obtenidos exitosamente"
    return 0
}

# Función para verificar la configuración necesaria
verify_config() {
    local required_vars=(
        "PROJECT_NAME"
        "PROJECT_DESCRIPTION"
        "VERSION"
        "API_V1_STR"
        "BACKEND_CORS_ORIGINS"
        "ENABLE_METRICS"
        "PROMETHEUS_PORT"
        "GRAFANA_PORT"
        "GRAFANA_ADMIN_PASSWORD"
        "BACKEND_PORT"
        "ENABLE_WHATSAPP_CALLBACK"
        "MOCK_EXTERNAL_SERVICES"
        "POSTGRES_SERVER"
        "POSTGRES_USER"
        "POSTGRES_PASSWORD"
        "POSTGRES_DB"
        "POSTGRES_PORT"
        "REDIS_HOST"
        "REDIS_PORT"
        "REDIS_URL"
        "SECRET_KEY"
        "ANTHROPIC_API_KEY"
        "WHATSAPP_CALLBACK_TOKEN"
        "WHATSAPP_META_API_KEY"
        "WHATSAPP_PROVIDER"
        "FRONTEND_PORT"
        "VITE_API_URL"
    )

    log_message "INFO" "Verificando variables de entorno requeridas..."
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_message "ERROR" "Variables requeridas no configuradas: ${missing_vars[*]}"
        return 1
    fi

    log_message "INFO" "Todas las variables requeridas están configuradas correctamente"
    return 0
}

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Función principal
main() {
    log_message "INFO" "Iniciando servicio backend..."

    # Verificar configuración
    if ! verify_config; then
        log_message "ERROR" "Falló la verificación de configuración"
        exit 1
    fi

    # Esperar por los servicios
    wait_for_service "$POSTGRES_SERVER" "$POSTGRES_PORT" "PostgreSQL"
    wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"
    wait_for_service "vault" "8200" "Vault"

    # Obtener secretos de Vault
    if ! fetch_vault_secrets; then
        log_message "ERROR" "Error al obtener secretos"
        # exit 1
    fi

    # Esperar servicios dependientes
    if ! wait_for_service "$POSTGRES_SERVER" "$POSTGRES_PORT" "PostgreSQL"; then
        log_message "ERROR" "Error esperando PostgreSQL"
        exit 1
    fi

    if ! wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis"; then
        log_message "ERROR" "Error esperando Redis"
        exit 1
    fi

    # Iniciar el backend
    log_message "INFO" "Iniciando servicio uvicorn..."
    exec uvicorn backend.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --log-level info \
        --proxy-headers \
        --forwarded-allow-ips='*'
}

# Ejecutar función principal
main