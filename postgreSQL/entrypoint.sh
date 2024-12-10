#!/bin/bash

# Script de inicialización personalizado para PostgreSQL

# Leer el secreto de Docker Swarm
ENCRYPT_KEY=$(cat /run/secrets/encrypt_key)

# Configurar PostgreSQL para usar la clave de cifrado
# Escapar caracteres especiales en la clave de cifrado
escaped_encrypt_key=$(printf '%s\n' "$ENCRYPT_KEY" | sed -e 's/[]\/$*.^[]/\\&/g')
sed -i "s/^#encrypt_key = .*$/encrypt_key = '$escaped_encrypt_key'/" /etc/postgresql/postgresql.conf

# Ajustar permisos del directorio de datos
chown -R postgres:postgres /var/lib/postgresql/data
chmod 700 /var/lib/postgresql/data

# Inicializar el directorio de datos si no está inicializado
if [ ! -f /var/lib/postgresql/data/PG_VERSION ]; then
  echo "Inicializando el directorio de datos de PostgreSQL..."
  gosu postgres initdb -D /var/lib/postgresql/data
fi

# Cambiar al usuario postgres
exec gosu postgres "$@"
