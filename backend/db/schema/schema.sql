CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE tutors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    school_id UUID REFERENCES schools(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tutor_student (
    tutor_id UUID REFERENCES tutors(id),
    student_id UUID REFERENCES students(id),
    relationship_type VARCHAR(50) NOT NULL, -- 'PARENT', 'LEGAL_GUARDIAN', 'RELATIVE', 'OFFICIAL'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (tutor_id, student_id)
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) NOT NULL,
    school_id UUID REFERENCES schools(id) NOT NULL,
    claude_conversation_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'INITIATED',
    reason TEXT,
    last_interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    CONSTRAINT valid_status CHECK (status IN (
        'INITIATED',
        'PENDING_TUTOR',
        'ACTIVE_TUTOR_DIALOG',
        'PENDING_SCHOOL_CONFIRMATION',
        'SCHOOL_CONFIRMED',
        'CLOSED',
        'CANCELLED'
    ))
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    sender_id UUID NOT NULL, -- ID del tutor, escuela o 'CLAUDE' para mensajes del sistema
    content TEXT NOT NULL,
    claude_response_metadata JSONB, -- Solo para mensajes donde sender_type = 'CLAUDE'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_sender_type CHECK (sender_type IN ('SCHOOL', 'TUTOR', 'CLAUDE'))
);

CREATE TABLE service_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(50) NOT NULL,
    status BOOLEAN DEFAULT false,
    last_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message VARCHAR(50) NOT NULL
);

CREATE INDEX idx_conversations_claude_id ON conversations(claude_conversation_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_tutor_student_student ON tutor_student(student_id);
CREATE INDEX idx_tutor_student_tutor ON tutor_student(tutor_id);

INSERT INTO schools (id, name, phone, address, country) VALUES
    (uuid_generate_v4(), 'IES San Isidro', '+34916421394', 'Calle Toledo, 39, 28005 Madrid', 'Spain'),
    (uuid_generate_v4(), 'Lincoln High School', '+12125556789', '1234 Broadway Ave, New York, NY 10019', 'USA');

INSERT INTO tutors (id, name, phone, email) VALUES
    (uuid_generate_v4(), 'María García', '+34666555444', 'maria.garcia@email.com'),
    (uuid_generate_v4(), 'John Smith', '+12125557890', 'john.smith@email.com'),
    (uuid_generate_v4(), 'Ana Martínez', '+34677888999', 'ana.martinez@email.com'),
    (uuid_generate_v4(), 'Sarah Johnson', '+12125559012', 'sarah.johnson@email.com');

INSERT INTO students (id, name, date_of_birth, school_id)
SELECT uuid_generate_v4(), 'Carlos García', '2010-05-15', id
FROM schools WHERE name = 'IES San Isidro';

INSERT INTO students (id, name, date_of_birth, school_id)
SELECT uuid_generate_v4(), 'Emma Smith', '2009-08-22', id
FROM schools WHERE name = 'Lincoln High School';

INSERT INTO service_status (id, service_name, status, error_message) VALUES
    (uuid_generate_v4(), 'Claude', false, 'No errors'),
    (uuid_generate_v4(), 'Whatsapp', false, 'No errors'),
    (uuid_generate_v4(), 'Backend', false, 'No errors');