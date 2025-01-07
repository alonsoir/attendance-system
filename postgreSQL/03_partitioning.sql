-- Funciones de mantenimiento de particiones
CREATE OR REPLACE FUNCTION create_messages_partition(start_date DATE, end_date DATE)
RETURNS void AS $$
DECLARE
    partition_name TEXT;
BEGIN
    partition_name := 'messages_y' ||
                     to_char(start_date, 'YYYY') ||
                     'm' ||
                     to_char(start_date, 'MM');

    -- Verificar si la partición ya existe
    IF NOT EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = partition_name
        AND n.nspname = 'public'
    ) THEN
        -- Crear la partición
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF messages
            FOR VALUES FROM (%L) TO (%L)',
            partition_name,
            start_date,
            end_date
        );

        -- Crear los mismos índices que la tabla principal
        EXECUTE format(
            'CREATE INDEX %I ON %I (claude_conversation_id)',
            'idx_' || partition_name || '_claude_conv_id',
            partition_name
        );

        EXECUTE format(
            'CREATE INDEX %I ON %I (student_id)',
            'idx_' || partition_name || '_student_id',
            partition_name
        );

        EXECUTE format(
            'CREATE INDEX %I ON %I (school_id)',
            'idx_' || partition_name || '_school_id',
            partition_name
        );

        EXECUTE format(
            'CREATE INDEX %I ON %I (created_at)',
            'idx_' || partition_name || '_created_at',
            partition_name
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Función principal de mantenimiento de particiones
CREATE OR REPLACE PROCEDURE maintain_message_partitions()
LANGUAGE plpgsql
AS $$
DECLARE
    current_month DATE;
    next_month DATE;
    prev_month DATE;
BEGIN
    -- Obtener fechas relevantes
    current_month := date_trunc('month', CURRENT_DATE);
    next_month := current_month + interval '1 month';
    prev_month := current_month - interval '1 month';

    -- Crear particiones para el mes anterior, actual y siguiente
    PERFORM create_messages_partition(prev_month, current_month);
    PERFORM create_messages_partition(current_month, next_month);
    PERFORM create_messages_partition(next_month, next_month + interval '1 month');

    -- Registrar la actividad
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    ) VALUES (
        'INFO',
        'SYSTEM',
        'Mantenimiento de particiones completado',
        jsonb_build_object(
            'months_maintained', jsonb_build_array(
                to_char(prev_month, 'YYYY-MM'),
                to_char(current_month, 'YYYY-MM'),
                to_char(next_month, 'YYYY-MM')
            )
        )
    );

EXCEPTION WHEN OTHERS THEN
    -- Registrar cualquier error
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    ) VALUES (
        'ERROR',
        'SYSTEM',
        'Error en mantenimiento de particiones',
        jsonb_build_object(
            'error', SQLERRM,
            'detail', SQLSTATE
        )
    );
    RAISE;
END;
$$;

-- Tabla para mensajes archivados
CREATE TABLE archived_messages (
    LIKE messages INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- Función para archivar mensajes antiguos
CREATE OR REPLACE PROCEDURE archive_old_messages(
    p_months_old INT DEFAULT 12
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_cutoff_date DATE;
    v_partition_name TEXT;
BEGIN
    -- Calcular la fecha de corte
    v_cutoff_date := date_trunc('month', CURRENT_DATE - (p_months_old || ' months')::interval);

    -- Mover los mensajes antiguos a la tabla de archivo
    INSERT INTO archived_messages
    SELECT *
    FROM messages
    WHERE created_at < v_cutoff_date;

    -- Eliminar los mensajes archivados de la tabla principal
    DELETE FROM messages
    WHERE created_at < v_cutoff_date;

    -- Registrar la actividad
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    ) VALUES (
        'INFO',
        'SYSTEM',
        'Archivado de mensajes completado',
        jsonb_build_object(
            'cutoff_date', v_cutoff_date,
            'months_old', p_months_old
        )
    );

EXCEPTION WHEN OTHERS THEN
    -- Registrar cualquier error
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    ) VALUES (
        'ERROR',
        'SYSTEM',
        'Error en archivado de mensajes',
        jsonb_build_object(
            'error', SQLERRM,
            'detail', SQLSTATE
        )
    );
    RAISE;
END;
$$;

-- Programar las tareas de mantenimiento con pg_cron
SELECT cron.schedule('maintain-partitions', '0 0 * * *', 'CALL maintain_message_partitions()');
SELECT cron.schedule('archive-messages', '0 1 1 * *', 'CALL archive_old_messages(12)');

-- Crear las particiones iniciales
CALL maintain_message_partitions();