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

if [ -f "/etc/postgresql/pg_hba.conf" ]; then
    echo "  pg_hba.conf encontrado"
else
    echo "  ERROR: pg_hba.conf no encontrado"
fi

# Leer el secreto de Docker Swarm
echo "- Verificando secreto de encriptación..."
if [ -f "/run/secrets/encrypt_key" ]; then
    echo "  Secreto encrypt_key encontrado"
    export POSTGRES_ENCRYPT_KEY=$(cat /run/secrets/encrypt_key)
    echo "  POSTGRES_ENCRYPT_KEY configurada"

    echo "- Creando script de inicialización para la clave de encriptación..."
    cat > /docker-entrypoint-initdb.d/00-set-encrypt-key.sql << EOF
    -- Script generado por entrypoint.sh
    CREATE OR REPLACE FUNCTION pg_temp.bootstrap_encryption_key()
    RETURNS void AS \$\$
    BEGIN
        RAISE NOTICE 'Iniciando configuración de clave de encriptación...';

        -- Esperar hasta que la función set_encryption_key esté disponible
        RAISE NOTICE 'Esperando función set_encryption_key...';
        WHILE NOT EXISTS (
            SELECT 1
            FROM pg_proc
            WHERE proname = 'set_encryption_key'
        ) LOOP
            RAISE NOTICE 'Función set_encryption_key aún no disponible, esperando...';
            PERFORM pg_sleep(1);
        END LOOP;

        -- Configurar la clave
        RAISE NOTICE 'Configurando clave de encriptación...';
        PERFORM set_encryption_key('$POSTGRES_ENCRYPT_KEY');
        RAISE NOTICE 'Clave de encriptación configurada exitosamente';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'Error configurando clave de encriptación: %', SQLERRM;
        RAISE;
    END;
    \$\$ LANGUAGE plpgsql;

    DO \$\$
    BEGIN
        RAISE NOTICE 'Ejecutando bootstrap_encryption_key...';
        PERFORM pg_temp.bootstrap_encryption_key();
        RAISE NOTICE 'bootstrap_encryption_key ejecutado exitosamente';
    END;
    \$\$;
EOF
    echo "  Script de inicialización creado en /docker-entrypoint-initdb.d/00-set-encrypt-key.sql"
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