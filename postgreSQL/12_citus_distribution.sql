-- 12_citus_distribution.sql

CREATE TEMP TABLE temp_messages AS SELECT * FROM messages;
TRUNCATE messages CASCADE;

-- Verificar instalación de extensión Citus
CREATE EXTENSION IF NOT EXISTS citus;

-- Verificación previa de datos
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM messages LIMIT 1) THEN
    RAISE EXCEPTION 'La tabla messages debe estar vacía antes de la distribución.';
  END IF;
END $$;

-- 1. Eliminar foreign keys
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_school_id_fkey;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_student_id_fkey;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_tutor_id_fkey;
ALTER TABLE students DROP CONSTRAINT IF EXISTS students_school_id_fkey;
ALTER TABLE tutors DROP CONSTRAINT IF EXISTS tutors_school_id_fkey;

-- 2. Eliminar y reconfigurar primary keys
ALTER TABLE students DROP CONSTRAINT IF EXISTS students_pkey;
ALTER TABLE students ALTER COLUMN school_id SET NOT NULL;
ALTER TABLE students ADD PRIMARY KEY (id, school_id);

ALTER TABLE tutors DROP CONSTRAINT IF EXISTS tutors_pkey;
ALTER TABLE tutors ALTER COLUMN school_id SET NOT NULL;
ALTER TABLE tutors ADD PRIMARY KEY (id, school_id);

ALTER TABLE messages DROP CONSTRAINT IF EXISTS unique_id;
ALTER TABLE messages ALTER COLUMN school_id SET NOT NULL;
ALTER TABLE messages ADD PRIMARY KEY (id, school_id, created_at);

-- 3. Distribuir las tablas
-- Primero schools como tabla de referencia
SELECT create_reference_table('schools');

-- Luego students como tabla base para colocalización
SELECT create_distributed_table('students', 'school_id');

-- Después tutors colocada con students
SELECT create_distributed_table('tutors', 'school_id', colocate_with => 'students');

-- Messages y sus particiones
SELECT create_distributed_table('messages', 'school_id', colocate_with => 'students');
SELECT create_distributed_table('messages_y2024m12', 'school_id', colocate_with => 'students');
SELECT create_distributed_table('messages_y2025m01', 'school_id', colocate_with => 'students');
SELECT create_distributed_table('messages_y2025m02', 'school_id', colocate_with => 'students');

-- 4. Recrear foreign keys
ALTER TABLE students ADD CONSTRAINT students_school_id_fkey
   FOREIGN KEY (school_id) REFERENCES schools(id);

ALTER TABLE tutors ADD CONSTRAINT tutors_school_id_fkey
   FOREIGN KEY (school_id) REFERENCES schools(id);

ALTER TABLE messages ADD CONSTRAINT messages_school_id_fkey
   FOREIGN KEY (school_id) REFERENCES schools(id);
ALTER TABLE messages ADD CONSTRAINT messages_student_id_fkey
   FOREIGN KEY (student_id) REFERENCES students(id);
ALTER TABLE messages ADD CONSTRAINT messages_tutor_id_fkey
   FOREIGN KEY (tutor_id) REFERENCES tutors(id);

-- 5. Configuración de Citus
ALTER DATABASE test_db SET citus.enable_repartition_joins TO ON;

-- 6. Limpiar datos locales después de la distribución
SELECT truncate_local_data_after_distributing_table('public.schools');
SELECT truncate_local_data_after_distributing_table('public.students');
SELECT truncate_local_data_after_distributing_table('public.tutors');
SELECT truncate_local_data_after_distributing_table('public.messages');
SELECT truncate_local_data_after_distributing_table('public.messages_y2024m12');
SELECT truncate_local_data_after_distributing_table('public.messages_y2025m01');
SELECT truncate_local_data_after_distributing_table('public.messages_y2025m02');

-- 7. Verificaciones finales
DO $$
DECLARE
   table_count int;
BEGIN
   -- Verificar que todas las tablas están distribuidas
   SELECT COUNT(*) INTO table_count
   FROM pg_dist_partition
   WHERE logicalrelid::text IN ('schools', 'students', 'tutors', 'messages');

   IF table_count < 4 THEN
       RAISE EXCEPTION 'No todas las tablas están distribuidas correctamente';
   END IF;

   -- Verificar colocalización
   IF NOT EXISTS (
       SELECT 1
       FROM pg_dist_partition
       WHERE logicalrelid::text IN ('students', 'tutors', 'messages')
       GROUP BY colocationid
       HAVING COUNT(*) = 3
   ) THEN
       RAISE EXCEPTION 'Las tablas no están colocadas correctamente';
   END IF;
END $$;

-- Mostrar estado final de la distribución
SELECT logicalrelid::regclass as table_name,
      partmethod,
      colocationid
FROM pg_dist_partition
WHERE logicalrelid::text LIKE 'messages%'
  OR logicalrelid::text IN ('schools', 'students', 'tutors')
ORDER BY table_name;

INSERT INTO messages SELECT * FROM temp_messages;
DROP TABLE temp_messages;