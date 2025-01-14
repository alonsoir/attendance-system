
docker service ls

docker service logs <container_id>

docker service rmi <container_id>

docker service rm <container_id>

docker logs <container_id>

# password: test_password
psql -h localhost -U test_user -d test_db

# listar todos los procedimientos almacenados
SELECT n.nspname as "Schema", p.proname as "Name", pg_get_function_arguments(p.oid) as "Arguments" FROM pg_catalog.pg_proc p LEFT JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace WHERE n.nspname NOT IN ('pg_catalog', 'information_schema') ORDER BY 1, 2;
# listar todas las funciones.
\df

# listar todas las tablas
\dt+

# listas las tablas y sus relaciones
SELECT
    tc.table_schema,
    tc.table_name,
    kcu.column_name,
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema = 'public';

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\c test_db

\du test_user

\du test_user, ALTER USER test_user WITH SUPERUSER;

SELECT * FROM schools;

SELECT * FROM tutors;

SELECT * FROM students;

# \dt