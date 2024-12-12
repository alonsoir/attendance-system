-- Añadir al inicio de 02-schema.sql
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    role_id UUID REFERENCES roles(id)
);

CREATE TABLE schools (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    address TEXT,
    country TEXT
);

CREATE TABLE tutors (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT
);

CREATE TABLE students (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    date_of_birth DATE,
    school_id UUID REFERENCES schools(id)
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    student_id UUID REFERENCES students(id),
    school_id UUID REFERENCES schools(id),
    claude_conversation_id TEXT,
    status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    sender_type TEXT,
    sender_id UUID,
    content TEXT,
    claude_response_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE service_status (
    id UUID PRIMARY KEY,
    service_name TEXT NOT NULL,
    status BOOLEAN NOT NULL,
    error_message TEXT,
    last_check TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id),
    permission_id UUID REFERENCES permissions(id),
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE tutor_student (
    tutor_id UUID REFERENCES tutors(id),
    student_id UUID REFERENCES students(id),
    relationship_type TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tutor_id, student_id)
);

-- Procedimientos para ACL
CREATE OR REPLACE PROCEDURE create_role(
    p_name VARCHAR(255),
    INOUT p_id UUID
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
    INOUT p_id UUID
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
    INOUT p_id UUID
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

CREATE OR REPLACE PROCEDURE create_school(
    p_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_address VARCHAR(255),
    p_country VARCHAR(100),
    INOUT p_id UUID
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
    INOUT p_id UUID
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
    INOUT p_id UUID
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

CREATE OR REPLACE PROCEDURE create_conversation(
    p_student_id UUID,
    p_school_id UUID,
    p_claude_conversation_id VARCHAR(255),
    INOUT p_id UUID
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
    INOUT p_id UUID
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
    INOUT p_id UUID
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

CREATE OR REPLACE PROCEDURE create_role_permission(
    p_role_id UUID,
    p_permission_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO role_permissions (role_id, permission_id)
    VALUES (p_role_id, p_permission_id)
    ON CONFLICT (role_id, permission_id) DO NOTHING;
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
    INSERT INTO tutor_student (tutor_id, student_id, relationship_type)
    VALUES (p_tutor_id, p_student_id, p_relationship_type)
    ON CONFLICT (tutor_id, student_id)
    DO UPDATE SET
        relationship_type = p_relationship_type,
        updated_at = CURRENT_TIMESTAMP;
END;
$$;