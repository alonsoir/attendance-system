-- Procedimientos para migración de datos
CREATE OR REPLACE PROCEDURE migrate_old_to_new_schema()
LANGUAGE plpgsql AS $$
DECLARE
    v_old_count integer;
    v_migrated_count integer;
    v_start_time timestamp;
    v_migration_status jsonb;
BEGIN
    v_start_time := CURRENT_TIMESTAMP;
    v_migration_status := '{}';

    -- 1. Migrar datos de messages eliminando la tabla conversations
    INSERT INTO system_notifications (level, category, message)
    VALUES ('INFO', 'MIGRATION', 'Iniciando migración de mensajes');

    WITH conversation_messages AS (
        SELECT
            m.id,
            m.sender_type,
            m.sender_id,
            m.content,
            m.created_at,
            c.claude_conversation_id,
            c.student_id,
            c.school_id
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
    )
    INSERT INTO messages_new (
        id,
        claude_conversation_id,
        student_id,
        school_id,
        tutor_id,
        sender_type,
        content,
        created_at
    )
    SELECT
        cm.id,
        cm.claude_conversation_id,
        cm.student_id,
        cm.school_id,
        CASE
            WHEN cm.sender_type = 'TUTOR' THEN cm.sender_id
            ELSE NULL
        END as tutor_id,
        cm.sender_type::sender_type_enum,
        cm.content,
        cm.created_at
    FROM conversation_messages cm;

    GET DIAGNOSTICS v_migrated_count = ROW_COUNT;
    v_migration_status := jsonb_set(v_migration_status, '{messages_migrated}', to_jsonb(v_migrated_count));

    -- 2. Actualizar la tabla users para incluir entity_id y entity_type
    UPDATE users u
    SET
        entity_type = 'SCHOOL',
        entity_id = s.id
    FROM schools s
    WHERE decrypt_value(u.username) = decrypt_value(s.name);

    GET DIAGNOSTICS v_migrated_count = ROW_COUNT;
    v_migration_status := jsonb_set(v_migration_status, '{school_users_updated}', to_jsonb(v_migrated_count));

    UPDATE users u
    SET
        entity_type = 'TUTOR',
        entity_id = t.id
    FROM tutors t
    WHERE decrypt_value(u.username) = decrypt_value(t.name);

    GET DIAGNOSTICS v_migrated_count = ROW_COUNT;
    v_migration_status := jsonb_set(v_migration_status, '{tutor_users_updated}', to_jsonb(v_migrated_count));

    -- 3. Migrar datos de los campos TEXT a VARCHAR con los límites correctos
    -- Schools
    ALTER TABLE schools
        ALTER COLUMN name TYPE VARCHAR(50),
        ALTER COLUMN phone TYPE VARCHAR(20),
        ALTER COLUMN address TYPE VARCHAR(50),
        ALTER COLUMN state TYPE VARCHAR(20),
        ALTER COLUMN country TYPE VARCHAR(5);

    -- Tutors
    ALTER TABLE tutors
        ALTER COLUMN name TYPE VARCHAR(50),
        ALTER COLUMN phone TYPE VARCHAR(20),
        ALTER COLUMN email TYPE VARCHAR(50);

    -- Students
    ALTER TABLE students
        ALTER COLUMN name TYPE VARCHAR(50);

    -- 4. Eliminar tablas obsoletas
    DROP TABLE IF EXISTS conversations CASCADE;
    DROP TABLE IF EXISTS tutor_student CASCADE;

    -- Registrar finalización de la migración
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    )
    VALUES (
        'INFO',
        'MIGRATION',
        'Migración completada exitosamente',
        jsonb_build_object(
            'duration', EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - v_start_time)),
            'statistics', v_migration_status
        )
    );

EXCEPTION WHEN OTHERS THEN
    -- Registrar error en la migración
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    )
    VALUES (
        'ERROR',
        'MIGRATION',
        'Error durante la migración',
        jsonb_build_object(
            'error', SQLERRM,
            'state', SQLSTATE,
            'statistics', v_migration_status
        )
    );
    RAISE;
END;
$$;

-- Procedimiento para verificar la integridad después de la migración
CREATE OR REPLACE PROCEDURE verify_migration()
LANGUAGE plpgsql AS $$
DECLARE
    v_verification_results jsonb;
BEGIN
    v_verification_results := '{}';

    -- Verificar que todos los mensajes tienen las referencias correctas
    SELECT jsonb_build_object(
        'total_messages', COUNT(*),
        'invalid_student_refs', COUNT(*) FILTER (WHERE student_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM students s WHERE s.id = student_id)),
        'invalid_school_refs', COUNT(*) FILTER (WHERE school_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM schools s WHERE s.id = school_id)),
        'invalid_tutor_refs', COUNT(*) FILTER (WHERE tutor_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM tutors t WHERE t.id = tutor_id))
    )
    INTO v_verification_results
    FROM messages;

    -- Verificar que todos los usuarios tienen entity_type y entity_id válidos
    WITH user_verification AS (
        SELECT
            COUNT(*) as total_users,
            COUNT(*) FILTER (WHERE entity_type IS NULL OR entity_id IS NULL) as missing_entity,
            COUNT(*) FILTER (
                WHERE entity_type = 'SCHOOL' AND NOT EXISTS (
                    SELECT 1 FROM schools s WHERE s.id = entity_id
                )
            ) as invalid_school_refs,
            COUNT(*) FILTER (
                WHERE entity_type = 'TUTOR' AND NOT EXISTS (
                    SELECT 1 FROM tutors t WHERE t.id = entity_id
                )
            ) as invalid_tutor_refs
        FROM users
    )
    SELECT jsonb_build_object(
        'user_verification', jsonb_build_object(
            'total_users', total_users,
            'missing_entity', missing_entity,
            'invalid_school_refs', invalid_school_refs,
            'invalid_tutor_refs', invalid_tutor_refs
        )
    )
    INTO v_verification_results
    FROM user_verification;

    -- Registrar resultados de la verificación
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    )
    VALUES (
        CASE
            WHEN (v_verification_results->>'invalid_refs')::int > 0 THEN 'WARNING'
            ELSE 'INFO'
        END,
        'MIGRATION',
        'Verificación de migración completada',
        v_verification_results
    );
END;
$$;

-- Procedimiento para rollback de la migración
CREATE OR REPLACE PROCEDURE rollback_migration()
LANGUAGE plpgsql AS $$
BEGIN
    -- Restaurar tablas eliminadas
    CREATE TABLE IF NOT EXISTS conversations (
        -- estructura original
    );

    CREATE TABLE IF NOT EXISTS tutor_student (
        -- estructura original
    );

    -- Restaurar tipos de datos originales
    ALTER TABLE schools
        ALTER COLUMN name TYPE TEXT,
        ALTER COLUMN phone TYPE TEXT,
        ALTER COLUMN address TYPE TEXT,
        ALTER COLUMN country TYPE TEXT;

    -- Similar para otras tablas...

    -- Limpiar campos nuevos
    ALTER TABLE users
        DROP COLUMN IF EXISTS entity_type,
        DROP COLUMN IF EXISTS entity_id;

    -- Registrar rollback
    INSERT INTO system_notifications (
        level,
        category,
        message
    )
    VALUES (
        'WARNING',
        'MIGRATION',
        'Rollback de migración completado'
    );
END;
$$;