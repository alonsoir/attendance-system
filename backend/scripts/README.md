El procedimiento para inicializar correctamente vault aún no está fino del todo, pero se puede hacer de la siguiente manera:

Una vez que se haya iniciado el contenedor vault, puedes hacer login en el mismo, buscas Unseal Key y Root Token, y 

opcion 1) vault operator unseal -address=$VAULT_ADDR $UNSEAL_KEY

donde VAULT_ADDR="http://127.0.0.1:8200" y UNSEAL_KEY=tu_unseal_key

opcion 2)los guardas en un archivo .env, y luego haces un docker-compose up -d.
