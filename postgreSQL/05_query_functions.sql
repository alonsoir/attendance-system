-- Funciones de consulta básicas
CREATE OR REPLACE FUNCTION get_school_details(p_id UUID)
RETURNS TABLE (
    id UUID,
    name VARCHAR(50),
    phone VARCHAR(20),
    address VARCHAR(50),
    state VARCHAR(20),
    country VARCHAR(5),
    created_at TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    updated_at TIMESTAMP WITH TIME ZONE,
    updated_by UUID
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        decrypt_value(s.name)::VARCHAR(50),
        decrypt_value(s.phone)::VARCHAR(20),
        decrypt_value(s.address)::VARCHAR(50),
        s.state,
        s.country,
        s.created_at,
        s.created_by,
        s.updated_at,
        s.updated_by
    FROM schools s
    WHERE s.id = p_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_tutor_details(p_id UUID)
RETURNS TABLE (
    id UUID,
    name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    updated_at TIMESTAMP WITH TIME ZONE,
    updated_by UUID
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        decrypt_value(t.name)::VARCHAR(50),
        decrypt_value(t.phone)::VARCHAR(20),
        decrypt_value(t.email)::VARCHAR(50),
        t.created_at,
        t.created_by,
        t.updated_at,
        t.updated_by
    FROM tutors t
    WHERE t.id = p_id;
END;
$$;

CREATE OR REPLACE FUNCTION get_student_details(p_id UUID)
RETURNS TABLE (
    id UUID,
    name VARCHAR(50),
    date_of_birth DATE,
    school_id UUID,
    school_name VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE,
    created_by UUID,
    updated_at TIMESTAMP WITH TIME ZONE,
    updated_by UUID
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id,
        decrypt_value(s.name)::VARCHAR(50),
        s.date_of_birth,
        s.school_id,
        decrypt_value(sc.name)::VARCHAR(50),
        s.created_at,
        s.created_by,
        s.updated_at,
        s.updated_by
    FROM students s
    LEFT JOIN schools sc ON s.school_id = sc.id
    WHERE s.id = p_id;
END;
$$;

-- Funciones de consulta de mensajes
CREATE OR REPLACE FUNCTION get_student_messages(
    p_student_id UUID,
    p_from_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_to_date TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    claude_conversation_id VARCHAR(50),
    sender_type sender_type_enum,
    sender_name VARCHAR(50),
    content VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE,
    created_by UUID
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.claude_conversation_id,
        m.sender_type,
        CASE m.sender_type
            WHEN 'SCHOOL' THEN decrypt_value(s.name)::VARCHAR(50)
            WHEN 'TUTOR' THEN decrypt_value(t.name)::VARCHAR(50)
            WHEN 'CLAUDE' THEN 'Claude'
        END,
        decrypt_value(m.content)::VARCHAR(1000),
        m.created_at,
        m.created_by
    FROM messages m
    LEFT JOIN schools s ON m.school_id = s.id
    LEFT JOIN tutors t ON m.tutor_id = t.id
    WHERE m.student_id = p_student_id
    AND (p_from_date IS NULL OR m.created_at >= p_from_date)
    AND (p_to_date IS NULL OR m.created_at <= p_to_date)
    ORDER BY m.created_at DESC;
END;
$$;

-- Función para obtener conversaciones por ID de Claude
CREATE OR REPLACE FUNCTION get_conversation_by_claude_id(
    p_claude_conversation_id VARCHAR(50)
)
RETURNS TABLE (
    id UUID,
    student_name VARCHAR(50),
    school_name VARCHAR(50),
    tutor_name VARCHAR(50),
    sender_type sender_type_enum,
    content VARCHAR(1000),
    created_at TIMESTAMP WITH TIME ZONE
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        decrypt_value(st.name)::VARCHAR(50) as student_name,
        decrypt_value(s.name)::VARCHAR(50) as school_name,
        decrypt_value(t.name)::VARCHAR(50) as tutor_name,
        m.sender_type,
        decrypt_value(m.content)::VARCHAR(1000),
        m.created_at
    FROM messages m
    LEFT JOIN students st ON m.student_id = st.id
    LEFT JOIN schools s ON m.school_id = s.id
    LEFT JOIN tutors t ON m.tutor_id = t.id
    WHERE m.claude_conversation_id = p_claude_conversation_id
    ORDER BY m.created_at ASC;
END;
$$;

-- Función para búsqueda de mensajes por contenido
CREATE OR REPLACE FUNCTION search_messages(
    p_search_text VARCHAR(100),
    p_student_id UUID DEFAULT NULL,
    p_school_id UUID DEFAULT NULL,
    p_tutor_id UUID DEFAULT NULL,
    p_from_date TIMESTAMP WITH TIME ZONE DEFAULT NULL,
    p_to_date TIMESTAMP WITH TIME ZONE DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    claude_conversation_id VARCHAR(50),
    student_name VARCHAR(50),
    sender_type sender_type_enum,
    content_preview VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.claude_conversation_id,
        decrypt_value(st.name)::VARCHAR(50),
        m.sender_type,
        substring(decrypt_value(m.content)::VARCHAR(1000) from 1 for 100),
        m.created_at
    FROM messages m
    JOIN students st ON m.student_id = st.id
    WHERE
        (decrypt_value(m.content) ILIKE '%' || p_search_text || '%')
        AND (p_student_id IS NULL OR m.student_id = p_student_id)
        AND (p_school_id IS NULL OR m.school_id = p_school_id)
        AND (p_tutor_id IS NULL OR m.tutor_id = p_tutor_id)
        AND (p_from_date IS NULL OR m.created_at >= p_from_date)
        AND (p_to_date IS NULL OR m.created_at <= p_to_date)
    ORDER BY m.created_at DESC;
END;
$$;

-- Función para estadísticas de uso
CREATE OR REPLACE FUNCTION get_usage_statistics(
    p_from_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    p_to_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    date DATE,
    total_messages BIGINT,
    claude_messages BIGINT,
    school_messages BIGINT,
    tutor_messages BIGINT,
    unique_students BIGINT,
    unique_conversations BIGINT
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        DATE(m.created_at) as date,
        COUNT(*) as total_messages,
        COUNT(*) FILTER (WHERE sender_type = 'CLAUDE') as claude_messages,
        COUNT(*) FILTER (WHERE sender_type = 'SCHOOL') as school_messages,
        COUNT(*) FILTER (WHERE sender_type = 'TUTOR') as tutor_messages,
        COUNT(DISTINCT student_id) as unique_students,
        COUNT(DISTINCT claude_conversation_id) as unique_conversations
    FROM messages m
    WHERE m.created_at >= p_from_date
    AND m.created_at < p_to_date
    GROUP BY DATE(m.created_at)
    ORDER BY DATE(m.created_at);
END;
$$;