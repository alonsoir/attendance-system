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


# Inicia Vault con Consul como backend y configuración personalizada
echo "Iniciando Vault con Consul como backend..."
docker run --rm -d \
  --name=vault \
  --network vault-consul-network \
  -e 'VAULT_DEV_ROOT_TOKEN_ID=myroot' \
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

# Inicializa Vault
echo "Inicializando Vault. {$VAULT_ADDR} {$VAULT_INIT_DIR/init.txt}"
docker exec -i vault vault operator init -address=$VAULT_ADDR > $VAULT_INIT_DIR/init.txt

# Guarda las claves de desbloqueo y el token raíz
echo "Guardando las claves de desbloqueo y el token raíz..."
cat $VAULT_INIT_DIR/init.txt | grep 'Unseal Key' > $VAULT_INIT_DIR/keys.txt
cat $VAULT_INIT_DIR/init.txt | grep 'Initial Root Token' > $VAULT_INIT_DIR/root_token.txt

echo "Vault inicializado con Consul como backend. Las claves de desbloqueo y el token raíz se encuentran en:"
echo "  - $VAULT_INIT_DIR/keys.txt"
echo "  - $VAULT_INIT_DIR/root_token.txt"

# Desbloquea Vault (unseal)
echo "Desbloqueando Vault (unseal)..."
UNSEAL_KEY=$(head -n 1 $VAULT_INIT_DIR/keys.txt | sed 's/Unseal Key 1: //')
echo "Clave de desbloqueo: $UNSEAL_KEY"
docker exec -it vault vault operator unseal -address=$VAULT_ADDR $UNSEAL_KEY

echo "Vault ha sido desbloqueado."
