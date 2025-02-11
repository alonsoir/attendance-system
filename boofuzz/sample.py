from boofuzz import *

'''
in a terminal, run 

1) nc -l 1337

It will crash inmediatly

2) socat TCP-LISTEN:1337,reuseaddr,fork STDOUT

It wont crash

3) ncat --ssl -l 1337

It will crash inmediatly

'''
def on_crash(target, fuzz_data_logger, session, sock):
    """
    Función que se ejecuta cuando el servidor se cae.
    Guarda información sobre el crash.
    """
    fuzz_data_logger.log_fail("💥 Servidor CRASHEADO 💥")
    with open("crash_log.txt", "a") as f:
        f.write(f"Crash detectado en intento {session.num_mutations}\n")

# Configurar el objetivo
target_ip = "127.0.0.1"
target_port = 1337
target = Target(connection=TCPSocketConnection(target_ip, target_port))  # Se usa TCPSocketConnection en lugar de SocketConnection

# Crear la sesión de fuzzing
session = Session(target=target)

# Definir el formato del paquete a fuzzear
s_initialize("Protocolo_Personalizado")
s_string("COMANDO ", fuzzable=False)  # Enviamos un comando válido
s_delim(" ", fuzzable=False)  # Espacio obligatorio
s_string("DATOS_FUZZ", fuzzable=True)  # Aquí fuzzing

# Asignar la función de crash handler
session.fuzz_one_input_fail_callback = on_crash

# Iniciar el fuzzing
session.connect(s_get("Protocolo_Personalizado"))
session.fuzz()
