# syntax=docker/dockerfile:1.4

# ============================================================================
# Etapa de escaneo de dependencias
# ============================================================================
FROM python:3.10-slim AS deps-check

WORKDIR /deps-check

COPY backend/pyproject.toml  ./pyproject.toml
COPY backend/poetry.lock ./poetry.lock

RUN pip install --no-cache-dir poetry safety && \
    poetry export -f requirements.txt -o requirements.txt --without-hashes && \
    safety check -r requirements.txt

# ============================================================================
# Etapa de compilación
# ============================================================================
FROM python:3.10-slim AS builder

ARG APP_ENV=development
ARG POETRY_VERSION=1.8.4

ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        curl ca-certificates build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

COPY backend/pyproject.toml ./pyproject.toml
COPY backend/poetry.lock ./poetry.lock

RUN poetry install --no-root $( [ "$APP_ENV" == "production" ] && echo "--no-dev" || echo "" )

COPY backend/ ./

RUN poetry run bandit -r . && \
    poetry run pylint --disable=all --enable=security . || true && \
    poetry run mypy . --strict || true

# ============================================================================
# Etapa de producción
# ============================================================================
FROM python:3.10-slim AS runtime

ARG APP_ENV=development
ENV APP_ENV=$APP_ENV \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PATH="/app/.local/bin:$PATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl ca-certificates netcat-traditional && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app /app

USER apprunner
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

EXPOSE 8000
ENTRYPOINT ["/app/backend-entrypoint.sh"]
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
