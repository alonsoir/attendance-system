#!/bin/bash
set -e

echo "=== Iniciando entrypoint.sh ==="
echo "- Verificando ambiente..."
echo "  POSTGRES_USER: $POSTGRES_USER"
echo "  POSTGRES_DB: $POSTGRES_DB"
echo "  PGDATA: $PGDATA"

# Verificar archivos de configuración
echo "- Verificando archivos de configuración..."
if [ -f "/etc/postgresql/postgresql.conf" ]; then
    echo "  postgresql.conf encontrado"
else
    echo "  ERROR: postgresql.conf no encontrado"
fi

# Leer el secreto de Docker Swarm
echo "- Verificando secreto de encriptación..."
if [ -f "/run/secrets/encrypt_key" ]; then
    echo "  Secreto encrypt_key encontrado"
    export POSTGRES_ENCRYPT_KEY=$(cat /run/secrets/encrypt_key)
    echo "  POSTGRES_ENCRYPT_KEY configurada"

    echo "- Creando script de inicialización para la clave de encriptación..."
    # Notar que ahora es 99-set-encrypt-key.sql para que se ejecute último
    cat > /docker-entrypoint-initdb.d/99-set-encrypt-key.sql << EOF
    DO \$\$
    BEGIN
        RAISE NOTICE 'Configurando clave de encriptación...';
        PERFORM set_encryption_key('$POSTGRES_ENCRYPT_KEY');
        RAISE NOTICE 'Clave de encriptación configurada exitosamente';
    END;
    \$\$;
EOF
    echo "  Script de inicialización creado en /docker-entrypoint-initdb.d/99-set-encrypt-key.sql"
else
    echo "  ERROR: Secreto encrypt_key no encontrado en /run/secrets/encrypt_key"
fi

echo "- Verificando scripts de inicialización..."
ls -la /docker-entrypoint-initdb.d/
echo "  Total de scripts: $(ls /docker-entrypoint-initdb.d/ | wc -l)"

echo "=== Ejecutando entrypoint original de postgres ==="
echo "- Comando a ejecutar: docker-entrypoint.sh $@"

# Ejecutar el entrypoint original de postgres
exec docker-entrypoint.sh "$@"