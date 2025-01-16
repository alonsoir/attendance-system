#!/bin/bash
set -euo pipefail

# Configuración
ENV_FILE=".env"
SECURE_ENV_FILE=".env.encrypted"
LOG_FILE="/app/logs/secure-env.log"
CIPHER="aes-256-gcm"

# Lista completa de variables requeridas
REQUIRED_VARS=(
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

# Función de logging
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$LOG_FILE"
}

# Validar variables de entorno
validate_env() {
    local missing_vars=()

    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_message "ERROR" "Faltan variables requeridas: ${missing_vars[*]}"
        return 1
    fi

    log_message "INFO" "Todas las variables requeridas están presentes"
}

# Función para encriptar variables de entorno
encrypt_env() {
    local env_key="$1"

    if [ ! -f "$ENV_FILE" ]; then
        log_message "ERROR" "Archivo $ENV_FILE no encontrado"
        return 1
    fi

    # Generar IV aleatorio
    iv=$(openssl rand -hex 12)

    # Encriptar el archivo
    encrypted_data=$(openssl enc -$CIPHER -k "$env_key" -iv "$iv" \
        -in "$ENV_FILE" 2>/dev/null | base64 -w 0)

    # Guardar IV y datos encriptados
    echo "${iv}:${encrypted_data}" > "$SECURE_ENV_FILE"
    log_message "INFO" "Variables de entorno encriptadas exitosamente"
}

# Función para desencriptar variables de entorno
decrypt_env() {
    local env_key="$1"

    if [ ! -f "$SECURE_ENV_FILE" ]; then
        log_message "ERROR" "Archivo $SECURE_ENV_FILE no encontrado"
        return 1
    fi

    # Leer IV y datos encriptados
    IFS=':' read -r iv encrypted_data < "$SECURE_ENV_FILE"

    # Desencriptar y cargar variables
    echo "$encrypted_data" | base64 -d | \
        openssl enc -$CIPHER -d -k "$env_key" -iv "$iv" 2>/dev/null > "$ENV_FILE"

    log_message "INFO" "Variables de entorno desencriptadas exitosamente"
}

# Función para validar variables de entorno
validate_env() {
    local required_vars=("POSTGRES_SERVER" "POSTGRES_PORT" "REDIS_HOST" "REDIS_PORT")
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_message "ERROR" "Faltan variables requeridas: ${missing_vars[*]}"
        return 1
    fi

    log_message "INFO" "Todas las variables requeridas están presentes"
}

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"