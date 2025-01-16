#!/bin/bash
echo "Current working directory: $(pwd)"
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "PATH: $PATH"
echo "Executing script..."

# Variables de entorno
VAULT_ADDR="http://vault:8200"
CONSUL_ADDR="http://consul:8500"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "Directorio del script: $SCRIPT_DIR"
VAULT_INIT_DIR="${SCRIPT_DIR}/vault"
echo "Directorio de inicialización de Vault: $VAULT_INIT_DIR"

# Crea el directorio de trabajo si no existe
mkdir -p "$VAULT_INIT_DIR"

# Espera a que Consul esté disponible
echo "Esperando a que Consul esté disponible..."
for i in {1..30}; do
  if wget -q --spider "$CONSUL_ADDR/v1/status/leader"; then
    echo "Consul está disponible."
    break
  fi
  echo "Intento $i: Consul no está disponible. Esperando..."
  sleep 2
done

# Espera a que Vault esté disponible
echo "Esperando a que Vault esté disponible..."
until wget -q --spider "$VAULT_ADDR/v1/sys/health"; do
  sleep 1
done

# Verifica si Vault ya está inicializado
echo "Verificando si Vault ya está inicializado..."
if wget -q -O- "$VAULT_ADDR/v1/sys/init" | grep -q '"initialized":true'; then
  echo "Vault ya está inicializado."
else
  # Inicializa Vault
  echo "Inicializando Vault..."
  vault operator init -key-shares=1 -key-threshold=1 > "$VAULT_INIT_DIR/keys.txt"
  if [ $? -ne 0 ]; then
    echo "Error al inicializar Vault."
    exit 1
  fi
  chmod 600 "$VAULT_INIT_DIR/keys.txt"
fi

# Extrae la Unseal Key y el Root Token de los keys.txt
echo "Extrayendo la Unseal Key y el Root Token..."
UNSEAL_KEY=$(grep 'Unseal Key 1' "$VAULT_INIT_DIR/keys.txt" | sed 's/.*Unseal Key 1: //')
ROOT_TOKEN=$(grep 'Root Token' "$VAULT_INIT_DIR/keys.txt" | sed 's/.*Root Token: //')

# Verifica si la Unseal Key y el Root Token se extrajeron correctamente
if [ -z "$UNSEAL_KEY" ] || [ -z "$ROOT_TOKEN" ]; then
  echo "Error: No se pudo extraer la Unseal Key o el Root Token de los keys.txt."
  exit 1
fi

echo "Clave de desbloqueo: $UNSEAL_KEY"
echo "Root Token: $ROOT_TOKEN"

# Guarda las claves en archivos separados
echo "Guardando las claves en archivos..."
echo "Unseal Key: $UNSEAL_KEY" > "$VAULT_INIT_DIR/unseal_key.txt"
echo "Root Token: $ROOT_TOKEN" > "$VAULT_INIT_DIR/root_token.txt"

echo "Claves guardadas en:"
echo "  - $VAULT_INIT_DIR/unseal_key.txt"
echo "  - $VAULT_INIT_DIR/root_token.txt"

# Verifica si Vault ya está desbloqueado
echo "Verificando si Vault ya está desbloqueado..."
if ! wget -q -O- "$VAULT_ADDR/v1/sys/seal-status" | grep -q '"sealed":true'; then
  echo "Vault ya está desbloqueado."
else
  # Desbloquea Vault (unseal)
  echo "Desbloqueando Vault (unseal)..."
  vault operator unseal "$UNSEAL_KEY"
  if [ $? -ne 0 ]; then
    echo "Error al desbloquear Vault."
    exit 1
  fi
fi

echo "Vault ha sido desbloqueado."