DO $$
DECLARE
    -- Variables para roles
    v_admin_role_id UUID;
    v_school_role_id UUID;
    v_tutor_role_id UUID;
    v_temp_role_id UUID;

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
    v_close_conversations_permission_id UUID;
    v_temp_permission_id UUID;

    -- Variables para usuarios
    v_admin_user_id UUID;
    v_school_user_id UUID;
    v_tutor_user_id UUID;
    v_temp_user_id UUID;

    -- Variables para escuelas
    v_school_id1 UUID;
    v_school_id2 UUID;
    v_school_id3 UUID;

    -- Variables para tutores
    v_tutor_id1 UUID;
    v_tutor_id2 UUID;
    v_tutor_id3 UUID;

    -- Variables para estudiantes
    v_student_id1 UUID;
    v_student_id2 UUID;
    v_student_id3 UUID;

    -- Variables para conversaciones
    v_conversation_id1 UUID;
    v_conversation_id2 UUID;
    v_conversation_id3 UUID;

    -- Variables para mensajes
    v_message_id1 UUID;
    v_message_id2 UUID;
    v_message_id3 UUID;

    -- Variables temporales
    v_temp_id UUID;
    v_has_permission BOOLEAN;
BEGIN
    -- 1. Crear y actualizar roles
    CALL create_role('ADMIN', v_admin_role_id);
    CALL create_role('SCHOOL', v_school_role_id);
    CALL create_role('TUTOR', v_tutor_role_id);
    CALL create_role('TEMP_ROLE', v_temp_role_id);

    -- Probar actualización de rol
    CALL update_encrypted_role(v_temp_role_id, 'UPDATED_TEMP_ROLE');

    -- 2. Crear y actualizar permisos
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
    CALL create_permission('TEMP_PERMISSION', v_temp_permission_id);

    -- Probar actualización de permiso
    CALL update_encrypted_permission(v_temp_permission_id, 'UPDATED_TEMP_PERMISSION');

    -- 3. Asignar permisos a roles usando el nuevo procedimiento
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
    CALL update_role_permission(v_admin_role_id, v_close_conversations_permission_id, 'ADD');

    -- School - permisos limitados
    CALL update_role_permission(v_school_role_id, v_create_student_permission_id, 'ADD');
    CALL update_role_permission(v_school_role_id, v_update_student_permission_id, 'ADD');
    CALL update_role_permission(v_school_role_id, v_delete_student_permission_id, 'ADD');
    CALL update_role_permission(v_school_role_id, v_send_messages_permission_id, 'ADD');
    CALL update_role_permission(v_school_role_id, v_close_conversations_permission_id, 'ADD');

    -- Tutor - permisos básicos
    CALL update_role_permission(v_tutor_role_id, v_view_records_permission_id, 'ADD');
    CALL update_role_permission(v_tutor_role_id, v_send_messages_permission_id, 'ADD');

    -- Probar eliminación de permiso
    CALL update_role_permission(v_tutor_role_id, v_send_messages_permission_id, 'REMOVE');
    CALL update_role_permission(v_tutor_role_id, v_send_messages_permission_id, 'ADD');

    -- 4. Crear y actualizar usuarios
    CALL create_user('admin', 'admin_password', v_admin_role_id, v_admin_user_id);
    CALL create_user('school_user', 'school_password', v_school_role_id, v_school_user_id);
    CALL create_user('tutor_user', 'tutor_password', v_tutor_role_id, v_tutor_user_id);
    CALL create_user('temp_user', 'temp_password', v_temp_role_id, v_temp_user_id);

    -- Probar actualización de usuario
    CALL update_encrypted_user(v_temp_user_id, 'updated_temp_user', 'new_password', v_temp_role_id);

    -- 5. Crear y actualizar escuelas
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

    CALL create_school(
        'Temp School',
        '+1234567890',
        'Temp Address',
        'Temp Country',
        v_school_id3
    );

    -- Probar actualización de escuela
    CALL update_encrypted_school(
        v_school_id3,
        'Updated Temp School',
        '+0987654321',
        'Updated Address',
        'Updated Country'
    );

    -- 6. Crear y actualizar tutores
    CALL create_tutor(
        'María García',
        '+3466655444',
        'maria.garcia@email.com',
        v_tutor_id1
    );

    CALL create_tutor(
        'John Smith',
        '+12125557890',
        'john.smith@email.com',
        v_tutor_id2
    );

    CALL create_tutor(
        'Temp Tutor',
        '+1234567890',
        'temp.tutor@email.com',
        v_tutor_id3
    );

    -- Probar actualización de tutor
    CALL update_encrypted_tutor(
        v_tutor_id3,
        'Updated Temp Tutor',
        '+0987654321',
        'updated.temp.tutor@email.com'
    );

    -- 7. Crear y actualizar estudiantes
    CALL create_student(
        'Carlos García',
        '2010-05-15'::DATE,
        v_school_id1,
        v_student_id1
    );

    CALL create_student(
        'Emma Smith',
        '2009-08-22'::DATE,
        v_school_id2,
        v_student_id2
    );

    CALL create_student(
        'Temp Student',
        '2011-01-01'::DATE,
        v_school_id3,
        v_student_id3
    );

    -- Probar actualización de estudiante
    CALL update_encrypted_student(
        v_student_id3,
        'Updated Temp Student',
        '2011-02-02'::DATE,
        v_school_id2
    );

    -- 8. Crear y actualizar relaciones tutor-estudiante
    CALL create_tutor_student_relationship(v_tutor_id1, v_student_id1, 'PARENT');
    CALL create_tutor_student_relationship(v_tutor_id2, v_student_id2, 'PARENT');
    CALL create_tutor_student_relationship(v_tutor_id3, v_student_id3, 'GUARDIAN');

    -- Probar actualización de relación tutor-estudiante
    CALL update_tutor_student_relationship(
        v_tutor_id3,
        v_student_id3,
        'UPDATED_GUARDIAN',
        true
    );

    -- 9. Crear y actualizar conversaciones
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

    CALL create_conversation(
        v_student_id3,
        v_school_id3,
        'temp-conversation',
        v_conversation_id3
    );

    -- Probar actualización de conversación
    CALL update_encrypted_conversation(
        v_conversation_id3,
        v_student_id3,
        v_school_id3,
        'updated-temp-conversation',
        'UPDATED'
    );

    -- 10. Crear y actualizar mensajes
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

    CALL create_message(
        v_conversation_id3,
        'STUDENT',
        v_student_id3,
        'Temp message',
        NULL,
        v_message_id3
    );

    -- Probar actualización de mensaje
    CALL update_encrypted_message(
        v_message_id3,
        v_conversation_id3,
        'STUDENT',
        v_student_id3,
        'Updated temp message',
        '{"status": "updated"}'::JSONB
    );

    -- 11. Crear y actualizar estados de servicio
    CALL create_service_status('Claude', false, 'No errors', v_temp_id);
    CALL create_service_status('Whatsapp', false, 'No errors', v_temp_id);
    CALL create_service_status('Backend', false, 'No errors', v_temp_id);

    -- Probar actualización de estado de servicio
    CALL update_service_status(v_temp_id, 'Backend', true, 'Updated status');

    -- 12. Probar funciones de consulta
    -- Verificar permisos
    SELECT user_has_permission(v_admin_user_id, 'CREATE_SCHOOL') INTO v_has_permission;
    RAISE NOTICE 'Admin has CREATE_SCHOOL permission: %', v_has_permission;

    -- Obtener permisos de rol
    PERFORM * FROM get_role_permissions(v_admin_role_id);

    -- Obtener tutores de estudiante
    PERFORM * FROM get_student_tutors(v_student_id1);

    -- Obtener estudiantes de tutor
    PERFORM * FROM get_tutor_students(v_tutor_id1);

    -- Obtener conversaciones de estudiante
    PERFORM * FROM get_student_conversations(v_student_id1);

    -- Obtener mensajes de conversación
    PERFORM * FROM get_conversation_messages(v_conversation_id1);

    -- Obtener estado de servicios
    PERFORM * FROM get_all_service_status();

    -- 13. Probar eliminaciones
    -- Eliminar mensaje temporal
    CALL delete_message(v_message_id3);

    -- Eliminar conversación temporal
    CALL delete_conversation(v_conversation_id3);

    -- Eliminar estudiante temporal
    CALL delete_student(v_student_id3);

    -- Eliminar tutor temporal
    CALL delete_tutor(v_tutor_id3);

    -- Eliminar escuela temporal
    CALL delete_school(v_school_id3);

    -- Eliminar usuario temporal
    CALL delete_user(v_temp_user_id);

    -- Eliminar rol temporal
    CALL delete_role(v_temp_role_id);

    -- Eliminar permiso temporal
    CALL delete_permission(v_temp_permission_id);

    RAISE NOTICE 'Data initialization completed successfully';
END;
$$;