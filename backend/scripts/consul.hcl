# Deshabilitar verificación de TLS en conexiones entrantes
tls {
  defaults {
    verify_incoming = false
  }
}

# Direcciones de red
bind_addr = "0.0.0.0"
advertise_addr = "{{ GetPrivateIP }}"
client_addr = "0.0.0.0"

# Directorio de datos
data_dir = "/consul/data"

# Configuración de clúster
server = true
bootstrap_expect = 1

# Logs
log_level = "INFO"
enable_syslog = true
