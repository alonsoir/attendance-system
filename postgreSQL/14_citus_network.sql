-- 14_citus_network.sql
DO $$
BEGIN
    -- Esperar a que los servicios estén listos
    PERFORM pg_sleep(10);

    -- Configuración básica coordinator-worker
    IF EXISTS (
        SELECT 1 FROM pg_roles
        WHERE rolname = current_user
        AND rolsuper
    ) THEN
        -- Solo intentar añadir el worker si estamos en el coordinator
        BEGIN
            PERFORM citus_add_node('attendance-worker', 5432);
            RAISE NOTICE 'Worker añadido exitosamente';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Error al añadir worker: %', SQLERRM;
        END;
    END IF;

    -- Verificar la configuración
    PERFORM pg_sleep(2);
    RAISE NOTICE 'Nodos activos: %', (
        SELECT string_agg(node_name || ':' || nodeport, ', ')
        FROM citus_get_active_worker_nodes()
    );
END $$;