-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Esta función auxiliar obtiene la clave de encriptación
CREATE OR REPLACE FUNCTION get_encryption_key()
RETURNS text AS $$
DECLARE
    v_key text;
BEGIN
    BEGIN
        v_key := current_setting('POSTGRES_ENCRYPT_KEY');
        RETURN v_key;
    EXCEPTION WHEN OTHERS THEN
        RAISE EXCEPTION 'Encryption key not found. Make sure POSTGRES_ENCRYPT_KEY is set.';
    END;
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