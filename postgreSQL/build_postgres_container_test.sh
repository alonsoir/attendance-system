# Detener el contenedor si está corriendo
docker stop test-postgres
docker rm test-postgres

# Construir la imagen de nuevo con los cambios en el Dockerfile
docker build -t test-postgres -f dockerfile_postgres_test_containers .

# Ejecutar el contenedor manualmente para probar
docker run --name test-postgres \
  -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_password \
  -e POSTGRES_DB=test_db \
  -p 5432:5432 \
  -d test-postgres

# Ver si hay contenedores corriendo
docker ps

# Ver si el puerto 5432 está en uso
lsof -i :5432

# Verificar los logs
docker logs test-postgres

# Intentar conectarse con psql
psql -h localhost -p 5432 -U test_user -d test_db