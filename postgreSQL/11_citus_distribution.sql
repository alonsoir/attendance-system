-- 11_citus_distribution.sql
-- Verificar instalación de extensión Citus
CREATE EXTENSION IF NOT EXISTS citus;

-- 1. Primero, eliminar todas las foreign keys
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_school_id_fkey;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_student_id_fkey;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_tutor_id_fkey;
ALTER TABLE students DROP CONSTRAINT IF EXISTS students_school_id_fkey;
ALTER TABLE tutors DROP CONSTRAINT IF EXISTS tutors_school_id_fkey;

-- 2. Ahora sí, eliminar los triggers
DO $$
DECLARE
   trigger_rec record;
BEGIN
   FOR trigger_rec IN
       SELECT tgname::text as trigger_name,
              relname::text as table_name
       FROM pg_trigger t
       JOIN pg_class c ON t.tgrelid = c.oid
       WHERE relname LIKE 'messages%'
   LOOP
       EXECUTE format('DROP TRIGGER IF EXISTS %I ON %I',
                     trigger_rec.trigger_name,
                     trigger_rec.table_name);
   END LOOP;
END $$;

-- 3. Eliminar y reconfigurar primary keys y columnas necesarias
ALTER TABLE students DROP CONSTRAINT IF EXISTS students_pkey;
ALTER TABLE students ALTER COLUMN school_id SET NOT NULL;
ALTER TABLE students ADD PRIMARY KEY (id, school_id);

-- Para tutors, primero añadir la columna school_id y configurarla
ALTER TABLE tutors DROP CONSTRAINT IF EXISTS tutors_pkey;
ALTER TABLE tutors ADD COLUMN IF NOT EXISTS school_id uuid;
UPDATE tutors SET school_id = (SELECT id FROM schools LIMIT 1) WHERE school_id IS NULL;
ALTER TABLE tutors ALTER COLUMN school_id SET NOT NULL;
ALTER TABLE tutors ADD PRIMARY KEY (id, school_id);

ALTER TABLE messages DROP CONSTRAINT IF EXISTS unique_id;
ALTER TABLE messages ALTER COLUMN school_id SET NOT NULL;
ALTER TABLE messages ADD PRIMARY KEY (id, school_id, created_at);

-- 4. Distribuir las tablas
-- Primero schools como tabla de referencia
SELECT create_reference_table('schools');

-- Luego students como tabla base para colocalización
SELECT create_distributed_table('students', 'school_id');

-- Después tutors colocada con students
SELECT create_distributed_table('tutors', 'school_id', colocate_with => 'students');

-- Messages y sus particiones
SELECT create_distributed_table('messages', 'school_id', colocate_with => 'students');

-- 5. Recrear foreign keys con las columnas correctas
ALTER TABLE students ADD CONSTRAINT students_school_id_fkey
  FOREIGN KEY (school_id) REFERENCES schools(id);

ALTER TABLE tutors ADD CONSTRAINT tutors_school_id_fkey
  FOREIGN KEY (school_id) REFERENCES schools(id);

ALTER TABLE messages ADD CONSTRAINT messages_school_id_fkey
  FOREIGN KEY (school_id) REFERENCES schools(id);

-- Foreign keys modificadas para incluir school_id
ALTER TABLE messages ADD CONSTRAINT messages_student_id_fkey
  FOREIGN KEY (student_id, school_id) REFERENCES students(id, school_id);

ALTER TABLE messages ADD CONSTRAINT messages_tutor_id_fkey
  FOREIGN KEY (tutor_id, school_id) REFERENCES tutors(id, school_id);

-- 6. Configuración básica de Citus
ALTER DATABASE test_db SET citus.enable_repartition_joins TO ON;