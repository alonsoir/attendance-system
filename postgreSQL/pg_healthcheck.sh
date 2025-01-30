#!/bin/bash

# variables adapted from https://github.com/docker-library/healthcheck
host="$(hostname -i || echo '127.0.0.1')"
user="${POSTGRES_USER:-postgres}"
db="${POSTGRES_DB:-$POSTGRES_USER}"

pg_isready -h "${host}" -p 5432    \
           -d "${db}" -U "${user}" \
           --timeout=5 --quiet || exit 1