#!/bin/bash
set -e

# Configuración
VAULT_ADDR=${VAULT_ADDR:-"http://127.0.0.1:8200"}
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

# Función para verificar el estado de Vault
check_vault_status() {
    if ! wget -q --spider "${VAULT_ADDR}/v1/sys/health"; then
        log_message "ERROR" "No se puede contactar con Vault"
        return 1
    fi

    # Usar el CLI de vault para verificar el estado
    if vault status > /dev/null 2>&1; then
        log_message "INFO" "Vault está operativo"
        return 0
    else
        log_message "WARN" "Vault no está completamente operativo"
        return 1
    fi
}

# Función para esperar a que Vault esté disponible
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

# Función para inicializar Vault
initialize_vault() {
    log_message "INFO" "Inicializando Vault..."

    # Verificar si Vault ya está inicializado usando el CLI
    if vault status 2>/dev/null | grep -q 'Initialized.*true'; then
        log_message "WARN" "Vault ya está inicializado"
        return 0
    fi

    # Inicializar Vault y guardar output
    if ! vault operator init > "$KEYS_FILE"; then
        log_message "ERROR" "Error al inicializar Vault"
        exit 1
    fi

    chmod 600 "$KEYS_FILE"
    log_message "INFO" "Vault inicializado, claves guardadas en $KEYS_FILE"
}

# Función para unseal Vault
unseal_vault() {
    log_message "INFO" "Realizando unseal de Vault..."

    # Verificar si ya está unsealed
    if vault status 2>/dev/null | grep -q 'Sealed.*false'; then
        log_message "INFO" "Vault ya está unsealed"
        return 0
    fi

    # Verificar archivo de claves
    if [[ ! -f "$KEYS_FILE" ]]; then
        log_message "ERROR" "No se encuentra el archivo de claves"
        exit 1
    fi

    # Usar las primeras 3 claves para unseal
    log_message "INFO" "Aplicando claves de unseal..."

    grep "Unseal Key" "$KEYS_FILE" | head -n 3 | while read -r line; do
        key=$(echo "$line" | awk '{print $4}')
        if ! vault operator unseal "$key"; then
            log_message "ERROR" "Error al aplicar clave de unseal"
            exit 1
        fi
        sleep 1
    done
}

# Función principal
main() {
    log_message "INFO" "Iniciando proceso de inicialización de Vault..."

    # Esperar a que Vault esté disponible
    wait_for_vault

    # Inicializar Vault si es necesario
    initialize_vault

    # Hacer unseal de Vault
    unseal_vault

    # Verificar estado final
    local retries=0
    while ! check_vault_status; do
        if [ $retries -ge $MAX_RETRIES ]; then
            log_message "ERROR" "Timeout esperando a que Vault esté operativo"
            exit 1
        fi
        retries=$((retries + 1))
        log_message "WARN" "Esperando a que Vault esté completamente operativo... Intento $retries de $MAX_RETRIES"
        sleep $RETRY_DELAY
    done

    log_message "INFO" "Vault está completamente inicializado y operativo"
    log_message "WARN" "¡IMPORTANTE! Las claves de unseal y el token root están en $KEYS_FILE"

    # Mostrar el token root
    ROOT_TOKEN=$(grep "Initial Root Token" "$KEYS_FILE" | awk '{print $4}')
    log_message "INFO" "Root Token: $ROOT_TOKEN"
}

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"

# Ejecutar función principal
main