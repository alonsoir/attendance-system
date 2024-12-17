# ============================================================================
# Etapa de compilación
# ============================================================================
FROM python:3.10-slim as builder

# Argumentos de construcción
ARG APP_ENV=development
ARG POETRY_VERSION=1.8.4

# Establecer variables de entorno para la construcción
ENV POETRY_VERSION=${POETRY_VERSION} \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME="/opt/poetry" \
    # Configurar pip para modo seguro
    PIP_NO_CACHE_DIR=1 \
    PIP_NO_INPUT=1 \
    # Asegurar que pip use HTTPS
    PIP_INDEX_URL=https://pypi.org/simple \
    PIP_TRUSTED_HOST=pypi.org

# Verificar la integridad de los paquetes
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Instalar dependencias del sistema con la mínima superficie de ataque
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        gnupg \
        ca-certificates \
        jq \
        libseccomp-dev \
        apparmor \
        auditd \
        fail2ban \
        rkhunter \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instalar poetry con verificación
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false

# Instalar cliente de Vault
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update \
    && apt-get install -y vault \
    && rm -rf /var/lib/apt/lists/*

# Carpeta de trabajo
WORKDIR /app

# Copiar archivos de configuración de seguridad
COPY --chown=root:root ./attendance_system/backend/security/apparmor-profile /etc/apparmor.d/
COPY --chown=root:root ./attendance_system/backend/security/seccomp-profile.json /etc/docker/seccomp-profile.json
COPY --chown=root:root ./attendance_system/backend/security/jail.local /etc/fail2ban/jail.local
COPY --chown=root:root ./attendance_system/backend/security/audit.rules /etc/audit/rules.d/audit.rules

# Configurar medidas de seguridad
RUN apparmor_parser -r -W /etc/apparmor.d/apparmor-profile && \
    service fail2ban restart && \
    auditctl -R /etc/audit/rules.d/audit.rules

# Copiar solo los archivos necesarios para la instalación de dependencias
COPY --chown=nobody:nogroup ./attendance_system/backend/pyproject.toml ./attendance_system/backend/poetry.lock ./

# Instalar dependencias según el entorno con comprobación de hashes
RUN if [ "$APP_ENV" = "production" ] ; then \
        $POETRY_HOME/bin/poetry install --no-dev --no-root --verify ; \
    else \
        $POETRY_HOME/bin/poetry install --no-root --verify ; \
    fi

# Copiar el código fuente
COPY --chown=nobody:nogroup ./attendance_system/backend ./

# Verificaciones de seguridad del código
RUN poetry run pip install safety bandit pylint mypy && \
    poetry run safety check && \
    poetry run bandit -r . -ll && \
    find . -type f -name "*.py" -not -path "./tests/*" -exec poetry run pylint {} + && \
    poetry run mypy . && \
    poetry run pip uninstall -y safety bandit pylint mypy

# ============================================================================
# Etapa de producción
# ============================================================================
FROM python:3.10-slim AS runtime

# Argumentos y variables de entorno
ARG APP_ENV=development
ENV APP_ENV=$APP_ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH" \
    # Variables de seguridad adicionales
    PYTHONHASHSEED=random \
    PYTHONPROFILEIMPORTTIME=0

# Instalar dependencias del sistema necesarias
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl \
        netcat-traditional \
        ca-certificates \
        jq \
        libseccomp-dev \
        apparmor \
        auditd \
        fail2ban \
        rkhunter \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Instalar cliente de Vault
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update \
    && apt-get install -y vault \
    && rm -rf /var/lib/apt/lists/*

# Carpeta de trabajo
WORKDIR /app

# Copiar configuraciones de seguridad
COPY --chown=root:root ./attendance_system/backend/security/apparmor-profile /etc/apparmor.d/
COPY --chown=root:root ./attendance_system/backend/security/seccomp-profile.json /etc/docker/seccomp-profile.json
COPY --chown=root:root ./attendance_system/backend/security/jail.local /etc/fail2ban/jail.local
COPY --chown=root:root ./attendance_system/backend/security/audit.rules /etc/audit/rules.d/audit.rules

# Configurar medidas de seguridad
RUN apparmor_parser -r -W /etc/apparmor.d/apparmor-profile && \
    service fail2ban restart && \
    auditctl -R /etc/audit/rules.d/audit.rules

# Copiar dependencias y código desde la etapa de compilación
COPY --from=builder --chown=nobody:nogroup /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder --chown=nobody:nogroup /app /app

# Crear usuario no root con el mínimo privilegio necesario
RUN groupadd -r apprunner --gid=999 && \
    useradd -r -g apprunner --uid=999 -d /app apprunner && \
    # Establecer permisos restrictivos
    chmod -R 550 /app && \
    # Asegurar que los archivos sean de solo lectura
    find /app -type f -exec chmod 440 {} \; && \
    # Crear directorio para logs
    mkdir -p /app/logs && \
    chown -R apprunner:apprunner /app/logs && \
    chmod 760 /app/logs

# Copiar y configurar scripts
COPY --chown=apprunner:apprunner ./attendance_system/backend/scripts/fetch-secrets.sh \
                                ./attendance_system/backend/scripts/secure-env.sh \
                                ./attendance_system/backend/scripts/rotate-secrets.sh \
                                /app/scripts/
RUN chmod 500 /app/scripts/*.sh

# Cambiar al usuario no privilegiado
USER apprunner:apprunner

# Exponer puerto
EXPOSE 8000

# Healthcheck mejorado
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl --fail --silent --max-time 2 http://localhost:8000/health || exit 1

# Script de inicio
COPY --chown=apprunner:apprunner ./attendance_system/backend/backend-entrypoint.sh /app/backend-entrypoint.sh
RUN chmod 550 /app/backend-entrypoint.sh

# Definir directorio de trabajo como solo lectura
VOLUME ["/app"]

# Ejecutar como usuario no privilegiado
ENTRYPOINT ["/app/backend-entrypoint.sh"]