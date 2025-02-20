-- Tablas para el sistema ACL
CREATE TABLE roles (
   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
   name VARCHAR(50) NOT NULL,
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   created_by UUID,
   updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   updated_by UUID
);

CREATE TABLE permissions (
   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
   name VARCHAR(50) NOT NULL,
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   created_by UUID,
   updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   updated_by UUID
);

CREATE TABLE role_permissions (
   role_id UUID REFERENCES roles(id),
   permission_id UUID REFERENCES permissions(id),
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   created_by UUID,
   PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE schools (
   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
   name VARCHAR(50) NOT NULL,
   phone VARCHAR(20),
   address VARCHAR(50),
   state VARCHAR(20),
   country VARCHAR(5),
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   created_by UUID,
   updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   updated_by UUID
);

CREATE TABLE tutors (
   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
   name VARCHAR(50) NOT NULL,
   phone VARCHAR(20),
   email VARCHAR(50),
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   created_by UUID,
   updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   updated_by UUID
);

CREATE TABLE users (
   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
   username VARCHAR(50) NOT NULL,
   password_hash VARCHAR(100) NOT NULL,
   role_id UUID REFERENCES roles(id),
   entity_type VARCHAR(6) CHECK (entity_type IN ('SCHOOL', 'TUTOR')),
   entity_id UUID,
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   created_by UUID,
   updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   updated_by UUID
);

-- En lugar de las foreign keys condicionales, usamos un trigger
CREATE OR REPLACE FUNCTION validate_entity_reference()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.entity_type = 'SCHOOL' THEN
        IF NOT EXISTS (SELECT 1 FROM schools WHERE id = NEW.entity_id) THEN
            RAISE EXCEPTION 'Invalid school reference';
        END IF;
    ELSIF NEW.entity_type = 'TUTOR' THEN
        IF NOT EXISTS (SELECT 1 FROM tutors WHERE id = NEW.entity_id) THEN
            RAISE EXCEPTION 'Invalid tutor reference';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_entity_reference
    BEFORE INSERT OR UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION validate_entity_reference();

CREATE TABLE students (
   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
   name VARCHAR(50) NOT NULL,
   date_of_birth DATE,
   school_id UUID REFERENCES schools(id),
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   created_by UUID,
   updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   updated_by UUID
);

CREATE TABLE messages (
    id UUID DEFAULT uuid_generate_v4(),
    claude_conversation_id VARCHAR(50) NOT NULL,
    student_id UUID REFERENCES students(id),
    school_id UUID REFERENCES schools(id),
    tutor_id UUID REFERENCES tutors(id),
    sender_type sender_type_enum NOT NULL,
    content VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    PRIMARY KEY (id, created_at),
    CONSTRAINT unique_id UNIQUE (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE system_config (
   key VARCHAR(50) PRIMARY KEY,
   value TEXT,
   description VARCHAR(200),
   updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
   updated_by UUID REFERENCES users(id)
);

CREATE TABLE system_notifications (
   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
   level notification_level NOT NULL,
   category notification_category NOT NULL,
   message VARCHAR(500) NOT NULL,
   details JSONB,
   source_entity_type VARCHAR(6),
   source_entity_id UUID,
   acknowledged BOOLEAN DEFAULT FALSE,
   acknowledged_by UUID REFERENCES users(id),
   acknowledged_at TIMESTAMP WITH TIME ZONE,
   created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_messages_claude_conversation_id ON messages(claude_conversation_id);
CREATE INDEX idx_messages_student_id ON messages(student_id);
CREATE INDEX idx_messages_school_id ON messages(school_id);
CREATE INDEX idx_messages_tutor_id ON messages(tutor_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_sender_type ON messages(sender_type);

CREATE INDEX idx_students_school_id ON students(school_id);
CREATE INDEX idx_students_name_dob ON students(name, date_of_birth);

CREATE INDEX idx_users_entity ON users(entity_type, entity_id);
CREATE INDEX idx_users_role_id ON users(role_id);

CREATE INDEX idx_system_notifications_level ON system_notifications(level);
CREATE INDEX idx_system_notifications_category ON system_notifications(category);
CREATE INDEX idx_system_notifications_created_at ON system_notifications(created_at);
CREATE INDEX idx_system_notifications_unack ON system_notifications(acknowledged) WHERE NOT acknowledged;

CREATE INDEX idx_messages_content_fts ON messages USING gin(to_tsvector('spanish', content));


-- Comentarios en las tablas
COMMENT ON TABLE messages IS 'Almacena todos los mensajes intercambiados entre escuelas, tutores y Claude';
COMMENT ON TABLE system_notifications IS 'Registro de eventos y notificaciones del sistema';
COMMENT ON TABLE system_config IS 'Configuración global del sistema';