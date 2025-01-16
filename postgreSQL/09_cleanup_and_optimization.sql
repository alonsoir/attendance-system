-- Configuración de sistema y optimizaciones
CREATE OR REPLACE PROCEDURE setup_system_configuration()
LANGUAGE plpgsql AS $$
BEGIN
    -- Configuraciones del sistema
    INSERT INTO system_config (key, value, description) VALUES
    ('message_retention_months', '12', 'Tiempo en meses para mantener mensajes antes de archivar'),
    ('max_message_length', '1000', 'Longitud máxima permitida para mensajes'),
    ('notification_retention_days', '30', 'Días para mantener notificaciones del sistema'),
    ('maintenance_hour', '2', 'Hora del día (0-23) para ejecutar mantenimiento'),
    ('archive_batch_size', '1000', 'Tamaño del lote para operaciones de archivado')
    ON CONFLICT (key) DO UPDATE
    SET description = EXCLUDED.description;
END;
$$;

-- Optimización de tablas
CREATE OR REPLACE PROCEDURE optimize_tables()
LANGUAGE plpgsql AS $$
DECLARE
    v_table_name text;
BEGIN
    -- Registrar inicio
    INSERT INTO system_notifications (level, category, message)
    VALUES ('INFO', 'MAINTENANCE', 'Iniciando optimización de tablas');

    -- Lista de tablas principales a optimizar
    FOR v_table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename IN ('messages', 'archived_messages', 'students', 'schools', 'tutors')
    LOOP
        -- ANALYZE for each table
        EXECUTE 'ANALYZE ' || v_table_name;

        -- Registrar progreso
        INSERT INTO system_notifications (
            level,
            category,
            message,
            details
        ) VALUES (
            'INFO',
            'MAINTENANCE',
            'Tabla optimizada',
            jsonb_build_object('table', v_table_name)
        );
    END LOOP;
END;
$$;

-- Limpieza de datos redundantes o huérfanos
CREATE OR REPLACE PROCEDURE cleanup_orphaned_data()
LANGUAGE plpgsql AS $$
DECLARE
    v_deleted_count integer;
BEGIN
    -- Eliminar mensajes de estudiantes que ya no existen
    WITH deleted AS (
        DELETE FROM messages m
        WHERE NOT EXISTS (
            SELECT 1 FROM students s WHERE s.id = m.student_id
        )
        RETURNING id
    )
    SELECT COUNT(*) INTO v_deleted_count FROM deleted;

    IF v_deleted_count > 0 THEN
        INSERT INTO system_notifications (
            level,
            category,
            message,
            details
        ) VALUES (
            'WARNING',
            'DATA_INTEGRITY',
            'Mensajes huérfanos eliminados',
            jsonb_build_object('count', v_deleted_count)
        );
    END IF;

    -- Limpiar notificaciones antiguas procesadas
    DELETE FROM system_notifications
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '30 days'
    AND (acknowledged = true OR level = 'INFO');
END;
$$;

-- Mantenimiento de índices
CREATE OR REPLACE PROCEDURE maintain_indexes()
LANGUAGE plpgsql AS $$
DECLARE
    v_index_name text;
    v_table_name text;
    v_index_size bigint;
    v_index_scans bigint;
BEGIN
    FOR v_index_name, v_table_name, v_index_size, v_index_scans IN
        SELECT
            schemaname || '.' || indexrelname as index_name,
            schemaname || '.' || tablename as table_name,
            pg_relation_size(indexrelid) as index_size,
            idx_scan as index_scans
        FROM pg_stat_user_indexes
        WHERE schemaname = 'public'
    LOOP
        -- Registrar índices grandes pero poco utilizados
        IF v_index_size > 10 * 1024 * 1024 AND v_index_scans < 100 THEN
            INSERT INTO system_notifications (
                level,
                category,
                message,
                details
            ) VALUES (
                'WARNING',
                'PERFORMANCE',
                'Índice grande con poco uso detectado',
                jsonb_build_object(
                    'index_name', v_index_name,
                    'table_name', v_table_name,
                    'size_mb', v_index_size::numeric / (1024 * 1024),
                    'scans', v_index_scans
                )
            );
        END IF;

        -- REINDEX para mantenimiento
        BEGIN
            EXECUTE 'REINDEX INDEX ' || v_index_name;
        EXCEPTION WHEN OTHERS THEN
            INSERT INTO system_notifications (
                level,
                category,
                message,
                details
            ) VALUES (
                'ERROR',
                'MAINTENANCE',
                'Error al reindexar',
                jsonb_build_object(
                    'index_name', v_index_name,
                    'error', SQLERRM
                )
            );
        END;
    END LOOP;
END;
$$;

-- Actualización de estadísticas
CREATE OR REPLACE PROCEDURE update_table_statistics()
LANGUAGE plpgsql AS $$
DECLARE
    v_table_name text;
BEGIN
    FOR v_table_name IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'ANALYZE VERBOSE ' || v_table_name;
    END LOOP;
END;
$$;

-- Programar tareas de mantenimiento
SELECT cron.schedule(
    'daily-optimization',
    '0 2 * * *',  -- 2 AM todos los días
    $$
    BEGIN
        CALL optimize_tables();
        CALL cleanup_orphaned_data();
        CALL maintain_indexes();
        CALL update_table_statistics();
    END;
    $$
);

-- Inicialización inicial del sistema
DO $$
BEGIN
    -- Configurar sistema
    CALL setup_system_configuration();

    -- Ejecutar optimización inicial
    CALL optimize_tables();
    CALL update_table_statistics();

    -- Registrar inicialización
    INSERT INTO system_notifications (
        level,
        category,
        message
    ) VALUES (
        'INFO',
        'SYSTEM',
        'Sistema inicializado y optimizado'
    );
END;
$$;