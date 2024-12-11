-- Crear extensiones necesarias
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear tablas para control de acceso y auditoría
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id)
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id),
    permission_id UUID NOT NULL REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),
    action TEXT NOT NULL,
    resource TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

-- Crear tablas para la aplicación
CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    address TEXT NOT NULL,
    country TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tutors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
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

-- Crear índices
CREATE INDEX idx_conversations_claude_id ON conversations(claude_conversation_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_tutor_student_student ON tutor_student(student_id);
CREATE INDEX idx_tutor_student_tutor ON tutor_student(tutor_id);

-- Procedimientos para ACL
CREATE OR REPLACE PROCEDURE create_role(
    p_name VARCHAR(255),
    OUT p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO roles (id, name)
    VALUES (uuid_generate_v4(), encrypt_value(p_name))
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_permission(
    p_name VARCHAR(255),
    OUT p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO permissions (id, name)
    VALUES (uuid_generate_v4(), encrypt_value(p_name))
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_user(
    p_username VARCHAR(255),
    p_password VARCHAR(255),
    p_role_id UUID,
    OUT p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO users (id, username, password_hash, role_id)
    VALUES (
        uuid_generate_v4(),
        encrypt_value(p_username),
        crypt(p_password, gen_salt('bf')),
        p_role_id
    )
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_role_permission(
    p_role_id UUID,
    p_permission_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO role_permissions (role_id, permission_id)
    VALUES (p_role_id, p_permission_id);
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
    VALUES (p_user_id, encrypt_value(p_action), encrypt_value(p_resource), CURRENT_TIMESTAMP);
END;
$$;

-- Procedimientos para la aplicación
CREATE OR REPLACE PROCEDURE create_school(
    p_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_address VARCHAR(255),
    p_country VARCHAR(100),
    OUT p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO schools (id, name, phone, address, country)
    VALUES (
        uuid_generate_v4(),
        encrypt_value(p_name),
        encrypt_value(p_phone),
        encrypt_value(p_address),
        encrypt_value(p_country)
    )
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_tutor(
    p_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_email VARCHAR(255),
    OUT p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO tutors (id, name, phone, email)
    VALUES (
        uuid_generate_v4(),
        encrypt_value(p_name),
        encrypt_value(p_phone),
        encrypt_value(p_email)
    )
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_student(
    p_name VARCHAR(255),
    p_date_of_birth DATE,
    p_school_id UUID,
    OUT p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO students (id, name, date_of_birth, school_id)
    VALUES (
        uuid_generate_v4(),
        encrypt_value(p_name),
        p_date_of_birth,
        p_school_id
    )
    RETURNING id INTO p_id;
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
    INSERT INTO tutor_student (tutor_id, student_id, relationship_type, is_active)
    VALUES (p_tutor_id, p_student_id, p_relationship_type, true);
END;
$$;

CREATE OR REPLACE PROCEDURE create_conversation(
    p_student_id UUID,
    p_school_id UUID,
    p_claude_conversation_id VARCHAR(255),
    OUT p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO conversations (
        id,
        student_id,
        school_id,
        claude_conversation_id,
        status
    )
    VALUES (
        uuid_generate_v4(),
        p_student_id,
        p_school_id,
        p_claude_conversation_id,
        'INITIATED'
    )
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_message(
    p_conversation_id UUID,
    p_sender_type VARCHAR(50),
    p_sender_id UUID,
    p_content TEXT,
    p_claude_response_metadata JSONB,
    OUT p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO messages (
        id,
        conversation_id,
        sender_type,
        sender_id,
        content,
        claude_response_metadata
    )
    VALUES (
        uuid_generate_v4(),
        p_conversation_id,
        p_sender_type,
        p_sender_id,
        encrypt_value(p_content),
        p_claude_response_metadata
    )
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_service_status(
    p_service_name VARCHAR(50),
    p_status BOOLEAN,
    p_error_message VARCHAR(50),
    OUT p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO service_status (
        id,
        service_name,
        status,
        error_message
    )
    VALUES (
        uuid_generate_v4(),
        p_service_name,
        p_status,
        p_error_message
    )
    RETURNING id INTO p_id;
END;
$$;
