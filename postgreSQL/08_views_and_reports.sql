-- Vista de resumen de actividad por escuela
CREATE OR REPLACE VIEW school_activity_summary AS
SELECT
    s.id as school_id,
    decrypt_value(s.name)::VARCHAR(50) as school_name,
    s.state,
    s.country,
    COUNT(DISTINCT st.id) as total_students,
    COUNT(DISTINCT m.claude_conversation_id) as total_conversations,
    COUNT(m.id) as total_messages,
    COUNT(m.id) FILTER (WHERE m.sender_type = 'CLAUDE') as claude_messages,
    COUNT(m.id) FILTER (WHERE m.sender_type = 'SCHOOL') as school_messages,
    COUNT(m.id) FILTER (WHERE m.sender_type = 'TUTOR') as tutor_messages,
    MIN(m.created_at) as first_message_date,
    MAX(m.created_at) as last_message_date
FROM schools s
LEFT JOIN students st ON s.id = st.school_id
LEFT JOIN messages m ON st.id = m.student_id
GROUP BY s.id, s.name, s.state, s.country;

-- Vista de actividad de tutores
CREATE OR REPLACE VIEW tutor_activity_summary AS
SELECT
    t.id as tutor_id,
    decrypt_value(t.name)::VARCHAR(50) as tutor_name,
    COUNT(DISTINCT m.student_id) as students_attended,
    COUNT(DISTINCT m.claude_conversation_id) as total_conversations,
    COUNT(m.id) as total_messages,
    COUNT(DISTINCT s.id) as schools_involved,
    MIN(m.created_at) as first_interaction,
    MAX(m.created_at) as last_interaction
FROM tutors t
LEFT JOIN messages m ON t.id = m.tutor_id
LEFT JOIN students st ON m.student_id = st.id
LEFT JOIN schools s ON st.school_id = s.id
GROUP BY t.id, t.name;

-- Vista de estudiantes activos
CREATE OR REPLACE VIEW active_students AS
SELECT
    st.id as student_id,
    decrypt_value(st.name)::VARCHAR(50) as student_name,
    st.date_of_birth,
    decrypt_value(s.name)::VARCHAR(50) as school_name,
    COUNT(DISTINCT m.claude_conversation_id) as total_conversations,
    COUNT(m.id) as total_messages,
    MAX(m.created_at) as last_activity
FROM students st
JOIN schools s ON st.school_id = s.id
LEFT JOIN messages m ON st.id = m.student_id
GROUP BY st.id, st.name, st.date_of_birth, s.name
HAVING MAX(m.created_at) > CURRENT_TIMESTAMP - INTERVAL '30 days';

-- Función para reporte de uso mensual
CREATE OR REPLACE FUNCTION generate_monthly_report(
    p_year INT,
    p_month INT
)
RETURNS TABLE (
    metric VARCHAR(50),
    value BIGINT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    WITH monthly_data AS (
        SELECT
            date_trunc('month', m.created_at) as month,
            COUNT(DISTINCT m.student_id) as active_students,
            COUNT(DISTINCT m.claude_conversation_id) as total_conversations,
            COUNT(m.id) as total_messages,
            COUNT(DISTINCT m.school_id) as active_schools,
            COUNT(DISTINCT m.tutor_id) as active_tutors
        FROM messages m
        WHERE EXTRACT(YEAR FROM m.created_at) = p_year
        AND EXTRACT(MONTH FROM m.created_at) = p_month
        GROUP BY date_trunc('month', m.created_at)
    )
    SELECT 'Estudiantes Activos'::VARCHAR(50), active_students FROM monthly_data
    UNION ALL
    SELECT 'Conversaciones Totales', total_conversations FROM monthly_data
    UNION ALL
    SELECT 'Mensajes Totales', total_messages FROM monthly_data
    UNION ALL
    SELECT 'Escuelas Activas', active_schools FROM monthly_data
    UNION ALL
    SELECT 'Tutores Activos', active_tutors FROM monthly_data;
END;
$$;

-- Función para reporte de tendencias
CREATE OR REPLACE FUNCTION get_usage_trends(
    p_months INT DEFAULT 6
)
RETURNS TABLE (
    month DATE,
    total_messages BIGINT,
    avg_messages_per_student NUMERIC,
    active_students BIGINT,
    new_students BIGINT
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    WITH monthly_stats AS (
        SELECT
            date_trunc('month', m.created_at)::DATE as month,
            COUNT(*) as messages,
            COUNT(DISTINCT m.student_id) as students,
            COUNT(DISTINCT
                CASE WHEN s.created_at >= date_trunc('month', m.created_at)
                     THEN s.id
                     END
            ) as new_students
        FROM messages m
        JOIN students s ON m.student_id = s.id
        WHERE m.created_at >= CURRENT_DATE - (p_months || ' months')::INTERVAL
        GROUP BY date_trunc('month', m.created_at)
    )
    SELECT
        month,
        messages as total_messages,
        ROUND(messages::NUMERIC / students, 2) as avg_messages_per_student,
        students as active_students,
        new_students
    FROM monthly_stats
    ORDER BY month DESC;
END;
$$;

-- Función para reporte de interacción Claude
CREATE OR REPLACE FUNCTION analyze_claude_interactions(
    p_days INT DEFAULT 30
)
RETURNS TABLE (
    metric VARCHAR(100),
    value NUMERIC
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT
            COUNT(*) FILTER (WHERE sender_type = 'CLAUDE') as claude_messages,
            COUNT(*) as total_messages,
            AVG(LENGTH(decrypt_value(content))) FILTER (WHERE sender_type = 'CLAUDE') as avg_claude_length,
            PERCENTILE_CONT(0.5) WITHIN GROUP (
                ORDER BY EXTRACT(EPOCH FROM
                    created_at - LAG(created_at) OVER (
                        PARTITION BY claude_conversation_id
                        ORDER BY created_at
                    )
                )
            ) FILTER (WHERE sender_type = 'CLAUDE') as median_response_time
        FROM messages
        WHERE created_at >= CURRENT_DATE - (p_days || ' days')::INTERVAL
    )
    SELECT 'Porcentaje de respuestas Claude'::VARCHAR(100),
           ROUND((claude_messages::NUMERIC / total_messages) * 100, 2)
    FROM stats
    UNION ALL
    SELECT 'Longitud promedio de respuesta', ROUND(avg_claude_length, 2)
    FROM stats
    UNION ALL
    SELECT 'Tiempo mediano de respuesta (segundos)', ROUND(median_response_time, 2)
    FROM stats;
END;
$$;