DO $$
DECLARE
    -- Variables para roles
    v_admin_role_id UUID;
    v_school_role_id UUID;
    v_tutor_role_id UUID;

    -- Variables para permisos
    v_create_school_permission_id UUID;
    v_update_school_permission_id UUID;
    v_delete_school_permission_id UUID;
    v_create_student_permission_id UUID;
    v_update_student_permission_id UUID;
    v_delete_student_permission_id UUID;
    v_create_tutor_permission_id UUID;
    v_update_tutor_permission_id UUID;
    v_delete_tutor_permission_id UUID;
    v_view_records_permission_id UUID;
    v_send_messages_permission_id UUID;

    -- Variables para entidades
    v_admin_user_id UUID;
    v_school_user_id UUID;
    v_tutor_user_id UUID;
    v_school_id1 UUID;
    v_school_id2 UUID;
    v_tutor_id1 UUID;
    v_tutor_id2 UUID;
    v_student_id1 UUID;
    v_student_id2 UUID;
    v_message_id1 UUID;
    v_message_id2 UUID;

BEGIN
    -- 1. Crear roles base
    CALL create_role('ADMIN', v_admin_user_id, v_admin_role_id);
    CALL create_role('SCHOOL', v_admin_user_id, v_school_role_id);
    CALL create_role('TUTOR', v_admin_user_id, v_tutor_role_id);

    -- 2. Crear permisos básicos
    CALL create_permission('CREATE_SCHOOL', v_admin_user_id, v_create_school_permission_id);
    CALL create_permission('UPDATE_SCHOOL', v_admin_user_id, v_update_school_permission_id);
    CALL create_permission('DELETE_SCHOOL', v_admin_user_id, v_delete_school_permission_id);
    CALL create_permission('CREATE_STUDENT', v_admin_user_id, v_create_student_permission_id);
    CALL create_permission('UPDATE_STUDENT', v_admin_user_id, v_update_student_permission_id);
    CALL create_permission('DELETE_STUDENT', v_admin_user_id, v_delete_student_permission_id);
    CALL create_permission('CREATE_TUTOR', v_admin_user_id, v_create_tutor_permission_id);
    CALL create_permission('UPDATE_TUTOR', v_admin_user_id, v_update_tutor_permission_id);
    CALL create_permission('DELETE_TUTOR', v_admin_user_id, v_delete_tutor_permission_id);
    CALL create_permission('VIEW_RECORDS', v_admin_user_id, v_view_records_permission_id);
    CALL create_permission('SEND_MESSAGES', v_admin_user_id, v_send_messages_permission_id);

    -- 3. Asignar permisos a roles
    -- Admin - todos los permisos
    CALL update_role_permission(v_admin_role_id, v_create_school_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_update_school_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_delete_school_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_create_student_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_update_student_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_delete_student_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_create_tutor_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_update_tutor_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_delete_tutor_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_view_records_permission_id, 'ADD');
    CALL update_role_permission(v_admin_role_id, v_send_messages_permission_id, 'ADD');

    -- School - permisos limitados
    CALL update_role_permission(v_school_role_id, v_create_student_permission_id, 'ADD');
    CALL update_role_permission(v_school_role_id, v_update_student_permission_id, 'ADD');
    CALL update_role_permission(v_school_role_id, v_send_messages_permission_id, 'ADD');

    -- Tutor - permisos básicos
    CALL update_role_permission(v_tutor_role_id, v_view_records_permission_id, 'ADD');
    CALL update_role_permission(v_tutor_role_id, v_send_messages_permission_id, 'ADD');

    -- 4. Crear escuelas de prueba
    CALL create_school(
        'IES San Isidro',
        '+34916421394',
        'Calle Toledo, 39',
        'Madrid',
        'ES',
        v_admin_user_id,
        v_school_id1
    );

    CALL create_school(
        'Lincoln High School',
        '+12125556789',
        '1234 Broadway Ave',
        'NY',
        'US',
        v_admin_user_id,
        v_school_id2
    );

    -- 5. Crear usuarios vinculados a escuelas
    CALL create_user(
        'school1_admin',
        'school1_pass',
        v_school_role_id,
        'SCHOOL',
        v_school_id1,
        v_admin_user_id,
        v_school_user_id
    );

    -- 6. Crear tutores
CALL create_tutor(
    'María García',
    '+34666554433',
    'maria.garcia@email.com',
    v_school_id1,              -- Añadido school_id1
    v_admin_user_id,
    v_tutor_id1
);

CALL create_tutor(
    'John Smith',
    '+12125557890',
    'john.smith@email.com',
    v_school_id2,              -- Añadido school_id2
    v_admin_user_id,
    v_tutor_id2
);

    -- 7. Crear usuarios vinculados a tutores
    CALL create_user(
        'tutor1',
        'tutor1_pass',
        v_tutor_role_id,
        'TUTOR',
        v_tutor_id1,
        v_admin_user_id,
        v_tutor_user_id
    );

    -- 8. Crear estudiantes
    CALL create_student(
        'Carlos García',
        '2010-05-15'::DATE,
        v_school_id1,
        v_admin_user_id,
        v_student_id1
    );

    CALL create_student(
        'Emma Smith',
        '2009-08-22'::DATE,
        v_school_id2,
        v_admin_user_id,
        v_student_id2
    );

    -- 9. Crear mensajes de prueba
    -- Mensaje de escuela
    CALL create_message(
        'claude-conv-1',
        v_student_id1,
        v_school_id1,
        NULL,
        'SCHOOL'::sender_type_enum,
        'Inicio de conversación sobre el estudiante Carlos',
        v_school_user_id,
        v_message_id1
    );

    -- Respuesta de Claude
    CALL create_message(
        'claude-conv-1',
        v_student_id1,
        v_school_id1,
        NULL,
        'CLAUDE'::sender_type_enum,
        'Entiendo, ¿en qué puedo ayudar con Carlos?',
        v_school_user_id,
        v_message_id2
    );

    -- 10. Crear registros de estado del sistema
    INSERT INTO system_notifications (
        level,
        category,
        message,
        details
    ) VALUES (
        'INFO',
        'SYSTEM',
        'Inicialización de datos de prueba completada',
        jsonb_build_object(
            'schools_created', 2,
            'tutors_created', 2,
            'students_created', 2,
            'messages_created', 2
        )
    );

    RAISE NOTICE 'Inicialización de datos de prueba completada exitosamente';
END;
$$;