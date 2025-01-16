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

-- UPDATE procedures
CREATE OR REPLACE PROCEDURE update_encrypted_role(
    p_id UUID,
    p_name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE roles
    SET name = encrypt_value(p_name)
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Role with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_encrypted_permission(
    p_id UUID,
    p_name VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE permissions
    SET name = encrypt_value(p_name)
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Permission with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_encrypted_user(
    p_id UUID,
    p_username VARCHAR(255),
    p_password VARCHAR(255),
    p_role_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE users
    SET username = encrypt_value(p_username),
        password_hash = CASE
            WHEN p_password IS NOT NULL THEN crypt(p_password, gen_salt('bf'))
            ELSE password_hash
        END,
        role_id = p_role_id
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'User with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_encrypted_school(
    p_id UUID,
    p_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_address VARCHAR(255),
    p_country VARCHAR(100)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE schools
    SET name = encrypt_value(p_name),
        phone = encrypt_value(p_phone),
        address = encrypt_value(p_address),
        country = encrypt_value(p_country)
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'School with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_encrypted_tutor(
    p_id UUID,
    p_name VARCHAR(255),
    p_phone VARCHAR(50),
    p_email VARCHAR(255)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE tutors
    SET name = encrypt_value(p_name),
        phone = encrypt_value(p_phone),
        email = encrypt_value(p_email)
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tutor with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_encrypted_student(
    p_id UUID,
    p_name VARCHAR(255),
    p_date_of_birth DATE,
    p_school_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE students
    SET name = encrypt_value(p_name),
        date_of_birth = p_date_of_birth,
        school_id = p_school_id
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Student with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_encrypted_conversation(
    p_id UUID,
    p_student_id UUID,
    p_school_id UUID,
    p_claude_conversation_id VARCHAR(255),
    p_status TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE conversations
    SET student_id = p_student_id,
        school_id = p_school_id,
        claude_conversation_id = p_claude_conversation_id,
        status = p_status
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Conversation with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_encrypted_message(
    p_id UUID,
    p_conversation_id UUID,
    p_sender_type VARCHAR(50),
    p_sender_id UUID,
    p_content TEXT,
    p_claude_response_metadata JSONB
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE messages
    SET conversation_id = p_conversation_id,
        sender_type = p_sender_type,
        sender_id = p_sender_id,
        content = encrypt_value(p_content),
        claude_response_metadata = p_claude_response_metadata
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Message with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_service_status(
    p_id UUID,
    p_service_name VARCHAR(50),
    p_status BOOLEAN,
    p_error_message VARCHAR(50)
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE service_status
    SET service_name = p_service_name,
        status = p_status,
        error_message = p_error_message,
        last_check = CURRENT_TIMESTAMP
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Service status with ID % not found', p_id;
    END IF;
END;
$$;

-- DELETE procedures
CREATE OR REPLACE PROCEDURE delete_role(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM role_permissions WHERE role_id = p_id;
    DELETE FROM roles WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Role with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_permission(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM role_permissions WHERE permission_id = p_id;
    DELETE FROM permissions WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Permission with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_user(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM users WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'User with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_school(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Primero actualizar los estudiantes para quitar la referencia
    UPDATE students SET school_id = NULL WHERE school_id = p_id;

    -- Luego eliminar las conversaciones asociadas
    DELETE FROM messages
    WHERE conversation_id IN (SELECT id FROM conversations WHERE school_id = p_id);

    DELETE FROM conversations WHERE school_id = p_id;
    DELETE FROM schools WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'School with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_tutor(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM tutor_student WHERE tutor_id = p_id;
    DELETE FROM tutors WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tutor with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_student(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Eliminar relaciones con tutores
    DELETE FROM tutor_student WHERE student_id = p_id;

    -- Eliminar mensajes de las conversaciones del estudiante
    DELETE FROM messages
    WHERE conversation_id IN (SELECT id FROM conversations WHERE student_id = p_id);

    -- Eliminar conversaciones
    DELETE FROM conversations WHERE student_id = p_id;

    -- Finalmente eliminar el estudiante
    DELETE FROM students WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Student with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_conversation(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM messages WHERE conversation_id = p_id;
    DELETE FROM conversations WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Conversation with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_message(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM messages WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Message with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_service_status(
    p_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM service_status WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Service status with ID % not found', p_id;
    END IF;
END;
$$;

-- READ procedures (GET by ID)
CREATE OR REPLACE FUNCTION get_encrypted_role(p_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT r.id, decrypt_value(r.name)::TEXT
    FROM roles r
    WHERE r.id = p_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_encrypted_permission(p_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, decrypt_value(p.name)::TEXT
    FROM permissions p
    WHERE p.id = p_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_encrypted_user(p_id UUID)
RETURNS TABLE (
    id UUID,
    username TEXT,
    role_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, decrypt_value(u.username)::TEXT, u.role_id
    FROM users u
    WHERE u.id = p_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_encrypted_school(p_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT,
    phone TEXT,
    address TEXT,
    country TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        decrypt_value(s.name)::TEXT,
        decrypt_value(s.phone)::TEXT,
        decrypt_value(s.address)::TEXT,
        decrypt_value(s.country)::TEXT
    FROM schools s
    WHERE s.id = p_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_encrypted_tutor(p_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT,
    phone TEXT,
    email TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        decrypt_value(t.name)::TEXT,
        decrypt_value(t.phone)::TEXT,
        decrypt_value(t.email)::TEXT
    FROM tutors t
    WHERE t.id = p_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_encrypted_student(p_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT,
    date_of_birth DATE,
    school_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        decrypt_value(s.name)::TEXT,
        s.date_of_birth,
        s.school_id
    FROM students s
    WHERE s.id = p_id;
END;
$$;

-- GET ALL procedures
CREATE OR REPLACE FUNCTION get_all_encrypted_roles()
RETURNS TABLE (
    id UUID,
    name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT r.id, decrypt_value(r.name)::TEXT
    FROM roles r;
END;
$$;

CREATE OR REPLACE FUNCTION get_all_encrypted_permissions()
RETURNS TABLE (
    id UUID,
    name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, decrypt_value(p.name)::TEXT
    FROM permissions p;
END;
$$;

CREATE OR REPLACE FUNCTION get_all_encrypted_users()
RETURNS TABLE (
    id UUID,
    username TEXT,
    role_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT u.id, decrypt_value(u.username)::TEXT, u.role_id
    FROM users u;
END;
$$;

CREATE OR REPLACE FUNCTION get_all_encrypted_schools()
RETURNS TABLE (
    id UUID,
    name TEXT,
    phone TEXT,
    address TEXT,
    country TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        decrypt_value(s.name)::TEXT,
        decrypt_value(s.phone)::TEXT,
        decrypt_value(s.address)::TEXT,
        decrypt_value(s.country)::TEXT
    FROM schools s;
END;
$$;

CREATE OR REPLACE FUNCTION get_all_encrypted_tutors()
RETURNS TABLE (
    id UUID,
    name TEXT,
    phone TEXT,
    email TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        decrypt_value(t.name)::TEXT,
        decrypt_value(t.phone)::TEXT,
        decrypt_value(t.email)::TEXT
    FROM tutors t;
END;
$$;

CREATE OR REPLACE FUNCTION get_all_encrypted_students()
RETURNS TABLE (
    id UUID,
    name TEXT,
    date_of_birth DATE,
    school_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        decrypt_value(s.name)::TEXT,
        s.date_of_birth,
        s.school_id
    FROM students s;
END;
$$;

CREATE OR REPLACE PROCEDURE update_role_permission(
    p_role_id UUID,
    p_permission_id UUID,
    p_action VARCHAR(10)  -- 'ADD' o 'REMOVE'
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_action = 'ADD' THEN
        INSERT INTO role_permissions (role_id, permission_id)
        VALUES (p_role_id, p_permission_id)
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    ELSIF p_action = 'REMOVE' THEN
        DELETE FROM role_permissions
        WHERE role_id = p_role_id AND permission_id = p_permission_id;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Role-Permission relationship not found for role_id % and permission_id %',
                          p_role_id, p_permission_id;
        END IF;
    ELSE
        RAISE EXCEPTION 'Invalid action: %. Must be either ADD or REMOVE', p_action;
    END IF;
END;
$$;

-- Procedimientos para la relación tutor-student
CREATE OR REPLACE PROCEDURE update_tutor_student_relationship(
    p_tutor_id UUID,
    p_student_id UUID,
    p_relationship_type VARCHAR(50),
    p_is_active BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE tutor_student
    SET relationship_type = p_relationship_type,
        is_active = p_is_active,
        updated_at = CURRENT_TIMESTAMP
    WHERE tutor_id = p_tutor_id AND student_id = p_student_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tutor-Student relationship not found for tutor_id % and student_id %',
                      p_tutor_id, p_student_id;
    END IF;
END;
$$;

-- Función para obtener todos los tutores de un estudiante
CREATE OR REPLACE FUNCTION get_student_tutors(p_student_id UUID)
RETURNS TABLE (
    tutor_id UUID,
    tutor_name TEXT,
    tutor_phone TEXT,
    tutor_email TEXT,
    relationship_type TEXT,
    is_active BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        decrypt_value(t.name)::TEXT,
        decrypt_value(t.phone)::TEXT,
        decrypt_value(t.email)::TEXT,
        ts.relationship_type,
        ts.is_active
    FROM tutors t
    JOIN tutor_student ts ON t.id = ts.tutor_id
    WHERE ts.student_id = p_student_id;
END;
$$;

-- Función para obtener todos los estudiantes de un tutor
CREATE OR REPLACE FUNCTION get_tutor_students(p_tutor_id UUID)
RETURNS TABLE (
    student_id UUID,
    student_name TEXT,
    date_of_birth DATE,
    school_name TEXT,
    relationship_type TEXT,
    is_active BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        decrypt_value(s.name)::TEXT,
        s.date_of_birth,
        decrypt_value(sc.name)::TEXT,
        ts.relationship_type,
        ts.is_active
    FROM students s
    JOIN tutor_student ts ON s.id = ts.student_id
    LEFT JOIN schools sc ON s.school_id = sc.id
    WHERE ts.tutor_id = p_tutor_id;
END;
$$;

-- Función para obtener todas las conversaciones de un estudiante
CREATE OR REPLACE FUNCTION get_student_conversations(p_student_id UUID)
RETURNS TABLE (
    conversation_id UUID,
    school_name TEXT,
    claude_conversation_id TEXT,
    status TEXT,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        decrypt_value(s.name)::TEXT,
        c.claude_conversation_id,
        c.status,
        c.created_at
    FROM conversations c
    JOIN schools s ON c.school_id = s.id
    WHERE c.student_id = p_student_id
    ORDER BY c.created_at DESC;
END;
$$;

-- Función para obtener todos los mensajes de una conversación
CREATE OR REPLACE FUNCTION get_conversation_messages(p_conversation_id UUID)
RETURNS TABLE (
    message_id UUID,
    sender_type TEXT,
    sender_name TEXT,
    content TEXT,
    claude_response_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.sender_type,
        CASE
            WHEN m.sender_type = 'SCHOOL' THEN decrypt_value((SELECT name FROM schools WHERE id = (SELECT school_id FROM conversations WHERE id = m.conversation_id)))
            WHEN m.sender_type = 'TUTOR' THEN decrypt_value((SELECT name FROM tutors WHERE id = m.sender_id))
            WHEN m.sender_type = 'STUDENT' THEN decrypt_value((SELECT name FROM students WHERE id = m.sender_id))
            ELSE 'SYSTEM'
        END::TEXT,
        decrypt_value(m.content)::TEXT,
        m.claude_response_metadata,
        m.created_at
    FROM messages m
    WHERE m.conversation_id = p_conversation_id
    ORDER BY m.created_at ASC;
END;
$$;

CREATE OR REPLACE FUNCTION get_all_service_status()
RETURNS TABLE (
    service_id UUID,
    service_name TEXT,
    status BOOLEAN,
    error_message TEXT,
    last_check TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        ss.id,
        ss.service_name,
        ss.status,
        ss.error_message,
        ss.last_check
    FROM service_status ss
    ORDER BY ss.service_name;
END;
$$;

-- Función para obtener todos los permisos de un rol
CREATE OR REPLACE FUNCTION get_role_permissions(p_role_id UUID)
RETURNS TABLE (
    permission_id UUID,
    permission_name TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        decrypt_value(p.name)::TEXT
    FROM permissions p
    JOIN role_permissions rp ON p.id = rp.permission_id
    WHERE rp.role_id = p_role_id;
END;
$$;

-- Función para verificar si un usuario tiene un permiso específico
CREATE OR REPLACE FUNCTION user_has_permission(p_user_id UUID, p_permission_name TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_has_permission BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM users u
        JOIN role_permissions rp ON u.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE u.id = p_user_id
        AND decrypt_value(p.name) = p_permission_name
    ) INTO v_has_permission;

    RETURN v_has_permission;
END;
$$;
