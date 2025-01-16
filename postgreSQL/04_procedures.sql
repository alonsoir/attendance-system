-- Procedimientos para ACL
CREATE OR REPLACE PROCEDURE create_role(
    p_name VARCHAR(50),
    p_created_by UUID,
    INOUT p_id UUID
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO roles (id, name, created_by, updated_by)
    VALUES (uuid_generate_v4(), p_name, p_created_by, p_created_by)
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
    VALUES (uuid_generate_v4(), p_name, p_created_by, p_created_by)
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
        p_username,
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
        p_name,
        p_phone,
        p_address,
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
        p_name,
        p_phone,
        p_email,
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
        p_name,
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
        p_content,
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
    SET name = p_name,
        phone = p_phone,
        address = p_address,
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
    SET name = p_name,
        phone = p_phone,
        email = p_email,
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
    SET name = p_name,
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

-- Procedimiento para obtener detalles de un rol
CREATE OR REPLACE PROCEDURE get_role_details(
    p_name VARCHAR(50),
    INOUT p_id UUID,
    INOUT p_created_at TIMESTAMP WITH TIME ZONE,
    INOUT p_created_by UUID,
    INOUT p_updated_at TIMESTAMP WITH TIME ZONE,
    INOUT p_updated_by UUID
) LANGUAGE plpgsql AS $$
BEGIN
    SELECT
        id,
        created_at,
        created_by,
        updated_at,
        updated_by
    INTO
        p_id,
        p_created_at,
        p_created_by,
        p_updated_at,
        p_updated_by
    FROM roles
    WHERE name = p_name;
END;
$$;

-- Procedimiento para obtener detalles de un usuario
CREATE OR REPLACE PROCEDURE get_user_details(
    p_username VARCHAR(50),
    INOUT p_id UUID,
    INOUT p_password_hash VARCHAR(100),
    INOUT p_role_id UUID,
    INOUT p_role_name VARCHAR(50),
    INOUT p_entity_type VARCHAR(6),
    INOUT p_entity_id UUID,
    INOUT p_entity_name VARCHAR(50),
    INOUT p_created_at TIMESTAMP WITH TIME ZONE,
    INOUT p_created_by UUID,
    INOUT p_updated_at TIMESTAMP WITH TIME ZONE,
    INOUT p_updated_by UUID
) LANGUAGE plpgsql AS $$
BEGIN
    SELECT
        u.id,
        u.password_hash,
        u.role_id,
        r.name,
        u.entity_type,
        u.entity_id,
        CASE
            WHEN u.entity_type = 'SCHOOL' THEN s.name
            WHEN u.entity_type = 'TUTOR' THEN t.name
            ELSE NULL
        END,
        u.created_at,
        u.created_by,
        u.updated_at,
        u.updated_by
    INTO
        p_id,
        p_password_hash,
        p_role_id,
        p_role_name,
        p_entity_type,
        p_entity_id,
        p_entity_name,
        p_created_at,
        p_created_by,
        p_updated_at,
        p_updated_by
    FROM users u
    LEFT JOIN roles r ON u.role_id = r.id
    LEFT JOIN schools s ON u.entity_type = 'SCHOOL' AND u.entity_id = s.id
    LEFT JOIN tutors t ON u.entity_type = 'TUTOR' AND u.entity_id = t.id
    WHERE u.username = p_username;
END;
$$;