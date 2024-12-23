storage "consul" {
  address = "http://consul:8500"
}

listener "tcp" {
  address       = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_disable   = 1
}

api_addr = "http://vault:8200"
cluster_addr = "https://vault:8201"
log_level = "info"
disable_mlock = true
