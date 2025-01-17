# Comandos para preparar a la base de datos en modo distribuido. Hay que ejecutarlos en el nodo master.
# Esto hay que revisarlo y prepararlo de tal manera que se pueda automatizar, como un script en el Dockerfile.
test_db=# \s historial.sql
Wrote history to file "historial.sql".
test_db=# \set HISTCONTROL IGNOREDUPS
\set HISTFILESIZE 100000
test_db=# exit
# whereis historial.sql
historial.sql:
# cat historial.sql
ALTER TABLE messages DROP CONSTRAINT messages_school_id_fkey;
ALTER TABLE messages DROP CONSTRAINT messages_student_id_fkey;
ALTER TABLE messages DROP CONSTRAINT messages_tutor_id_fkey;
SELECT truncate_local_data_after_distributing_table('public.schools');
SELECT truncate_local_data_after_distributing_table('public.students');
SELECT truncate_local_data_after_distributing_table('public.tutors');
ALTER TABLE messages ADD CONSTRAINT messages_school_id_fkey
    FOREIGN KEY (school_id) REFERENCES schools(id);
ALTER TABLE messages ADD CONSTRAINT messages_student_id_fkey
    FOREIGN KEY (student_id) REFERENCES students(id);
ALTER TABLE messages ADD CONSTRAINT messages_tutor_id_fkey
    FOREIGN KEY (tutor_id) REFERENCES tutors(id);
SELECT pg_get_functiondef(oid) FROM pg_proc WHERE proname = 'validate_message_access';
DROP TRIGGER IF EXISTS message_access_validation ON messages;
DROP TRIGGER IF EXISTS message_access_validation ON messages_y2024m12;
DROP TRIGGER IF EXISTS message_access_validation ON messages_y2025m01;
DROP TRIGGER IF EXISTS message_access_validation ON messages_y2025m02;
SELECT create_distributed_table('messages', 'id');
-- Primero, eliminar las distribuciones actuales
SELECT undistribute_table('students');
SELECT undistribute_table('tutors');

-- Luego redistribuir asegurando la colocalización
SELECT create_distributed_table('students', 'id', colocate_with => 'none');
SELECT create_distributed_table('tutors', 'id', colocate_with => 'students');
SELECT create_distributed_table('messages', 'id', colocate_with => 'students');
SELECT undistribute_table('students', cascade_via_foreign_keys=>true);
SELECT undistribute_table('tutors', cascade_via_foreign_keys=>true);
ALTER TABLE messages DROP CONSTRAINT messages_school_id_fkey;
ALTER TABLE messages DROP CONSTRAINT messages_student_id_fkey;
ALTER TABLE messages DROP CONSTRAINT messages_tutor_id_fkey;
SELECT create_distributed_table('students', 'id', colocate_with => 'none');
SELECT create_distributed_table('tutors', 'id', colocate_with => 'students');
SELECT create_distributed_table('messages', 'id', colocate_with => 'students');
ALTER TABLE messages ADD CONSTRAINT messages_school_id_fkey
    FOREIGN KEY (school_id) REFERENCES schools(id);
ALTER TABLE messages ADD CONSTRAINT messages_student_id_fkey
    FOREIGN KEY (student_id) REFERENCES students(id);
ALTER TABLE messages ADD CONSTRAINT messages_tutor_id_fkey
    FOREIGN KEY (tutor_id) REFERENCES tutors(id);
-- Drop foreign keys
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_school_id_fkey;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_student_id_fkey;
ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_tutor_id_fkey;

ALTER TABLE students DROP CONSTRAINT IF EXISTS students_school_id_fkey;
ALTER TABLE tutors DROP CONSTRAINT IF EXISTS tutors_school_id_fkey;
-- Primero schools como reference table (ya que es la tabla de referencia principal)
SELECT create_reference_table('schools');

-- Luego students con una nueva distribución
SELECT create_distributed_table('students', 'id', colocate_with => 'none');

-- Después tutors colocado con students
SELECT create_distributed_table('tutors', 'id', colocate_with => 'students');

-- Finalmente messages colocado con students
SELECT create_distributed_table('messages', 'id', colocate_with => 'students');
SELECT truncate_local_data_after_distributing_table('public.schools');
SELECT truncate_local_data_after_distributing_table('public.students');
SELECT truncate_local_data_after_distributing_table('public.tutors');
SELECT run_command_on_workers('DROP TABLE IF EXISTS messages CASCADE;');
SELECT create_distributed_table('messages', 'id', colocate_with => 'students');
SELECT truncate_local_data_after_distributing_table('public.messages_y2025m01');
-- Recrear las foreign keys
ALTER TABLE students ADD CONSTRAINT students_school_id_fkey
    FOREIGN KEY (school_id) REFERENCES schools(id);

ALTER TABLE messages ADD CONSTRAINT messages_school_id_fkey
    FOREIGN KEY (school_id) REFERENCES schools(id);
ALTER TABLE messages ADD CONSTRAINT messages_student_id_fkey
    FOREIGN KEY (student_id) REFERENCES students(id);
ALTER TABLE messages ADD CONSTRAINT messages_tutor_id_fkey
    FOREIGN KEY (tutor_id) REFERENCES tutors(id);
CREATE TRIGGER message_access_validation
BEFORE INSERT OR UPDATE ON messages
FOR EACH ROW EXECUTE FUNCTION validate_message_access();
SELECT undistribute_table('messages', cascade_via_foreign_keys=>true);
SELECT undistribute_table('students', cascade_via_foreign_keys=>true);
SELECT undistribute_table('tutors', cascade_via_foreign_keys=>true);
SELECT undistribute_table('schools', cascade_via_foreign_keys=>true);
SELECT create_reference_table('schools');
SELECT create_distributed_table('students', 'school_id');
SELECT create_distributed_table('tutors', 'school_id', colocate_with => 'students');
SELECT create_distributed_table('messages', 'school_id', colocate_with => 'students');
\d+ students
\d+ schools
\d+ tutors
\d+ messages
-- Crear una nueva PK que incluya school_id
ALTER TABLE students DROP CONSTRAINT students_pkey;
ALTER TABLE students ADD PRIMARY KEY (id, school_id);

-- Ahora podemos distribuir
SELECT create_distributed_table('students', 'school_id');
-- Modificar tutors para incluir school_id en su PK
ALTER TABLE tutors DROP CONSTRAINT tutors_pkey;
ALTER TABLE tutors ADD PRIMARY KEY (id);
ALTER TABLE tutors ADD school_id uuid REFERENCES schools(id);  -- Añadir school_id
ALTER TABLE tutors ALTER COLUMN school_id SET NOT NULL;  -- Hacerlo NOT NULL
ALTER TABLE tutors DROP CONSTRAINT tutors_pkey;
ALTER TABLE tutors ADD PRIMARY KEY (id, school_id);

-- Distribuir tutors
SELECT create_distributed_table('tutors', 'school_id', colocate_with => 'students');
ALTER TABLE tutors DROP CONSTRAINT schools_id_fkey;
\d+ students
\d+ schools
\d+ tutors
\d+ messages
ALTER TABLE tutors DROP CONSTRAINT schools_id_fkey;
-- 1. Eliminar la constraint existente
ALTER TABLE tutors DROP CONSTRAINT tutors_school_id_fkey;

-- 2. Obtener un ID de escuela válido y actualizar los tutores
SELECT id FROM schools LIMIT 1;  -- Primero veamos qué ID usar
-- 3. Usar ese ID para actualizar los tutores (reemplaza <school_id> con el ID real)
UPDATE tutors SET school_id = '457fac03-dd67-49db-a42c-e9d9f81f1fb9';
-- 4. Ahora podemos hacer los cambios necesarios
ALTER TABLE tutors ALTER COLUMN school_id SET NOT NULL;
ALTER TABLE tutors ADD CONSTRAINT tutors_school_id_fkey FOREIGN KEY (school_id) REFERENCES schools(id);
ALTER TABLE tutors ADD PRIMARY KEY (id, school_id);
SELECT create_distributed_table('tutors', 'school_id', colocate_with => 'students');
SELECT truncate_local_data_after_distributing_table('public.tutors');
-- Primero eliminar la PK y FKs existentes
ALTER TABLE messages DROP CONSTRAINT unique_id;
ALTER TABLE messages DROP CONSTRAINT messages_school_id_fkey;

-- Crear nueva PK incluyendo school_id
ALTER TABLE messages ADD PRIMARY KEY (id, school_id, created_at);

-- Distribuir la tabla
SELECT create_distributed_table('messages', 'school_id', colocate_with => 'students');
-- Ver tablas distribuidas y su tipo
SELECT logicalrelid, partmethod, colocationid
FROM pg_dist_partition
ORDER BY logicalrelid::text;

-- Ver nodos activos
SELECT * FROM citus_get_active_worker_nodes();
-- Insertar una nueva escuela
INSERT INTO schools (name, state, country)
VALUES ('Escuela Prueba', 'Madrid', 'ES')
RETURNING id, name;
-- Usar ese id para insertar un estudiante
INSERT INTO students (name, school_id)
VALUES ('Estudiante Prueba', '7388b47f-4685-4a71-8dac-505f6cd8a859')
RETURNING id, name, school_id;
-- Insertar un tutor para esa escuela
INSERT INTO tutors (name, school_id)
VALUES ('Tutor Prueba', '7388b47f-4685-4a71-8dac-505f6cd8a859')
RETURNING id, name, school_id;
-- Insertar un mensaje
INSERT INTO messages (claude_conversation_id, student_id, school_id, tutor_id, sender_type, content)
VALUES ('test-conv-1', 'fc50f8c4-878d-4a66-bb7a-2e68b583e939', '7388b47f-4685-4a71-8dac-505f6cd8a859', '8b1764a8-7cf9-41cd-a849-46317132ce92', 'TUTOR', 'Mensaje de prueba');
\s historial.sql
#