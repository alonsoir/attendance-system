-- Procedimientos para ACL
CREATE OR REPLACE PROCEDURE create_role(
    p_name VARCHAR(50),
    p_created_by UUID,
    INOUT p_id UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO roles (id, name, created_by, updated_by)
    VALUES (uuid_generate_v4(), encrypt_value(p_name), p_created_by, p_created_by)
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_permission(
    p_name VARCHAR(50),
    p_created_by UUID,
    INOUT p_id UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO permissions (id, name, created_by, updated_by)
    VALUES (uuid_generate_v4(), encrypt_value(p_name), p_created_by, p_created_by)
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_user(
    p_username VARCHAR(50),
    p_password VARCHAR(100),
    p_role_id UUID,
    p_entity_type VARCHAR(6),
    p_entity_id UUID,
    p_created_by UUID,
    INOUT p_id UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO users (
        id, username, password_hash, role_id,
        entity_type, entity_id,
        created_by, updated_by
    )
    VALUES (
        uuid_generate_v4(),
        encrypt_value(p_username),
        crypt(p_password, gen_salt('bf')),
        p_role_id,
        p_entity_type,
        p_entity_id,
        p_created_by,
        p_created_by
    )
    RETURNING id INTO p_id;
END;
$$;

-- Procedimientos para entidades principales
CREATE OR REPLACE PROCEDURE create_school(
    p_name VARCHAR(50),
    p_phone VARCHAR(20),
    p_address VARCHAR(50),
    p_state VARCHAR(20),
    p_country VARCHAR(5),
    p_created_by UUID,
    INOUT p_id UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO schools (
        id, name, phone, address, state, country,
        created_by, updated_by
    )
    VALUES (
        uuid_generate_v4(),
        encrypt_value(p_name),
        encrypt_value(p_phone),
        encrypt_value(p_address),
        p_state,
        p_country,
        p_created_by,
        p_created_by
    )
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_tutor(
    p_name VARCHAR(50),
    p_phone VARCHAR(20),
    p_email VARCHAR(50),
    p_created_by UUID,
    INOUT p_id UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO tutors (
        id, name, phone, email,
        created_by, updated_by
    )
    VALUES (
        uuid_generate_v4(),
        encrypt_value(p_name),
        encrypt_value(p_phone),
        encrypt_value(p_email),
        p_created_by,
        p_created_by
    )
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_student(
    p_name VARCHAR(50),
    p_date_of_birth DATE,
    p_school_id UUID,
    p_created_by UUID,
    INOUT p_id UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO students (
        id, name, date_of_birth, school_id,
        created_by, updated_by
    )
    VALUES (
        uuid_generate_v4(),
        encrypt_value(p_name),
        p_date_of_birth,
        p_school_id,
        p_created_by,
        p_created_by
    )
    RETURNING id INTO p_id;
END;
$$;

CREATE OR REPLACE PROCEDURE create_message(
    p_claude_conversation_id VARCHAR(50),
    p_student_id UUID,
    p_school_id UUID,
    p_tutor_id UUID,
    p_sender_type sender_type_enum,
    p_content VARCHAR(1000),
    p_created_by UUID,
    INOUT p_id UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO messages (
        id, claude_conversation_id,
        student_id, school_id, tutor_id,
        sender_type, content,
        created_by
    )
    VALUES (
        uuid_generate_v4(),
        p_claude_conversation_id,
        p_student_id,
        p_school_id,
        p_tutor_id,
        p_sender_type,
        encrypt_value(p_content),
        p_created_by
    )
    RETURNING id INTO p_id;

    -- Registrar la creación del mensaje en las notificaciones si es necesario
    IF p_sender_type = 'CLAUDE' THEN
        INSERT INTO system_notifications (
            level,
            category,
            message,
            details,
            source_entity_type,
            source_entity_id
        ) VALUES (
            'INFO',
            'SYSTEM',
            'Nuevo mensaje de Claude',
            jsonb_build_object(
                'conversation_id', p_claude_conversation_id,
                'student_id', p_student_id
            ),
            CASE
                WHEN p_school_id IS NOT NULL THEN 'SCHOOL'
                WHEN p_tutor_id IS NOT NULL THEN 'TUTOR'
            END,
            COALESCE(p_school_id, p_tutor_id)
        );
    END IF;
END;
$$;

-- Procedimientos de actualización
CREATE OR REPLACE PROCEDURE update_school(
    p_id UUID,
    p_name VARCHAR(50),
    p_phone VARCHAR(20),
    p_address VARCHAR(50),
    p_state VARCHAR(20),
    p_country VARCHAR(5),
    p_updated_by UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE schools
    SET name = encrypt_value(p_name),
        phone = encrypt_value(p_phone),
        address = encrypt_value(p_address),
        state = p_state,
        country = p_country,
        updated_at = CURRENT_TIMESTAMP,
        updated_by = p_updated_by
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'School with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_tutor(
    p_id UUID,
    p_name VARCHAR(50),
    p_phone VARCHAR(20),
    p_email VARCHAR(50),
    p_updated_by UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE tutors
    SET name = encrypt_value(p_name),
        phone = encrypt_value(p_phone),
        email = encrypt_value(p_email),
        updated_at = CURRENT_TIMESTAMP,
        updated_by = p_updated_by
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tutor with ID % not found', p_id;
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE update_student(
    p_id UUID,
    p_name VARCHAR(50),
    p_date_of_birth DATE,
    p_school_id UUID,
    p_updated_by UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE students
    SET name = encrypt_value(p_name),
        date_of_birth = p_date_of_birth,
        school_id = p_school_id,
        updated_at = CURRENT_TIMESTAMP,
        updated_by = p_updated_by
    WHERE id = p_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Student with ID % not found', p_id;
    END IF;
END;
$$;