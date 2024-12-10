DO $$
DECLARE
    v_admin_role_id UUID;
    v_school_role_id UUID;
    v_tutor_role_id UUID;
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
    v_close_conversations_permission_id UUID;
    v_admin_user_id UUID;
    v_school_user_id UUID;
    v_tutor_user_id UUID;
    v_school_id1 UUID;
    v_school_id2 UUID;
    v_tutor_id1 UUID;
    v_tutor_id2 UUID;
    v_student_id1 UUID;
    v_student_id2 UUID;
    v_conversation_id1 UUID;
    v_conversation_id2 UUID;
    v_message_id1 UUID;
    v_message_id2 UUID;
BEGIN
    -- Crear roles
    CALL create_role('ADMIN', v_admin_role_id);
    CALL create_role('SCHOOL', v_school_role_id);
    CALL create_role('TUTOR', v_tutor_role_id);

    -- Crear permisos
    CALL create_permission('CREATE_SCHOOL', v_create_school_permission_id);
    CALL create_permission('UPDATE_SCHOOL', v_update_school_permission_id);
    CALL create_permission('DELETE_SCHOOL', v_delete_school_permission_id);
    CALL create_permission('CREATE_STUDENT', v_create_student_permission_id);
    CALL create_permission('UPDATE_STUDENT', v_update_student_permission_id);
    CALL create_permission('DELETE_STUDENT', v_delete_student_permission_id);
    CALL create_permission('CREATE_TUTOR', v_create_tutor_permission_id);
    CALL create_permission('UPDATE_TUTOR', v_update_tutor_permission_id);
    CALL create_permission('DELETE_TUTOR', v_delete_tutor_permission_id);
    CALL create_permission('VIEW_STUDENT_RECORDS', v_view_records_permission_id);
    CALL create_permission('SEND_MESSAGES', v_send_messages_permission_id);
    CALL create_permission('CLOSE_CONVERSATIONS', v_close_conversations_permission_id);

    -- Asignar permisos a roles
    -- Admin
    CALL create_role_permission(v_admin_role_id, v_create_school_permission_id);
    CALL create_role_permission(v_admin_role_id, v_update_school_permission_id);
    CALL create_role_permission(v_admin_role_id, v_delete_school_permission_id);
    CALL create_role_permission(v_admin_role_id, v_create_student_permission_id);
    CALL create_role_permission(v_admin_role_id, v_update_student_permission_id);
    CALL create_role_permission(v_admin_role_id, v_delete_student_permission_id);
    CALL create_role_permission(v_admin_role_id, v_create_tutor_permission_id);
    CALL create_role_permission(v_admin_role_id, v_update_tutor_permission_id);
    CALL create_role_permission(v_admin_role_id, v_delete_tutor_permission_id);
    CALL create_role_permission(v_admin_role_id, v_view_records_permission_id);
    CALL create_role_permission(v_admin_role_id, v_send_messages_permission_id);
    CALL create_role_permission(v_admin_role_id, v_close_conversations_permission_id);

    -- School
    CALL create_role_permission(v_school_role_id, v_create_student_permission_id);
    CALL create_role_permission(v_school_role_id, v_update_student_permission_id);
    CALL create_role_permission(v_school_role_id, v_delete_student_permission_id);
    CALL create_role_permission(v_school_role_id, v_send_messages_permission_id);
    CALL create_role_permission(v_school_role_id, v_close_conversations_permission_id);

    -- Tutor
    CALL create_role_permission(v_tutor_role_id, v_view_records_permission_id);
    CALL create_role_permission(v_tutor_role_id, v_send_messages_permission_id);

    -- Crear usuarios iniciales
    CALL create_user('admin', 'admin_password', v_admin_role_id, v_admin_user_id);
    CALL create_user('school_user', 'school_password', v_school_role_id, v_school_user_id);
    CALL create_user('tutor_user', 'tutor_password', v_tutor_role_id, v_tutor_user_id);

    -- Crear escuelas iniciales
    CALL create_school(
        'IES San Isidro',
        '+34916421394',
        'Calle Toledo, 39, 28005 Madrid',
        'Spain',
        v_school_id1
    );

    CALL create_school(
        'Lincoln High School',
        '+12125556789',
        '1234 Broadway Ave, New York, NY 10019',
        'USA',
        v_school_id2
    );

    -- Crear tutores iniciales
    CALL create_tutor(
        'María García',
        '+34666555444',
        'maria.garcia@email.com',
        v_tutor_id1
    );

    CALL create_tutor(
        'John Smith',
        '+12125557890',
        'john.smith@email.com',
        v_tutor_id2
    );

    -- Crear estudiantes iniciales
    CALL create_student(
        'Carlos García',
        '2010-05-15',
        v_school_id1,
        v_student_id1
    );

    CALL create_student(
        'Emma Smith',
        '2009-08-22',
        v_school_id2,
        v_student_id2
    );

    -- Crear relaciones tutor-estudiante
    CALL create_tutor_student_relationship(
        v_tutor_id1,
        v_student_id1,
        'PARENT'
    );

    CALL create_tutor_student_relationship(
        v_tutor_id2,
        v_student_id2,
        'PARENT'
    );

    -- Crear conversaciones iniciales
    CALL create_conversation(
        v_student_id1,
        v_school_id1,
        'claude-conversation-1',
        v_conversation_id1
    );

    CALL create_conversation(
        v_student_id2,
        v_school_id2,
        'claude-conversation-2',
        v_conversation_id2
    );

    -- Crear mensajes iniciales
    CALL create_message(
        v_conversation_id1,
        'SCHOOL',
        v_school_user_id,
        'Student needs help with math homework',
        NULL,
        v_message_id1
    );

    CALL create_message(
        v_conversation_id2,
        'TUTOR',
        v_tutor_user_id,
        'Checking on student progress',
        NULL,
        v_message_id2
    );

    -- Crear estados de servicio iniciales
    CALL create_service_status('Claude', false, 'No errors', NULL);
    CALL create_service_status('Whatsapp', false, 'No errors', NULL);
    CALL create_service_status('Backend', false, 'No errors', NULL);
END;
$$;
