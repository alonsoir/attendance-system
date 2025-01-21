-- Función para validar si un usuario tiene acceso a una escuela
CREATE OR REPLACE FUNCTION can_access_school(
    p_user_id UUID,
    p_school_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql AS $$
DECLARE
    v_entity_type VARCHAR(6);
    v_entity_id UUID;
BEGIN
    -- Obtener información del usuario
    SELECT entity_type, entity_id
    INTO v_entity_type, v_entity_id
    FROM users
    WHERE id = p_user_id;

    -- Validar acceso
    RETURN (
        -- Es la misma escuela
        (v_entity_type = 'SCHOOL' AND v_entity_id = p_school_id)
        OR
        -- Es un tutor con estudiantes en esa escuela
        (v_entity_type = 'TUTOR' AND EXISTS (
            SELECT 1
            FROM students s
            WHERE s.school_id = p_school_id
            AND EXISTS (
                SELECT 1
                FROM messages m
                WHERE m.student_id = s.id
                AND m.tutor_id = v_entity_id
            )
        ))
    );
END;
$$;

-- Función para validar si un usuario puede acceder a un estudiante
CREATE OR REPLACE FUNCTION can_access_student(
    p_user_id UUID,
    p_student_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql AS $$
DECLARE
    v_entity_type VARCHAR(6);
    v_entity_id UUID;
    v_school_id UUID;
BEGIN
    -- Obtener información del usuario
    SELECT entity_type, entity_id
    INTO v_entity_type, v_entity_id
    FROM users
    WHERE id = p_user_id;

    -- Obtener escuela del estudiante
    SELECT school_id
    INTO v_school_id
    FROM students
    WHERE id = p_student_id;

    -- Validar acceso
    RETURN (
        -- Es de la misma escuela
        (v_entity_type = 'SCHOOL' AND v_entity_id = v_school_id)
        OR
        -- Es un tutor del estudiante
        (v_entity_type = 'TUTOR' AND EXISTS (
            SELECT 1
            FROM messages m
            WHERE m.student_id = p_student_id
            AND m.tutor_id = v_entity_id
        ))
    );
END;
$$;

-- Función para validar si un usuario puede acceder a un mensaje
CREATE OR REPLACE FUNCTION can_access_message(
    p_user_id UUID,
    p_message_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql AS $$
DECLARE
    v_entity_type VARCHAR(6);
    v_entity_id UUID;
    v_school_id UUID;
    v_tutor_id UUID;
BEGIN
    -- Obtener información del usuario
    SELECT entity_type, entity_id
    INTO v_entity_type, v_entity_id
    FROM users
    WHERE id = p_user_id;

    -- Obtener información del mensaje
    SELECT school_id, tutor_id
    INTO v_school_id, v_tutor_id
    FROM messages
    WHERE id = p_message_id;

    -- Validar acceso
    RETURN (
        -- Es de la misma escuela
        (v_entity_type = 'SCHOOL' AND v_entity_id = v_school_id)
        OR
        -- Es el mismo tutor
        (v_entity_type = 'TUTOR' AND v_entity_id = v_tutor_id)
    );
END;
$$;

-- Procedimiento para registrar intentos de acceso no autorizados
CREATE OR REPLACE PROCEDURE log_unauthorized_access(
    p_user_id UUID,
    p_resource_type VARCHAR(50),
    p_resource_id UUID,
    p_action VARCHAR(50)
)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details,
        source_entity_type,
        source_entity_id
    )
    SELECT
        'WARNING',
        'SECURITY',
        'Intento de acceso no autorizado',
        jsonb_build_object(
            'resource_type', p_resource_type,
            'resource_id', p_resource_id,
            'action', p_action,
            'user_entity_type', u.entity_type,
            'user_entity_id', u.entity_id
        ),
        u.entity_type,
        u.entity_id
    FROM users u
    WHERE u.id = p_user_id;
END;
$$;

-- Trigger para validar acceso antes de crear o actualizar mensajes
CREATE OR REPLACE FUNCTION validate_message_access()
RETURNS TRIGGER AS $$
BEGIN
    -- Validar que el usuario tenga acceso al estudiante y la escuela
    IF NOT (
        can_access_student(NEW.created_by, NEW.student_id) AND
        can_access_school(NEW.created_by, NEW.school_id)
    ) THEN
        CALL log_unauthorized_access(
            NEW.created_by,
            'message',
            NEW.id,
            TG_OP
        );
        RAISE EXCEPTION 'Acceso no autorizado';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Vista segura para mensajes que filtra por acceso
CREATE OR REPLACE VIEW secure_messages AS
SELECT m.*
FROM messages m
WHERE can_access_message(current_user::uuid, m.id);