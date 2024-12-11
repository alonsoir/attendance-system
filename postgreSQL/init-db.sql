-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear una tabla para almacenar la clave de encriptación
CREATE TABLE IF NOT EXISTS encryption_config (
    key_name TEXT PRIMARY KEY,
    key_value TEXT NOT NULL
);

-- Función para configurar la clave de encriptación
CREATE OR REPLACE FUNCTION set_encryption_key(p_key TEXT)
RETURNS void AS $$
BEGIN
    -- Eliminar clave anterior si existe
    DELETE FROM encryption_config WHERE key_name = 'main_key';
    -- Insertar nueva clave
    INSERT INTO encryption_config (key_name, key_value) VALUES ('main_key', p_key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para obtener la clave de encriptación
CREATE OR REPLACE FUNCTION get_encryption_key()
RETURNS text AS $$
DECLARE
    v_key text;
BEGIN
    SELECT key_value INTO v_key FROM encryption_config WHERE key_name = 'main_key';
    IF v_key IS NULL THEN
        RAISE EXCEPTION 'Encryption key not found. Make sure it has been set properly.';
    END IF;
    RETURN v_key;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para encriptar
CREATE OR REPLACE FUNCTION encrypt_value(p_value TEXT)
RETURNS TEXT AS $$
DECLARE
    v_key text;
BEGIN
    v_key := get_encryption_key();
    IF p_value IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN pgp_sym_encrypt(p_value, v_key)::text;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error encrypting value: %', SQLERRM;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para desencriptar
CREATE OR REPLACE FUNCTION decrypt_value(p_value TEXT)
RETURNS TEXT AS $$
DECLARE
    v_key text;
BEGIN
    v_key := get_encryption_key();
    IF p_value IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN pgp_sym_decrypt(p_value::bytea, v_key)::text;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Error decrypting value: %', SQLERRM;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;