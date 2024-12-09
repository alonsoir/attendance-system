-- Crear extensión pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Crear tablas para control de acceso y auditoría
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id),
    permission_id UUID NOT NULL REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

-- Crear procedimientos almacenados para cifrado y descifrado
CREATE OR REPLACE FUNCTION get_encrypted_schools()
RETURNS TABLE (
    id UUID,
    name VARCHAR(255),
    phone VARCHAR(50),
    address VARCHAR(255),
    country VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        id,
        convert_from(decrypt(name, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'), 'UTF-8') AS name,
        convert_from(decrypt(phone, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'), 'UTF-8') AS phone,
        convert_from(decrypt(address, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'), 'UTF-8') AS address,
        convert_from(decrypt(country, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'), 'UTF-8') AS country
    FROM schools;
END;
$$;

CREATE OR REPLACE PROCEDURE create_encrypted_school(
    p_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_address VARCHAR(255),
    p_country VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO schools (
        name,
        phone,
        address,
        country
    ) VALUES (
        encrypt(p_name, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'),
        encrypt(p_phone, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'),
        encrypt(p_address, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'),
        encrypt(p_country, current_setting('ENCRYPT_KEY'), 'aes-256-cbc')
    );
END;
$$;

CREATE OR REPLACE PROCEDURE update_encrypted_school(
    p_id UUID,
    p_new_name VARCHAR(255),
    p_new_phone VARCHAR(50),
    p_new_address VARCHAR(255),
    p_new_country VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE schools
    SET name = encrypt(p_new_name, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'),
        phone = encrypt(p_new_phone, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'),
        address = encrypt(p_new_address, current_setting('ENCRYPT_KEY'), 'aes-256-cbc'),
        country = encrypt(p_new_country, current_setting('ENCRYPT_KEY'), 'aes-256-cbc')
    WHERE id = p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_school(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM schools
    WHERE id = p_id;
END;
$$;

-- Crear roles y permisos iniciales
INSERT INTO roles (name) VALUES ('ADMIN'), ('SCHOOL'), ('TUTOR');

INSERT INTO permissions (name)
VALUES ('CREATE_SCHOOL'), ('UPDATE_SCHOOL'), ('DELETE_SCHOOL'),
       ('CREATE_STUDENT'), ('UPDATE_STUDENT'), ('DELETE_STUDENT'),
       ('CREATE_TUTOR'), ('UPDATE_TUTOR'), ('DELETE_TUTOR'),
       ('VIEW_STUDENT_RECORDS'), ('SEND_MESSAGES'), ('CLOSE_CONVERSATIONS');

-- Asignar permisos a los roles
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
CROSS JOIN permissions p
WHERE r.name = 'ADMIN';

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'SCHOOL' AND p.name IN ('CREATE_STUDENT', 'UPDATE_STUDENT', 'DELETE_STUDENT', 'SEND_MESSAGES', 'CLOSE_CONVERSATIONS');

INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'TUTOR' AND p.name IN ('VIEW_STUDENT_RECORDS', 'SEND_MESSAGES');

-- Crear usuarios iniciales
INSERT INTO users (username, password_hash, role_id)
VALUES ('admin', crypt('admin_password', gen_salt('bf')), (SELECT id FROM roles WHERE name = 'ADMIN'));

INSERT INTO users (username, password_hash, role_id)
VALUES ('school_user', crypt('school_password', gen_salt('bf')), (SELECT id FROM roles WHERE name = 'SCHOOL'));

INSERT INTO users (username, password_hash, role_id)
VALUES ('tutor_user', crypt('tutor_password', gen_salt('bf')), (SELECT id FROM roles WHERE name = 'TUTOR'));