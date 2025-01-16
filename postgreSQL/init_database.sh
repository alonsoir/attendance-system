#!/bin/bash

# Esperar a que PostgreSQL esté listo
until pg_isready -h localhost -U postgres; do
  echo "Esperando a que PostgreSQL esté listo..."
  sleep 2
done

# Ejecutar los scripts SQL
# Inicializa capaciadad cifrado de campos.
psql -U postgres -d test_db -f /docker-entrypoint-initdb.d/init-db.sql
# Iniciala el esquema y procedimientos almacenados.
psql -U postgres -d test_db -f /docker-entrypoint-initdb.d/init_database_schema.sql
# Inicializa los datos de prueba.
psql -U postgres -d test_db -f /docker-entrypoint-initdb.d/init_database_data.sql
