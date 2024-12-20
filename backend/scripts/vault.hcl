storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_disable   = 1
}

api_addr = "http://localhost:8200"
cluster_addr = "https://localhost:8201"

# Configuración de logeo
log_level = "info"
disable_mlock = true
