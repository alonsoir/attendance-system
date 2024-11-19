# Etapa de compilación
FROM python:3.10-slim as builder

# Argumentos de construcción
ARG APP_ENV=development

# Instalar poetry
ENV POETRY_VERSION=1.8.4
RUN pip install "poetry==$POETRY_VERSION"

# Configurar poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Carpeta de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY pyproject.toml poetry.lock ./

# Instalar dependencias según el entorno
RUN if [ "$APP_ENV" = "production" ] ; then \
        poetry install --no-dev --no-root ; \
    else \
        poetry install --no-root ; \
    fi

# Copiar código fuente
COPY . .

# Etapa de producción
FROM python:3.10-slim

# Argumentos y variables de entorno
ARG APP_ENV=development
ENV APP_ENV=$APP_ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.local/bin:$PATH"

# Carpeta de trabajo
WORKDIR /app

# Copiar dependencias y código desde la etapa de compilación
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /app /app

# Exponer puerto
EXPOSE 8000

# Script de inicio
COPY backend-entrypoint.sh /backend-entrypoint.sh
RUN chmod +x /backend-entrypoint.sh

ENTRYPOINT ["/backend-entrypoint.sh"]
