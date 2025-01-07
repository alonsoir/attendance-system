-- Este archivo asume que pgcrypto y uuid-ossp ya están instalados
-- y que las funciones encrypt_value/decrypt_value ya existen

-- Habilitar pg_cron para tareas programadas
CREATE EXTENSION IF NOT EXISTS "pg_cron";

-- Crear tipos ENUM para el sistema
CREATE TYPE sender_type_enum AS ENUM ('CLAUDE', 'SCHOOL', 'TUTOR');
CREATE TYPE notification_level AS ENUM ('INFO', 'WARNING', 'ERROR', 'CRITICAL');
CREATE TYPE notification_category AS ENUM (
    'SYSTEM',           -- eventos del sistema
    'SECURITY',         -- intentos de acceso, cambios en permisos
    'DATA_INTEGRITY',   -- problemas con datos
    'PERFORMANCE',      -- issues de rendimiento
    'ACCESS_CONTROL'    -- eventos relacionados con ACL
);

-- Configuración inicial de pg_cron
SELECT cron.schedule('maintain-messages-partitions', '0 0 * * *', 'SELECT maintain_message_partitions()');