#!/bin/sh
set -e

# Configuración
VAULT_ADDR=${VAULT_ADDR:-"http://127.0.0.1:8200"}
CONSUL_ADDR=${CONSUL_ADDR:-"http://127.0.0.1:8500"}
KEYS_FILE="/vault/file/vault-keys.txt"
MAX_RETRIES=30
RETRY_DELAY=5
LOG_FILE="/vault/file/vault-init.log"

# Función de logging
log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message" | tee -a "$LOG_FILE"
}

# Función para verificar si Consul está inicializado
is_consul_initialized() {
    if wget -q -O- "${CONSUL_ADDR}/v1/status/leader" | grep -q '"Address":'; then
        return 0
    fi
    return 1
}

# Función para verificar si Vault está inicializado
is_vault_initialized() {
    if wget -q -O- "${VAULT_ADDR}/v1/sys/health" | grep -q '"initialized":true'; then
        return 0
    fi
    return 1
}

# Función para verificar si Vault está unsealed
is_vault_unsealed() {
    vault status 2>/dev/null | grep -q 'Sealed.*false'
}

# Esperar a que Consul esté disponible
wait_for_consul() {
    local retries=0
    log_message "INFO" "Esperando a que Consul esté disponible..."
    while ! is_consul_initialized; do
        if [ $retries -ge $MAX_RETRIES ]; then
            log_message "ERROR" "Timeout esperando a que Consul esté disponible"
            exit 1
        fi
        retries=$((retries + 1))
        log_message "WARN" "Intento $retries de $MAX_RETRIES. Reintentando en $RETRY_DELAY segundos..."
        sleep $RETRY_DELAY
    done
    log_message "INFO" "Consul está disponible"
}

# Esperar a que Vault esté disponible
wait_for_vault() {
    local retries=0
    log_message "INFO" "Esperando a que Vault esté disponible..."
    while ! wget -q --spider "${VAULT_ADDR}/v1/sys/health"; do
        if [ $retries -ge $MAX_RETRIES ]; then
            log_message "ERROR" "Timeout esperando a que Vault esté disponible"
            exit 1
        fi
        retries=$((retries + 1))
        log_message "WARN" "Intento $retries de $MAX_RETRIES. Reintentando en $RETRY_DELAY segundos..."
        sleep $RETRY_DELAY
    done
    log_message "INFO" "Vault está disponible"
}

# Inicializar Vault
initialize_vault() {
    log_message "INFO" "Inicializando Vault..."
    if is_vault_initialized; then
        log_message "INFO" "Vault ya está inicializado"
        return 0
    fi
    if ! vault operator init > "$KEYS_FILE"; then
        log_message "ERROR" "Error al inicializar Vault"
        exit 1
    fi
    chmod 600 "$KEYS_FILE"
    log_message "INFO" "Vault inicializado, claves guardadas en $KEYS_FILE"
}

# Extraer Unseal Key y Root Token del log del contenedor de Vault
extract_vault_keys() {
    log_message "INFO" "Extrayendo Unseal Key y Root Token del log del contenedor de Vault..."
    UNSEAL_KEY=$(docker logs vault 2>&1 | grep 'Unseal Key' | head -n 1 | sed 's/.*Unseal Key: //')
    ROOT_TOKEN=$(docker logs vault 2>&1 | grep 'Root Token' | head -n 1 | sed 's/.*Root Token: //')

    if [ -z "$UNSEAL_KEY" ] || [ -z "$ROOT_TOKEN" ]; then
        log_message "ERROR" "No se pudo extraer la Unseal Key o el Root Token del log del contenedor de Vault"
        exit 1
    fi

    echo "Unseal Key: $UNSEAL_KEY" > /vault/file/unseal_key.txt
    echo "Root Token: $ROOT_TOKEN" > /vault/file/root_token.txt
    log_message "INFO" "Unseal Key y Root Token guardados en /vault/file/"
}

# Realizar unseal de Vault
unseal_vault() {
    log_message "INFO" "Realizando unseal de Vault..."
    if is_vault_unsealed; then
        log_message "INFO" "Vault ya está unsealed"
        return 0
    fi
    if [[ ! -f "$KEYS_FILE" ]]; then
        log_message "ERROR" "No se encuentra el archivo de claves para unseal"
        exit 1
    fi
    local keys
    keys=$(grep "Unseal Key" "$KEYS_FILE" | awk '{print $4}' | head -n 3)
    for key in $keys; do
        if ! vault operator unseal "$key"; then
            log_message "ERROR" "Error al aplicar clave de unseal"
            exit 1
        fi
        sleep 1
    done
    log_message "INFO" "Vault ha sido unsealed"
}

# Verificar estado final
verify_vault_status() {
    local retries=0
    while ! vault status >/dev/null 2>&1; do
        if [ $retries -ge $MAX_RETRIES ]; then
            log_message "ERROR" "Timeout esperando a que Vault esté operativo"
            exit 1
        fi
        retries=$((retries + 1))
        log_message "WARN" "Vault no está completamente operativo. Reintentando ($retries/$MAX_RETRIES)..."
        sleep $RETRY_DELAY
    done
    log_message "INFO" "Vault está completamente operativo"
}

# Función principal
main() {
    log_message "INFO" "Iniciando proceso de inicialización de Vault..."
    wait_for_consul
    wait_for_vault
    initialize_vault
    extract_vault_keys
    unseal_vault
    verify_vault_status
    log_message "INFO" "Vault está completamente inicializado y operativo"
}

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Ejecutar función principal
main
