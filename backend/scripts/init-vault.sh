#!/bin/bash
set -euo pipefail

# Configuración
VAULT_ADDR=${VAULT_ADDR:-"http://vault:8200"}
VAULT_TOKEN=${VAULT_TOKEN:-"attendance_root_token"}
LOG_FILE="/app/logs/vault-init.log"
MAX_RETRIES=5
RETRY_DELAY=5

# Función de logging
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$LOG_FILE"
}

# Función para esperar que Vault esté disponible
wait_for_vault() {
    local retries=0
    log_message "INFO" "Esperando que Vault esté disponible..."

    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -sf "${VAULT_ADDR}/v1/sys/health" > /dev/null; then
            log_message "INFO" "Vault está disponible"
            return 0
        fi
        retries=$((retries + 1))
        log_message "WARN" "Intento $retries: Vault no disponible, reintentando en $RETRY_DELAY segundos..."
        sleep $RETRY_DELAY
    done

    log_message "ERROR" "Vault no disponible después de $MAX_RETRIES intentos"
    return 1
}

# Función para inicializar Vault
init_vault() {
    log_message "INFO" "Inicializando configuración de Vault..."

    # Habilitar el motor de secretos KV versión 2
    curl -sf \
        -H "X-Vault-Token: ${VAULT_TOKEN}" \
        -X POST \
        -d '{"type": "kv", "options": {"version": "2"}}' \
        "${VAULT_ADDR}/v1/sys/mounts/secret" || {
            if [ $? -eq 22 ]; then
                log_message "INFO" "El motor de secretos KV ya está habilitado"
            else
                log_message "ERROR" "Error al habilitar el motor de secretos KV"
                return 1
            fi
        }

    # Crear política para la aplicación
    local policy_name="attendance-policy"
    local policy_rules='{
        "path": {
            "secret/data/*": {
                "capabilities": ["create", "read", "update", "delete", "list"]
            }
        }
    }'

    curl -sf \
        -H "X-Vault-Token: ${VAULT_TOKEN}" \
        -X PUT \
        -d "{\"policy\": ${policy_rules}}" \
        "${VAULT_ADDR}/v1/sys/policies/acl/${policy_name}"

    log_message "INFO" "Política ${policy_name} creada/actualizada"
}

# Función para cargar secretos desde .env
load_secrets_from_env() {
    local env_file=".env"
    if [ ! -f "$env_file" ]; then
        log_message "ERROR" "Archivo .env no encontrado"
        return 1
    fi

    log_message "INFO" "Cargando secretos desde .env..."

    # Leer el archivo .env y cargar secretos en Vault
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Ignorar líneas vacías o comentarios
        [[ -z "$key" || "$key" =~ ^# ]] && continue

        # Limpiar espacios y comillas
        key=$(echo "$key" | tr -d '"' | tr -d "'" | xargs)
        value=$(echo "$value" | tr -d '"' | tr -d "'" | xargs)

        # Crear o actualizar secreto en Vault
        curl -sf \
            -H "X-Vault-Token: ${VAULT_TOKEN}" \
            -X POST \
            -d "{\"data\": {\"value\": \"${value}\"}}" \
            "${VAULT_ADDR}/v1/secret/data/${key}"

        if [ $? -eq 0 ]; then
            log_message "INFO" "Secreto ${key} guardado exitosamente"
        else
            log_message "ERROR" "Error al guardar secreto ${key}"
        fi
    done < "$env_file"
}

# Función principal
main() {
    # Crear directorio de logs si no existe
    mkdir -p "$(dirname "$LOG_FILE")"

    log_message "INFO" "Iniciando configuración de Vault..."

    # Esperar que Vault esté disponible
    wait_for_vault || exit 1

    # Inicializar Vault
    init_vault || exit 1

    # Cargar secretos
    load_secrets_from_env || exit 1

    log_message "INFO" "Configuración de Vault completada exitosamente"
}

# Manejo de errores
trap 'log_message "ERROR" "Script interrumpido por error"' ERR

# Ejecutar script principal
main