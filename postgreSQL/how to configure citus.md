# psql -h localhost -d test_db -U test_user;
Password for user test_user: 
psql (17.2 (Debian 17.2-1.pgdg120+1), server 15.10 (Debian 15.10-1.pgdg120+1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off, ALPN: none)
Type "help" for help.

test_db=# -- Ejemplo con una de tus tablas existentes, por ejemplo 'messages'
SELECT create_distributed_table('messages', 'id');
ERROR:  cannot distribute relation "messages" because it has triggers
HINT:  Consider dropping all the triggers on "messages" and retry.
test_db=# SELECT run_command_on_workers('SELECT version();');
                                                               run_command_on_workers                                                               
----------------------------------------------------------------------------------------------------------------------------------------------------
 (attendance-worker,5432,t,"PostgreSQL 15.10 (Debian 15.10-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit")
(1 row)

test_db=# SELECT tgname, tgrelid::regclass AS table_name
FROM pg_trigger
WHERE tgrelid = 'messages'::regclass;
            tgname            | table_name 
------------------------------+------------
 RI_ConstraintTrigger_c_17390 | messages
 RI_ConstraintTrigger_c_17391 | messages
 RI_ConstraintTrigger_c_17395 | messages
 RI_ConstraintTrigger_c_17396 | messages
 RI_ConstraintTrigger_c_17400 | messages
 RI_ConstraintTrigger_c_17401 | messages
 message_access_validation    | messages
(7 rows)

test_db=# SELECT pg_get_triggerdef(oid) 
FROM pg_trigger 
WHERE tgname = 'message_access_validation';
                                                                  pg_get_triggerdef                                                                   
------------------------------------------------------------------------------------------------------------------------------------------------------
 CREATE TRIGGER message_access_validation BEFORE INSERT OR UPDATE ON public.messages FOR EACH ROW EXECUTE FUNCTION validate_message_access()
 CREATE TRIGGER message_access_validation BEFORE INSERT OR UPDATE ON public.messages_y2024m12 FOR EACH ROW EXECUTE FUNCTION validate_message_access()
 CREATE TRIGGER message_access_validation BEFORE INSERT OR UPDATE ON public.messages_y2025m01 FOR EACH ROW EXECUTE FUNCTION validate_message_access()
 CREATE TRIGGER message_access_validation BEFORE INSERT OR UPDATE ON public.messages_y2025m02 FOR EACH ROW EXECUTE FUNCTION validate_message_access()
(4 rows)

test_db=# SELECT
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'messages'::regclass;
     constraint_name      |              constraint_definition               
--------------------------+--------------------------------------------------
 unique_id                | PRIMARY KEY (id, created_at)
 messages_student_id_fkey | FOREIGN KEY (student_id) REFERENCES students(id)
 messages_school_id_fkey  | FOREIGN KEY (school_id) REFERENCES schools(id)
 messages_tutor_id_fkey   | FOREIGN KEY (tutor_id) REFERENCES tutors(id)
(4 rows)

test_db=# -- Distribuir primero las tablas padre
SELECT create_distributed_table('schools', 'id');
SELECT create_distributed_table('students', 'id');
SELECT create_distributed_table('tutors', 'id');
ERROR:  relation "schools" already exists
CONTEXT:  while executing command on attendance-worker:5432
ERROR:  referenced table "schools" must be a distributed table or a reference table
DETAIL:  To enforce foreign keys, the referencing and referenced rows need to be stored on the same node.
HINT:  You could use SELECT create_reference_table('schools') to replicate the referenced table to all nodes or consider dropping the foreign key
ERROR:  relation "tutors" already exists
CONTEXT:  while executing command on attendance-worker:5432
test_db=# SELECT run_command_on_workers('DROP TABLE IF EXISTS schools CASCADE;');
SELECT run_command_on_workers('DROP TABLE IF EXISTS students CASCADE;');
SELECT run_command_on_workers('DROP TABLE IF EXISTS tutors CASCADE;');
         run_command_on_workers          
-----------------------------------------
 (attendance-worker,5432,t,"DROP TABLE")
(1 row)

         run_command_on_workers          
-----------------------------------------
 (attendance-worker,5432,t,"DROP TABLE")
(1 row)

         run_command_on_workers          
-----------------------------------------
 (attendance-worker,5432,t,"DROP TABLE")
(1 row)

test_db=# SELECT create_reference_table('schools');
NOTICE:  Copying data from local table...
NOTICE:  copying the data has completed
DETAIL:  The local data in the table is no longer visible, but is still on disk.
HINT:  To remove the local data, run: SELECT truncate_local_data_after_distributing_table($$public.schools$$)
 create_reference_table 
------------------------
 
(1 row)

test_db=# SELECT create_distributed_table('students', 'id');
SELECT create_distributed_table('tutors', 'id');
NOTICE:  Copying data from local table...
NOTICE:  copying the data has completed
DETAIL:  The local data in the table is no longer visible, but is still on disk.
HINT:  To remove the local data, run: SELECT truncate_local_data_after_distributing_table($$public.students$$)
 create_distributed_table 
--------------------------
 
(1 row)

NOTICE:  Copying data from local table...
NOTICE:  copying the data has completed
DETAIL:  The local data in the table is no longer visible, but is still on disk.
HINT:  To remove the local data, run: SELECT truncate_local_data_after_distributing_table($$public.tutors$$)
 create_distributed_table 
--------------------------
 
(1 row)

test_db=# SELECT truncate_local_data_after_distributing_table('public.schools');
SELECT truncate_local_data_after_distributing_table('public.students');
SELECT truncate_local_data_after_distributing_table('public.tutors');
ERROR:  cannot truncate a table referenced in a foreign key constraint by a local table
DETAIL:  Table "messages" references "schools"
ERROR:  cannot truncate a table referenced in a foreign key constraint by a local table
DETAIL:  Table "messages" references "students"
ERROR:  cannot truncate a table referenced in a foreign key constraint by a local table
DETAIL:  Table "messages" references "tutors"
test_db=# ALTER TABLE messages DROP CONSTRAINT messages_school_id_fkey;
ALTER TABLE messages DROP CONSTRAINT messages_student_id_fkey;
ALTER TABLE messages DROP CONSTRAINT messages_tutor_id_fkey;
ALTER TABLE
ALTER TABLE
ALTER TABLE
test_db=# SELECT truncate_local_data_after_distributing_table('public.schools');
SELECT truncate_local_data_after_distributing_table('public.students');
SELECT truncate_local_data_after_distributing_table('public.tutors');
NOTICE:  truncate cascades to table "students"
 truncate_local_data_after_distributing_table 
----------------------------------------------
 
(1 row)

 truncate_local_data_after_distributing_table 
----------------------------------------------
 
(1 row)

 truncate_local_data_after_distributing_table 
----------------------------------------------
 
(1 row)

test_db=# ALTER TABLE messages ADD CONSTRAINT messages_school_id_fkey 
    FOREIGN KEY (school_id) REFERENCES schools(id);
ALTER TABLE messages ADD CONSTRAINT messages_student_id_fkey 
    FOREIGN KEY (student_id) REFERENCES students(id);
ALTER TABLE messages ADD CONSTRAINT messages_tutor_id_fkey 
    FOREIGN KEY (tutor_id) REFERENCES tutors(id);
ALTER TABLE
ALTER TABLE
ALTER TABLE
test_db=# 