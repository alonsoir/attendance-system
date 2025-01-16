-- backend/tests/containers/test_data.sql

-- Insertar escuelas de prueba
INSERT INTO schools (id, name, phone, address, country)
VALUES
    (uuid_generate_v4(), 'IES Test Madrid', '+34916421394', 'Calle Test 1, Madrid', 'Spain'),
    (uuid_generate_v4(), 'Test High School', '+12125556789', '123 Test Ave, New York', 'USA');

-- Insertar tutores de prueba
INSERT INTO tutors (id, name, phone, email)
VALUES
    (uuid_generate_v4(), 'Test Tutor 1', '+34666555444', 'tutor1@test.com'),
    (uuid_generate_v4(), 'Test Tutor 2', '+34666555445', 'tutor2@test.com');

-- Insertar estudiantes (necesitamos los IDs de las escuelas)
WITH school_ids AS (SELECT id FROM schools LIMIT 2)
INSERT INTO students (id, name, date_of_birth, school_id)
SELECT
    uuid_generate_v4(),
    'Test Student ' || generate_series(1, 2),
    '2010-01-01'::date + (generate_series(1, 2) || ' years')::interval,
    id
FROM school_ids;