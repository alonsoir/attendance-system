#!/bin/bash

# Esperar a que PostgreSQL esté listo
until pg_isready -h localhost -U postgres; do
  echo "Esperando a que PostgreSQL esté listo..."
  sleep 2
done

# Ejecutar los scripts SQL
psql -U postgres -d test_db -f /docker-entrypoint-initdb.d/init_database_schema.sql
psql -U postgres -d test_db -f /docker-entrypoint-initdb.d/init_database_data.sql
