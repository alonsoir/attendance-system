# syntax=docker/dockerfile:1.4
# ============================================================================
# Etapa de escaneo de dependencias
# ============================================================================
FROM python:3.10-slim AS deps-check

WORKDIR /deps-check
COPY pyproject.toml poetry.lock ./

# Verificar vulnerabilidades en dependencias
RUN pip install --no-cache-dir safety && \
    pip freeze > requirements.txt && \
    safety check -r requirements.txt

# ============================================================================
# Etapa de escaneo de seguridad
# ============================================================================
FROM aquasec/trivy:latest AS security-scan

WORKDIR /scan
COPY . .
RUN trivy filesystem --severity HIGH,CRITICAL . && \
    trivy config --severity HIGH,CRITICAL .

# ============================================================================
# Etapa de compilación
# ============================================================================
FROM python:3.10-slim AS builder

# Argumentos de construcción
ARG APP_ENV=development
ARG POETRY_VERSION=1.8.4

# Variables de entorno de construcción
ENV POETRY_VERSION=${POETRY_VERSION} \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    # Configuración segura de pip
    PIP_NO_CACHE_DIR=1 \
    PIP_NO_INPUT=1 \
    PIP_INDEX_URL=https://pypi.org/simple \
    PIP_TRUSTED_HOST=pypi.org \
    # Configuración segura de Python
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONNOUSERSITE=1

# Habilitar BuildKit
ENV DOCKER_BUILDKIT=1

# Verificar integridad de paquetes
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Instalar dependencias mínimas necesarias
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        build-essential \
        jq && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Instalar Poetry usando pip
RUN pip install --no-cache-dir poetry==${POETRY_VERSION} \
    --disable-pip-version-check \
    --no-warn-script-location \
    --no-warn-conflicts && \
    poetry config virtualenvs.create false

WORKDIR /app

# Copiar y verificar archivos de dependencias
COPY --chown=nobody:nogroup pyproject.toml poetry.lock ./

# Verificar dependencias e instalar herramientas de auditoría
RUN pip install --no-cache-dir pip-audit && \
    poetry self add poetry-plugin-export && \
    poetry check && \
    poetry export -f requirements.txt -o /tmp/requirements.txt && \
    pip-audit -r /tmp/requirements.txt --progress-spinner on -o /tmp/pip-audit.json || true

# Instalar dependencias con verificación
RUN if [ "$APP_ENV" == "production" ] ; then \
        poetry install --no-dev --no-root ; \
    else \
        poetry install --no-root ; \
    fi

# Copiar código fuente
COPY --chown=nobody:nogroup . .

# Análisis estático y verificaciones de seguridad
RUN poetry run pip install bandit pylint mypy && \
    poetry run bandit -r . -ll -ii && \
    poetry run pylint --disable=all --enable=security,authentication . || true && \
    poetry run mypy . --strict || true

# ============================================================================
# Etapa de producción
# ============================================================================
FROM python:3.10-slim AS runtime

ARG APP_ENV=development
ENV APP_ENV=$APP_ENV \
    # Configuración segura de Python
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONNOUSERSITE=1 \
    PYTHONSAFEPATH=1 \
    PATH="/app/.local/bin:$PATH" \
    # Configuración de runtime
    PYTHON_EGG_CACHE="/tmp/python-eggs" \
    TMPDIR="/tmp"

# Instalar solo dependencias esenciales
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        netcat-traditional && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# Copiar solo los archivos necesarios
COPY --from=builder --chown=nobody:nogroup /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder --chown=nobody:nogroup /app /app

# Generar y verificar checksums
RUN find /app -type f -exec sha256sum {} \; > /app/checksums.txt && \
    chmod 400 /app/checksums.txt

# Crear usuario no privilegiado
RUN groupadd -r apprunner --gid=999 && \
    useradd -r -g apprunner --uid=999 -d /app apprunner -s /usr/sbin/nologin && \
    mkdir -p /app/logs /tmp/python-eggs && \
    chown -R apprunner:apprunner /app/logs /tmp/python-eggs && \
    chmod 750 /app/logs && \
    chmod 700 /tmp/python-eggs && \
    # Establecer permisos restrictivos
    find /app -type f -exec chmod 440 {} \; && \
    find /app -type d -exec chmod 550 {} \;

# Copiar y configurar scripts
COPY --chown=apprunner:apprunner scripts/fetch-secrets.sh \
                                scripts/init-vault.sh \
                                scripts/rotate-secrets.sh \
                                scripts/secure-env.sh \
                                /app/scripts/
RUN chmod 500 /app/scripts/*.sh

COPY --chown=apprunner:apprunner backend-entrypoint.sh /app/backend-entrypoint.sh
RUN chmod 500 /app/backend-entrypoint.sh

USER apprunner:apprunner

# Healthcheck robusto
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl --fail --silent --max-time 2 --retry 3 http://localhost:8000/health || exit 1

# Volumen solo lectura
VOLUME ["/app"]

# Solo exponer puerto necesario
EXPOSE 8000

ENTRYPOINT ["/app/backend-entrypoint.sh"]
CMD ["uvicorn", "backend.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*", \
     "--limit-concurrency", "1000", \
     "--backlog", "2048", \
     "--timeout-keep-alive", "5", \
     "--use-colors", "false", \
     "--http", "h11", \
     "--loop", "uvloop", \
     "--no-access-log"]