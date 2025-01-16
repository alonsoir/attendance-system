# Deshabilitar verificación de TLS en conexiones entrantes
tls {
  defaults {
    verify_incoming = false
  }
}

# Direcciones de red
bind_addr = "0.0.0.0"
advertise_addr = "127.0.0.1"  # Usa la IP privada del contenedor o nodo
client_addr = "0.0.0.0"

# Directorio de datos
data_dir = "/consul/data"

# Configuración de clúster
server = true
bootstrap_expect = 1

# Logs
log_level = "INFO"
enable_syslog = false  # Desactiva si no estás utilizando syslog
