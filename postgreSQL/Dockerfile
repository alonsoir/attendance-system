FROM postgres:15

RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl https://install.citusdata.com/community/deb.sh | bash && \
    apt-get install -y postgresql-contrib postgresql-15-cron openssl postgresql-15-citus-11.2 && \
    rm -rf /var/lib/apt/lists/*

# Crear directorio para configuraciones y certificados
RUN mkdir -p /etc/postgresql/ssl && \
    chown -R postgres:postgres /etc/postgresql/ssl

# Generar certificados SSL autofirmados
RUN cd /etc/postgresql/ssl && \
    openssl req -new -x509 \
        -days 365 \
        -nodes \
        -text \
        -out server.crt \
        -keyout server.key \
        -subj "/CN=postgres" \
        -addext "subjectAltName = DNS:localhost,IP:127.0.0.1,DNS:*.local" && \
    chmod 600 server.key && \
    chown postgres:postgres server.key server.crt

# Copiar configuraciones a ubicación temporal
COPY pg_hba.conf /etc/postgresql/
COPY postgresql.conf /etc/postgresql/

# Crear script para copiar configuraciones
RUN echo '#!/bin/bash\n\
cp /etc/postgresql/pg_hba.conf $PGDATA/\n\
cp /etc/postgresql/postgresql.conf $PGDATA/\n\
chmod 600 $PGDATA/pg_hba.conf\n\
chmod 600 $PGDATA/postgresql.conf\n\
chown postgres:postgres $PGDATA/pg_hba.conf\n\
chown postgres:postgres $PGDATA/postgresql.conf' > /docker-entrypoint-initdb.d/00_config_files.sh && \
chmod +x /docker-entrypoint-initdb.d/00_config_files.sh

# Copiar scripts SQL en orden específico
COPY 00_init_db_encryption_capabilites.sql /docker-entrypoint-initdb.d/00_init_db_encryption_capabilites.sql
COPY 01_extensions_and_types.sql /docker-entrypoint-initdb.d/01_extensions_and_types.sql
COPY 02_base_tables.sql /docker-entrypoint-initdb.d/02_base_tables.sql
COPY 03_partitioning.sql /docker-entrypoint-initdb.d/03_partitioning.sql
COPY 04_procedures.sql /docker-entrypoint-initdb.d/04_procedures.sql
COPY 05_query_functions.sql /docker-entrypoint-initdb.d/05_query_functions.sql
COPY 06_maintenance_procedures.sql /docker-entrypoint-initdb.d/06_maintenance_procedures.sql
COPY 07_security_procedures.sql /docker-entrypoint-initdb.d/07_security_procedures.sql
COPY 08_views_and_reports.sql /docker-entrypoint-initdb.d/08_views_and_reports.sql
COPY 09_cleanup_and_optimization.sql /docker-entrypoint-initdb.d/09_cleanup_and_optimization.sql
COPY 11_citus_distribution.sql /docker-entrypoint-initdb.d/11_citus_distribution.sql
COPY 12_init_test_data.sql /docker-entrypoint-initdb.d/12_init_test_data.sql
COPY 13_citus_verification.sql /docker-entrypoint-initdb.d/13_citus_verification.sql

EXPOSE 5432

# Eliminar la referencia explícita al config_file ya que ahora estará en la ubicación por defecto
CMD ["postgres"]