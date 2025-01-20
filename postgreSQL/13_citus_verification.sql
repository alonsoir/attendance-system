-- 13_citus_verification.sql

-- Función de ayuda para logging
CREATE OR REPLACE FUNCTION log_test_result(test_name text, result text) RETURNS void AS $$
BEGIN
    RAISE NOTICE 'Test %: %', test_name, result;
END;
$$ LANGUAGE plpgsql;

-- 1. Pruebas de inserción
DO $$
DECLARE
    school_id uuid;
    student_id uuid;
    tutor_id uuid;
BEGIN
    -- Insertar nueva escuela
    INSERT INTO schools (name, state, country)
    VALUES ('Escuela Test Citus', 'Madrid', 'ES')
    RETURNING id INTO school_id;

    -- Insertar estudiante
    INSERT INTO students (name, school_id)
    VALUES ('Estudiante Test Citus', school_id)
    RETURNING id INTO student_id;

    -- Insertar tutor
    INSERT INTO tutors (name, email, school_id)
    VALUES ('Tutor Test Citus', 'tutor@test.com', school_id)
    RETURNING id INTO tutor_id;

    -- Insertar mensajes en diferentes particiones
    INSERT INTO messages (claude_conversation_id, student_id, school_id, tutor_id, sender_type, content, created_at)
    VALUES
        ('test-conv-1', student_id, school_id, tutor_id, 'TUTOR', 'Mensaje test 1', '2024-12-15T10:00:00Z'),
        ('test-conv-2', student_id, school_id, tutor_id, 'STUDENT', 'Mensaje test 2', '2025-01-15T10:00:00Z'),
        ('test-conv-3', student_id, school_id, tutor_id, 'CLAUDE', 'Mensaje test 3', '2025-02-15T10:00:00Z');

    PERFORM log_test_result('Inserción de datos', 'OK');
EXCEPTION WHEN OTHERS THEN
    PERFORM log_test_result('Inserción de datos', 'ERROR: ' || SQLERRM);
    RAISE;
END $$;

-- 2. Pruebas de SELECT
DO $$
BEGIN
    -- Test 1: Consulta simple por escuela
    EXPLAIN ANALYZE
    SELECT s.name as school_name, COUNT(m.*) as message_count
    FROM schools s
    LEFT JOIN messages m ON m.school_id = s.id
    GROUP BY s.id, s.name;

    PERFORM log_test_result('Consulta agrupada por escuela', 'OK');

    -- Test 2: Join complejo con todas las tablas
    EXPLAIN ANALYZE
    SELECT
        s.name as school_name,
        st.name as student_name,
        t.name as tutor_name,
        m.content,
        m.created_at
    FROM messages m
    JOIN schools s ON s.id = m.school_id
    JOIN students st ON st.id = m.student_id
    JOIN tutors t ON t.id = m.tutor_id
    WHERE m.created_at >= '2024-12-01'
    ORDER BY m.created_at DESC
    LIMIT 10;

    PERFORM log_test_result('Join complejo', 'OK');

EXCEPTION WHEN OTHERS THEN
    PERFORM log_test_result('Consultas SELECT', 'ERROR: ' || SQLERRM);
    RAISE;
END $$;

-- 3. Pruebas de UPDATE
DO $$
DECLARE
    test_school_id uuid;
BEGIN
    -- Obtener una escuela de prueba
    SELECT id INTO test_school_id FROM schools WHERE name = 'Escuela Test Citus';

    -- Update en una tabla de referencia
    UPDATE schools
    SET phone = '123456789'
    WHERE id = test_school_id;

    -- Update en una tabla distribuida
    UPDATE students
    SET updated_at = CURRENT_TIMESTAMP
    WHERE school_id = test_school_id;

    -- Update en tabla particionada
    UPDATE messages
    SET content = content || ' (actualizado)'
    WHERE school_id = test_school_id;

    PERFORM log_test_result('Operaciones UPDATE', 'OK');
EXCEPTION WHEN OTHERS THEN
    PERFORM log_test_result('Operaciones UPDATE', 'ERROR: ' || SQLERRM);
    RAISE;
END $$;

-- 4. Pruebas de DELETE
DO $$
DECLARE
    test_school_id uuid;
BEGIN
    -- Obtener la escuela de prueba
    SELECT id INTO test_school_id FROM schools WHERE name = 'Escuela Test Citus';

    -- Eliminar mensajes
    DELETE FROM messages WHERE school_id = test_school_id;

    -- Eliminar estudiantes
    DELETE FROM students WHERE school_id = test_school_id;

    -- Eliminar tutores
    DELETE FROM tutors WHERE school_id = test_school_id;

    -- Eliminar escuela
    DELETE FROM schools WHERE id = test_school_id;

    PERFORM log_test_result('Operaciones DELETE', 'OK');
EXCEPTION WHEN OTHERS THEN
    PERFORM log_test_result('Operaciones DELETE', 'ERROR: ' || SQLERRM);
    RAISE;
END $$;

-- 5. Verificación de distribución de datos
SELECT
    tableoid::regclass as table_name,
    COUNT(*) as row_count
FROM messages
GROUP BY tableoid
ORDER BY table_name;

-- 6. Verificación de rendimiento de joins
EXPLAIN ANALYZE
SELECT
    date_trunc('month', m.created_at) as month,
    s.name as school_name,
    COUNT(DISTINCT st.id) as num_students,
    COUNT(DISTINCT t.id) as num_tutors,
    COUNT(*) as num_messages
FROM messages m
JOIN schools s ON s.id = m.school_id
JOIN students st ON st.id = m.student_id
JOIN tutors t ON t.id = m.tutor_id
GROUP BY date_trunc('month', m.created_at), s.name
ORDER BY month;

-- 7. Validar estado de los workers
SELECT * FROM citus_get_active_worker_nodes();

-- 8. Verificar distribución de shards
SELECT
    logicalrelid::regclass as table_name,
    COUNT(DISTINCT shardid) as num_shards
FROM pg_dist_shard
GROUP BY logicalrelid
ORDER BY table_name;