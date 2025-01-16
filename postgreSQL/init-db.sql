-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear tabla para almacenar la clave de cifrado
CREATE TABLE IF NOT EXISTS encryption_config (
    key_name TEXT PRIMARY KEY,
    key_value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Función para generar una nueva clave de cifrado
CREATE OR REPLACE FUNCTION generate_encryption_key()
RETURNS text AS $$
DECLARE
    v_key text;
BEGIN
    -- Generar una clave aleatoria usando pgcrypto
    v_key := encode(gen_random_bytes(32), 'base64');
    RAISE NOTICE 'Nueva clave de cifrado generada';

    -- Almacenar la clave
    INSERT INTO encryption_config (key_name, key_value)
    VALUES ('main_key', v_key)
    ON CONFLICT (key_name) DO NOTHING
    RETURNING key_value INTO v_key;

    RAISE NOTICE 'Clave almacenada en encryption_config';
    RETURN v_key;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para obtener la clave de cifrado
CREATE OR REPLACE FUNCTION get_encryption_key()
RETURNS text AS $$
DECLARE
    v_key text;
BEGIN
    -- Intentar obtener la clave existente
    SELECT key_value INTO v_key FROM encryption_config WHERE key_name = 'main_key';

    -- Si no existe, generar una nueva
    IF v_key IS NULL THEN
        v_key := generate_encryption_key();
    END IF;

    RETURN v_key;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para encriptar valores
CREATE OR REPLACE FUNCTION encrypt_value(p_value TEXT)
RETURNS TEXT AS $$
DECLARE
    v_encrypted text;
BEGIN
    IF p_value IS NULL THEN
        RETURN NULL;
    END IF;

    v_encrypted := pgp_sym_encrypt(p_value, get_encryption_key())::text;
    RAISE NOTICE 'Valor encriptado exitosamente';
    RETURN v_encrypted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para desencriptar valores
CREATE OR REPLACE FUNCTION decrypt_value(p_value TEXT)
RETURNS TEXT AS $$
DECLARE
    v_decrypted text;
BEGIN
    IF p_value IS NULL THEN
        RETURN NULL;
    END IF;

    v_decrypted := pgp_sym_decrypt(p_value::bytea, get_encryption_key())::text;
    RAISE NOTICE 'Valor desencriptado exitosamente';
    RETURN v_decrypted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Generar la clave inicial
DO $$
BEGIN
    PERFORM generate_encryption_key();
    RAISE NOTICE 'Sistema de encriptación inicializado correctamente';
END;
$$;