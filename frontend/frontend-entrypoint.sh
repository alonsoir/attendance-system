#!/bin/bash
set -e

echo "Iniciando el servidor frontend..."
exec nginx -g "daemon off;"
