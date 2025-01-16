#!/bin/bash

# Variables de entorno
VAULT_ADDR="http://127.0.0.1:8200"
CONSUL_ADDR="http://127.0.0.1:8500"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # Directorio donde está el script
echo "Directorio del script: $SCRIPT_DIR"
VAULT_INIT_DIR="${SCRIPT_DIR}/vault"  # Ruta donde se guardarán las claves y tokens
echo "Directorio de inicialización de Vault: $VAULT_INIT_DIR"
# Crea el directorio de trabajo si no existe
mkdir -p $VAULT_INIT_DIR

docker volume rm consul_data || echo "El volumen consul_data no existe."
docker volume create consul_data || echo "El volumen consul_data ya existe."

docker network rm vault-consul-network || echo "La red vault-consul-network no existe."
# Inicia la red de Docker para Vault y Consul
echo "Iniciando network vault-consul-network..."
docker network create vault-consul-network || echo "La red vault-consul-network ya existe."

# Inicia Consul en Docker con la configuración personalizada
echo "Iniciando Consul en Docker..."
docker run -d --name=consul --network vault-consul-network -e CONSUL_BIND_INTERFACE=eth0 -p 8500:8500 hashicorp/consul:1.20

echo "Esperando a que Consul esté disponible..."
for i in {1..30}; do
  if curl --silent --fail $CONSUL_ADDR/v1/status/leader; then
    echo "Consul está disponible."
    break
  fi
  echo "Intento $i: Consul no está disponible. Esperando..."
  sleep 2
done

# Limpia los datos de Consul
echo "Limpiando datos de Consul..."
curl --request PUT --data '{"recurse": true}' $CONSUL_ADDR/v1/kv/vault?recurse=true

# Inicia Vault con Consul como backend y configuración personalizada
echo "Iniciando Vault con Consul como backend..."
docker run --rm -d \
  --name=vault \
  --network vault-consul-network \
  -e 'VAULT_ADDR=http://127.0.0.1:8200' \
  -e 'VAULT_API_ADDR=http://127.0.0.1:8200' \
  -e 'VAULT_LISTEN_ADDRESS=0.0.0.0:8200' \
  -e 'VAULT_BACKEND_CONSUL_ADDRESS=http://127.0.0.1:8500' \
  -p 8200:8200 \
  hashicorp/vault:1.18

# Espera a que Vault esté disponible
echo "Esperando a que Vault esté disponible doing {$VAULT_ADDR/v1/sys/health}"
until curl --silent --fail $VAULT_ADDR/v1/sys/health; do
  sleep 1
done

# Verifica si Vault ya está inicializado
echo "Verificando si Vault ya está inicializado..."
VAULT_INIT_STATUS=$(curl --silent --fail $VAULT_ADDR/v1/sys/init | jq -r .initialized)
if [ "$VAULT_INIT_STATUS" == "true" ]; then
  echo "Vault ya está inicializado."
else
  # Inicializa Vault
  echo "Inicializando Vault. address: {$VAULT_ADDR}..."
  docker exec -i vault vault operator init -address=$VAULT_ADDR
fi

# Extrae la Unseal Key y el Root Token del log del contenedor de Vault
echo "Extrayendo la Unseal Key y el Root Token del log del contenedor de Vault..."
UNSEAL_KEY=$(docker logs vault 2>&1 | grep 'Unseal Key' | head -n 1 | sed 's/.*Unseal Key: //')
ROOT_TOKEN=$(docker logs vault 2>&1 | grep 'Root Token' | head -n 1 | sed 's/.*Root Token: //')

# Verifica si la Unseal Key y el Root Token se extrajeron correctamente
if [ -z "$UNSEAL_KEY" ] || [ -z "$ROOT_TOKEN" ]; then
  echo "Error: No se pudo extraer la Unseal Key o el Root Token del log del contenedor de Vault."
  exit 1
fi

echo "Clave de desbloqueo: $UNSEAL_KEY"
echo "Root Token: $ROOT_TOKEN"

# Guarda las claves en archivos
echo "Guardando las claves en archivos..."
echo "Unseal Key: $UNSEAL_KEY" > $VAULT_INIT_DIR/unseal_key.txt
echo "Root Token: $ROOT_TOKEN" > $VAULT_INIT_DIR/root_token.txt

echo "Claves guardadas en:"
echo "  - $VAULT_INIT_DIR/unseal_key.txt"
echo "  - $VAULT_INIT_DIR/root_token.txt"

# Verifica si Vault ya está desbloqueado
echo "Verificando si Vault ya está desbloqueado..."
VAULT_SEALED_STATUS=$(curl --silent --fail $VAULT_ADDR/v1/sys/seal-status | jq -r .sealed)
if [ "$VAULT_SEALED_STATUS" == "false" ]; then
  echo "Vault ya está desbloqueado."
else
  # Desbloquea Vault (unseal)
  echo "Desbloqueando Vault (unseal)..."
  docker exec -it vault vault operator unseal -address=$VAULT_ADDR $UNSEAL_KEY
fi

echo "Vault ha sido desbloqueado."
