-- Este archivo asume que pgcrypto y uuid-ossp ya están instalados
-- y que las funciones encrypt_value/decrypt_value ya existen

-- Crear extensión pg_cron de manera simple
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS citus;
-- Crear tipos ENUM para el sistema
CREATE TYPE sender_type_enum AS ENUM ('CLAUDE', 'SCHOOL', 'TUTOR');
CREATE TYPE notification_level AS ENUM (
    'INFO',
    'WARNING',
    'ERROR'
);

CREATE TYPE notification_category AS ENUM (
    'INFO',
    'DATA_INTEGRITY',
    'PERFORMANCE',
    'MAINTENANCE',
    'SYSTEM'
);

-- Configuración inicial de pg_cron
SELECT cron.schedule('maintain-messages-partitions', '0 0 * * *', 'SELECT maintain_message_partitions()');