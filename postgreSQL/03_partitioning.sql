-- Function to create message partitions
CREATE OR REPLACE FUNCTION create_messages_partition(start_date TIMESTAMP WITH TIME ZONE, end_date TIMESTAMP WITH TIME ZONE)
RETURNS void AS $$
DECLARE
    partition_name TEXT;
BEGIN
    partition_name := 'messages_y' ||
                     to_char(start_date, 'YYYY') ||
                     'm' ||
                     to_char(start_date, 'MM');

    IF NOT EXISTS (
        SELECT 1
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = partition_name
        AND n.nspname = 'public'
    ) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF messages
            FOR VALUES FROM (%L) TO (%L)',
            partition_name,
            start_date,
            end_date
        );

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

-- Procedure to maintain message partitions
CREATE OR REPLACE PROCEDURE maintain_message_partitions()
LANGUAGE plpgsql
AS $$
DECLARE
    current_month DATE;
    next_month DATE;
    prev_month DATE;
BEGIN
    current_month := date_trunc('month', CURRENT_DATE);
    next_month := current_month + interval '1 month';
    prev_month := current_month - interval '1 month';

    PERFORM create_messages_partition(prev_month::TIMESTAMP WITH TIME ZONE, current_month::TIMESTAMP WITH TIME ZONE);
    PERFORM create_messages_partition(current_month::TIMESTAMP WITH TIME ZONE, next_month::TIMESTAMP WITH TIME ZONE);
    PERFORM create_messages_partition(next_month::TIMESTAMP WITH TIME ZONE, (next_month + interval '1 month')::TIMESTAMP WITH TIME ZONE);

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

-- Schedule maintenance procedures with pg_cron
SELECT cron.schedule('maintain-partitions', '0 0 * * *', 'CALL maintain_message_partitions()');
SELECT cron.schedule('archive-messages', '0 1 1 * *', 'CALL archive_old_messages(12)');

-- Call the maintenance procedure
CALL maintain_message_partitions();