-- Procedimiento para limpiar mensajes antiguos
CREATE OR REPLACE PROCEDURE cleanup_old_messages(
    p_months_old INT DEFAULT 12,
    p_batch_size INT DEFAULT 1000
)
LANGUAGE plpgsql AS $$
DECLARE
    v_cutoff_date TIMESTAMP WITH TIME ZONE;
    v_deleted_count INT := 0;
    v_batch_count INT;
BEGIN
    v_cutoff_date := CURRENT_TIMESTAMP - (p_months_old || ' months')::INTERVAL;

    LOOP
        -- Mover mensajes antiguos a la tabla de archivo en lotes
        WITH batch AS (
            SELECT id
            FROM messages
            WHERE created_at < v_cutoff_date
            LIMIT p_batch_size
            FOR UPDATE SKIP LOCKED
        )
        INSERT INTO archived_messages
        SELECT m.*
        FROM messages m
        JOIN batch b ON m.id = b.id
        RETURNING 1 INTO v_batch_count;

        -- Si no hay más registros para procesar, salir del loop
        IF v_batch_count IS NULL THEN
            EXIT;
        END IF;

        -- Eliminar los mensajes que fueron archivados
        DELETE FROM messages m
        USING archived_messages a
        WHERE m.id = a.id;

        v_deleted_count := v_deleted_count + v_batch_count;

        -- Registrar progreso
        INSERT INTO system_notifications (
            level,
            category,
            message,
            details
        ) VALUES (
            'INFO',
            'SYSTEM',
            'Progreso de limpieza de mensajes',
            jsonb_build_object(
                'batch_processed', v_batch_count,
                'total_processed', v_deleted_count,
                'cutoff_date', v_cutoff_date
            )
        );

        -- Pequeña pausa para no sobrecargar el sistema
        PERFORM pg_sleep(0.1);
    END LOOP;

    -- Registrar finalización
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    ) VALUES (
        'INFO',
        'SYSTEM',
        'Limpieza de mensajes completada',
        jsonb_build_object(
            'total_archived', v_deleted_count,
            'cutoff_date', v_cutoff_date,
            'months_old', p_months_old
        )
    );
END;
$$;

-- Procedimiento para limpiar notificaciones antiguas
CREATE OR REPLACE PROCEDURE cleanup_old_notifications(
    p_days_old INT DEFAULT 30
)
LANGUAGE plpgsql AS $$
DECLARE
    v_cutoff_date TIMESTAMP WITH TIME ZONE;
    v_deleted_count INT;
BEGIN
    v_cutoff_date := CURRENT_TIMESTAMP - (p_days_old || ' days')::INTERVAL;

    DELETE FROM system_notifications
    WHERE created_at < v_cutoff_date
    AND (acknowledged = true OR level = 'INFO')
    RETURNING COUNT(*) INTO v_deleted_count;

    -- Registrar la limpieza
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    ) VALUES (
        'INFO',
        'SYSTEM',
        'Limpieza de notificaciones completada',
        jsonb_build_object(
            'notifications_deleted', v_deleted_count,
            'cutoff_date', v_cutoff_date,
            'days_old', p_days_old
        )
    );
END;
$$;

-- Procedimiento para verificar la integridad de las referencias
CREATE OR REPLACE PROCEDURE check_data_integrity()
LANGUAGE plpgsql AS $$
DECLARE
    v_orphaned_messages INT;
    v_orphaned_students INT;
BEGIN
    -- Verificar mensajes huérfanos
    SELECT COUNT(*) INTO v_orphaned_messages
    FROM messages m
    LEFT JOIN students s ON m.student_id = s.id
    WHERE m.student_id IS NOT NULL
    AND s.id IS NULL;

    IF v_orphaned_messages > 0 THEN
        INSERT INTO system_notifications (
            level,
            category,
            message,
            details
        ) VALUES (
            'WARNING',
            'DATA_INTEGRITY',
            'Se encontraron mensajes con referencias inválidas',
            jsonb_build_object('orphaned_messages', v_orphaned_messages)
        );
    END IF;

    -- Verificar estudiantes huérfanos
    SELECT COUNT(*) INTO v_orphaned_students
    FROM students s
    LEFT JOIN schools sc ON s.school_id = sc.id
    WHERE s.school_id IS NOT NULL
    AND sc.id IS NULL;

    IF v_orphaned_students > 0 THEN
        INSERT INTO system_notifications (
            level,
            category,
            message,
            details
        ) VALUES (
            'WARNING',
            'DATA_INTEGRITY',
            'Se encontraron estudiantes con referencias inválidas',
            jsonb_build_object('orphaned_students', v_orphaned_students)
        );
    END IF;
END;
$$;

-- Procedimiento para realizar mantenimiento general
CREATE OR REPLACE PROCEDURE perform_system_maintenance()
LANGUAGE plpgsql AS $$
BEGIN
    -- Ejecutar todos los procedimientos de mantenimiento
    CALL cleanup_old_messages();
    CALL cleanup_old_notifications();
    CALL check_data_integrity();
    CALL maintain_message_partitions();

    -- Actualizar estadísticas de PostgreSQL
    ANALYZE messages;
    ANALYZE archived_messages;
    ANALYZE system_notifications;

    -- Registrar el mantenimiento completo
    INSERT INTO system_notifications (
        level,
        category,
        message
    ) VALUES (
        'INFO',
        'SYSTEM',
        'Mantenimiento general del sistema completado'
    );
END;
$$;

-- Programar tareas de mantenimiento
SELECT cron.schedule(
    'daily-maintenance',
    '0 2 * * *',  -- 2 AM todos los días
    'CALL perform_system_maintenance()'
);

SELECT cron.schedule(
    'integrity-check',
    '0 */4 * * *',  -- Cada 4 horas
    'CALL check_data_integrity()'
);