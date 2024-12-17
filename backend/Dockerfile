# ============================================================================
# Etapa de compilación
# ============================================================================
FROM python:3.10-slim AS builder

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
        lsb-release && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Instalar poetry con verificación
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && echo "export PATH=/opt/poetry/bin:$PATH" >> ~/.bashrc \
    && source ~/.bashrc \
    && poetry --version

# Añadir Poetry al PATH para la etapa de compilación
ENV PATH="/opt/poetry/bin:$PATH"

# Verificar que Poetry está instalado correctamente
RUN poetry --version

# Instalar cliente de Vault
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update \
    && apt-get install -y vault \
    && rm -rf /var/lib/apt/lists/*

# Carpeta de trabajo
WORKDIR /app

# Copiar archivos de configuración de seguridad
COPY --chown=root:root security/seccomp-profile.json /etc/docker/seccomp-profile.json

# Copiar solo los archivos necesarios para la instalación de dependencias
COPY --chown=nobody:nogroup ../pyproject.toml ./pyproject.toml
COPY --chown=nobody:nogroup ../poetry.lock ./poetry.lock

# Instalar dependencias según el entorno
RUN if [ "$APP_ENV" = "production" ] ; then \
        /opt/poetry/bin/poetry install --no-dev --no-root ; \
    else \
        /opt/poetry/bin/poetry install --no-root ; \
    fi

# Copiar el código fuente
COPY --chown=nobody:nogroup . ./

# Verificaciones de seguridad del código
#RUN poetry run pip install safety bandit pylint mypy && \
#    poetry run safety check && \
#    poetry run bandit -r . -ll && \
#    find . -type f -name "*.py" -not -path "./tests/*" -exec poetry run pylint {} + && \
#    poetry run mypy .

