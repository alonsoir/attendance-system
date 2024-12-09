# Detener el contenedor si está corriendo
docker stop test-postgres-encrypted
docker rm test-postgres-encrypted

# Generar una clave de cifrado segura
ENCRYPT_KEY=$(openssl rand -base64 32)

echo "La clave de cifrado generada es: $ENCRYPT_KEY"
echo "Asegúrate de guardar esta clave en un lugar seguro."

# Construir la imagen de nuevo con los cambios en el Dockerfile
docker build -t test-postgres-encrypted -f dockerfile_postgres_test_containers . \
  --build-arg ENCRYPT_KEY="$ENCRYPT_KEY"

# Ejecutar el contenedor manualmente para probar
docker run --name test-postgres-encrypted \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_password \
  -e POSTGRES_DB=test_db \
  -e ENCRYPT_KEY="$ENCRYPT_KEY" \
  -p 5432:5432 \
  -d test-postgres-encrypted

# Ver si hay contenedores corriendo
docker ps

# Ver si el puerto 5432 está en uso
lsof -i :5432

# Verificar los logs
docker logs test-postgres-encrypted

# Esperar a que PostgreSQL esté listo
echo "Esperando 5 segundos a que PostgreSQL esté completamente iniciado..."
sleep 5

# Intentar conectarse con psql usando la variable de entorno PGPASSWORD
PGPASSWORD=test_password psql -h localhost -p 5432 -U test_user -d test_db