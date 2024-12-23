#!/bin/bash

# Variables de entorno
VAULT_ADDR="http://127.0.0.1:8200"
VAULT_INIT_DIR="/tmp/vault"
VAULT_CONFIG="/etc/vault.d/vault.hcl"
CONSUL_ADDR="http://127.0.0.1:8500"

echo "Iniciando network vault-consul-network..."
docker network create vault-consul-network

# Inicia Consul en Docker (si no está corriendo)
echo "Iniciando Consul en Docker..."
docker run -d --name=consul --network vault-consul-network -e CONSUL_BIND_INTERFACE=eth0 -p 8500:8500 hashicorp/consul:1.20

# Ejecuta Vault con configuración para usar Consul como backend
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
echo "Esperando a que Vault esté disponible..."
until curl --silent --fail $VAULT_ADDR/v1/sys/health; do
  sleep 1
done

# Inicializa Vault
echo "Inicializando Vault..."
vault operator init -address=$VAULT_ADDR > $VAULT_INIT_DIR/init.txt

# Guarda las claves de desbloqueo y el token raíz
echo "Guardando las claves de desbloqueo y el token raíz..."
cat $VAULT_INIT_DIR/init.txt | grep 'Unseal Key' > $VAULT_INIT_DIR/keys.txt
cat $VAULT_INIT_DIR/init.txt | grep 'Initial Root Token' > $VAULT_INIT_DIR/root_token.txt

echo "Vault inicializado con Consul como backend. Las claves de desbloqueo y el token raíz se encuentran en:"
echo "  - $VAULT_INIT_DIR/keys.txt"
echo "  - $VAULT_INIT_DIR/root_token.txt"
