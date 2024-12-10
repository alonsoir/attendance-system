-- Crear extensión pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Crear extensión uuid-ossp
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear tablas para control de acceso y auditoría
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id)
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id),
    permission_id UUID NOT NULL REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

-- Crear tablas para la aplicación
CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tutors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    school_id UUID REFERENCES schools(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tutor_student (
    tutor_id UUID REFERENCES tutors(id),
    student_id UUID REFERENCES students(id),
    relationship_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tutor_id, student_id)
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) NOT NULL,
    school_id UUID REFERENCES schools(id) NOT NULL,
    claude_conversation_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'INITIATED',
    reason TEXT,
    last_interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    CONSTRAINT valid_status CHECK (status IN (
        'INITIATED',
        'PENDING_TUTOR',
        'ACTIVE_TUTOR_DIALOG',
        'PENDING_SCHOOL_CONFIRMATION',
        'SCHOOL_CONFIRMED',
        'CLOSED',
        'CANCELLED'
    ))
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    sender_id UUID NOT NULL,
    content TEXT NOT NULL,
    claude_response_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_sender_type CHECK (sender_type IN ('SCHOOL', 'TUTOR', 'CLAUDE'))
);

CREATE TABLE service_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(50) NOT NULL,
    status BOOLEAN DEFAULT false,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message VARCHAR(50) NOT NULL
);

CREATE INDEX idx_conversations_claude_id ON conversations(claude_conversation_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_tutor_student_student ON tutor_student(student_id);
CREATE INDEX idx_tutor_student_tutor ON tutor_student(tutor_id);

-- Crear procedimientos almacenados para las tablas ACL
CREATE OR REPLACE PROCEDURE create_role(
    p_name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO roles (name) VALUES (CONVERT_TO(CAST(p_name AS bytea), 'UTF-8'));
END;
$$;

CREATE OR REPLACE PROCEDURE create_user(
    p_username VARCHAR(255),
    p_password VARCHAR(255),
    p_role_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (username, password_hash, role_id)
    VALUES (CONVERT_TO(CAST(p_username AS bytea), 'UTF-8'),
            crypt(p_password, gen_salt('bf')),
            p_role_id);
END;
$$;

CREATE OR REPLACE PROCEDURE create_permission(
    p_name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO permissions (name) VALUES (CONVERT_TO(CAST(p_name AS bytea), 'UTF-8'));
END;
$$;

CREATE OR REPLACE PROCEDURE create_role_permission(
    p_role_id UUID,
    p_permission_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO role_permissions (role_id, permission_id) VALUES (p_role_id, p_permission_id);
END;
$$;

CREATE OR REPLACE PROCEDURE create_audit_log(
    p_user_id UUID,
    p_action VARCHAR(255),
    p_resource VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit_logs (user_id, action, resource, timestamp)
    VALUES (p_user_id, p_action, p_resource, CURRENT_TIMESTAMP);
END;
$$;

-- Crear procedimientos almacenados para las tablas de la aplicación
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
        CONVERT_TO(CAST(encrypt(p_name, current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8'),
        CONVERT_TO(CAST(encrypt(p_phone, current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8'),
        CONVERT_TO(CAST(encrypt(p_address, current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8'),
        CONVERT_TO(CAST(encrypt(p_country, current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_encrypted_tutor(
    p_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_email VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO tutors (
        name,
        phone,
        email
    ) VALUES (
        CONVERT_TO(CAST(encrypt(p_name, current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8'),
        CONVERT_TO(CAST(encrypt(p_phone, current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8'),
        CONVERT_TO(CAST(encrypt(p_email, current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_encrypted_student(
    p_name VARCHAR(255),
    p_date_of_birth DATE,
    p_school_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO students (
        name,
        date_of_birth,
        school_id
    ) VALUES (
        CONVERT_TO(CAST(encrypt(p_name, current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8'),
        p_date_of_birth,
        p_school_id
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_tutor_student_relationship(
    p_tutor_id UUID,
    p_student_id UUID,
    p_relationship_type VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO tutor_student (
        tutor_id,
        student_id,
        relationship_type,
        is_active
    ) VALUES (
        p_tutor_id,
        p_student_id,
        p_relationship_type,
        true
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_conversation(
    p_student_id UUID,
    p_school_id UUID,
    p_claude_conversation_id VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO conversations (
        student_id,
        school_id,
        claude_conversation_id,
        status
    ) VALUES (
        p_student_id,
        p_school_id,
        p_claude_conversation_id,
        'INITIATED'
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_message(
    p_conversation_id UUID,
    p_sender_type VARCHAR(50),
    p_sender_id UUID,
    p_content TEXT,
    p_claude_response_metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO messages (
        conversation_id,
        sender_type,
        sender_id,
        content,
        claude_response_metadata
    ) VALUES (
        p_conversation_id,
        p_sender_type,
        p_sender_id,
        p_content,
        p_claude_response_metadata
    );
END;
$$;

CREATE OR REPLACE PROCEDURE create_service_status(
    p_service_name VARCHAR(50),
    p_status BOOLEAN,
    p_error_message VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO service_status (
        service_name,
        status,
        error_message
    ) VALUES (
        p_service_name,
        p_status,
        p_error_message
    );
END;
$$;

-- Crear usuarios iniciales
CALL create_role('ADMIN');
CALL create_role('SCHOOL');
CALL create_role('TUTOR');

CALL create_permission('CREATE_SCHOOL');
CALL create_permission('UPDATE_SCHOOL');
CALL create_permission('DELETE_SCHOOL');
CALL create_permission('CREATE_STUDENT');
CALL create_permission('UPDATE_STUDENT');
CALL create_permission('DELETE_STUDENT');
CALL create_permission('CREATE_TUTOR');
CALL create_permission('UPDATE_TUTOR');
CALL create_permission('DELETE_TUTOR');
CALL create_permission('VIEW_STUDENT_RECORDS');
CALL create_permission('SEND_MESSAGES');
CALL create_permission('CLOSE_CONVERSATIONS');

CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'CREATE_SCHOOL'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'UPDATE_SCHOOL'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'DELETE_SCHOOL'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'CREATE_STUDENT'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'UPDATE_STUDENT'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'DELETE_STUDENT'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'CREATE_TUTOR'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'UPDATE_TUTOR'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'DELETE_TUTOR'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'VIEW_STUDENT_RECORDS'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'SEND_MESSAGES'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'ADMIN'), (SELECT id FROM permissions WHERE name = 'CLOSE_CONVERSATIONS'));

CALL create_role_permission((SELECT id FROM roles WHERE name = 'SCHOOL'), (SELECT id FROM permissions WHERE name = 'CREATE_STUDENT'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'SCHOOL'), (SELECT id FROM permissions WHERE name = 'UPDATE_STUDENT'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'SCHOOL'), (SELECT id FROM permissions WHERE name = 'DELETE_STUDENT'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'SCHOOL'), (SELECT id FROM permissions WHERE name = 'SEND_MESSAGES'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'SCHOOL'), (SELECT id FROM permissions WHERE name = 'CLOSE_CONVERSATIONS'));

CALL create_role_permission((SELECT id FROM roles WHERE name = 'TUTOR'), (SELECT id FROM permissions WHERE name = 'VIEW_STUDENT_RECORDS'));
CALL create_role_permission((SELECT id FROM roles WHERE name = 'TUTOR'), (SELECT id FROM permissions WHERE name = 'SEND_MESSAGES'));

CALL create_user('admin', 'admin_password', (SELECT id FROM roles WHERE name = 'ADMIN'));
CALL create_user('school_user', 'school_password', (SELECT id FROM roles WHERE name = 'SCHOOL'));
CALL create_user('tutor_user', 'tutor_password', (SELECT id FROM roles WHERE name = 'TUTOR'));

-- Insertar datos iniciales de operativa
CALL create_encrypted_school('IES San Isidro', '+34916421394', 'Calle Toledo, 39, 28005 Madrid', 'Spain');
CALL create_encrypted_school('Lincoln High School', '+12125556789', '1234 Broadway Ave, New York, NY 10019', 'USA');

CALL create_encrypted_tutor('María García', '+34666555444', 'maria.garcia@email.com');
CALL create_encrypted_tutor('John Smith', '+12125557890', 'john.smith@email.com');
CALL create_encrypted_tutor('Ana Martínez', '+34677888999', 'ana.martinez@email.com');
CALL create_encrypted_tutor('Sarah Johnson', '+12125559012', 'sarah.johnson@email.com');

CALL create_encrypted_student('Carlos García', '2010-05-15', (SELECT id FROM schools WHERE name = CONVERT_TO(CAST(encrypt('IES San Isidro', current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')));
CALL create_encrypted_student('Emma Smith', '2009-08-22', (SELECT id FROM schools WHERE name = CONVERT_TO(CAST(encrypt('Lincoln High School', current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')));
CALL create_tutor_student_relationship((SELECT id FROM tutors WHERE name = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('María García', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
(SELECT id FROM students WHERE name = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('Carlos García', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
'PARENT');
CALL create_tutor_student_relationship((SELECT id FROM tutors WHERE name = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('John Smith', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
(SELECT id FROM students WHERE name = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('Emma Smith', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
'PARENT');
CALL create_conversation((SELECT id FROM students WHERE name = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('Carlos García', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
(SELECT id FROM schools WHERE name = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('IES San Isidro', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
'claude-conversation-1');
CALL create_conversation((SELECT id FROM students WHERE name = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('Emma Smith', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
(SELECT id FROM schools WHERE name = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('Lincoln High School', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
'claude-conversation-2');
CALL create_message((SELECT id FROM conversations WHERE claude_conversation_id = 'claude-conversation-1'),
'SCHOOL',
(SELECT id FROM users WHERE username = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('school_user', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
'Student needs help with math homework',
NULL);
CALL create_message((SELECT id FROM conversations WHERE claude_conversation_id = 'claude-conversation-2'),
'TUTOR',
(SELECT id FROM users WHERE username = CONVERT_TO(CAST(decrypt(encode(CONVERT_FROM('tutor_user', 'UTF-8'), 'escape'), current_setting('ENCRYPT_KEY'), 'aes-256-cbc') AS VARCHAR), 'UTF-8')),
'Checking on student progress',
NULL);
CALL create_service_status('Claude', false, 'No errors');
CALL create_service_status('Whatsapp', false, 'No errors');
CALL create_service_status('Backend', false, 'No errors');