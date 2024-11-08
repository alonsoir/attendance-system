# Variables de versiones
PYTHON_VERSION := 3.10
POETRY_VERSION := 1.8.4
NODE_VERSION := 20.x
APP_NAME := attendance-system
HEROKU_APP_NAME := your-heroku-app-name

# Determinar el entorno
ENV ?= dev
ENV_FILE := .env-$(ENV)

# Cargar variables de entorno
include $(ENV_FILE)
export

# Colores para output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Emojis
EMOJI_CHECK := ✅
EMOJI_ERROR := ❌
EMOJI_WARN := ⚠️
EMOJI_INFO := ℹ️

# Paths
BACKEND_PATH := attendance_system
FRONTEND_PATH := frontend
DOCS_PATH := docs

# Lista de todos los targets que no son archivos
.PHONY: help install build test run deploy clean docker-build docker-run docker-stop \
        heroku-deploy init check-env check-deps format lint type-check security-check \
        docs test-coverage migrate db-reset frontend-install frontend-build logs check-secrets

# Verificar secrets
check-secrets:
	@echo "$(YELLOW)Verificando archivos por secrets...$(NC)"
	@if command -v ggshield >/dev/null 2>&1; then \
		ggshield secret scan path .; \
	else \
		echo "$(RED)ggshield no está instalado. Instálalo con: pip install ggshield$(NC)"; \
		exit 1; \
	fi

# Verificar archivo de entorno
check-env: check-secrets
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "$(RED)$(EMOJI_ERROR) Error: Archivo $(ENV_FILE) no encontrado$(NC)"; \
		echo "$(YELLOW)$(EMOJI_INFO) Copia $(ENV_FILE).example a $(ENV_FILE) y configura tus variables$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Verificando variables requeridas en $(ENV_FILE)...$(NC)"
	@source $(ENV_FILE) && [ -z "$$SECRET_KEY" ] && echo "$(RED)ERROR: SECRET_KEY no está configurada$(NC)" && exit 1 || true
	@source $(ENV_FILE) && [ -z "$$ANTHROPIC_API_KEY" ] && echo "$(RED)ERROR: ANTHROPIC_API_KEY no está configurada$(NC)" && exit 1 || true
	@echo "$(GREEN)$(EMOJI_CHECK) Archivo $(ENV_FILE) verificado correctamente$(NC)"

# Verificar dependencias del sistema
check-deps:
	@echo "$(BLUE)$(EMOJI_INFO) Verificando dependencias del sistema...$(NC)"
	@command -v python$(PYTHON_VERSION) >/dev/null 2>&1 || { echo "$(RED)$(EMOJI_ERROR) Python $(PYTHON_VERSION) no encontrado$(NC)"; exit 1; }
	@command -v docker >/dev/null 2>&1 || { echo "$(RED)$(EMOJI_ERROR) Docker no encontrado$(NC)"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "$(RED)$(EMOJI_ERROR) Node.js no encontrado$(NC)"; exit 1; }
	@command -v npm >/dev/null 2>&1 || { echo "$(RED)$(EMOJI_ERROR) npm no encontrado$(NC)"; exit 1; }
	@echo "$(GREEN)$(EMOJI_CHECK) Todas las dependencias están instaladas$(NC)"

# Ayuda
help:
	@echo "$(CYAN)Comandos disponibles:$(NC)"
	@echo ""
	@echo "$(BLUE)Instalación y Configuración:$(NC)"
	@echo "  $(GREEN)make init ENV=[dev|prod]$(NC)        - Inicializar proyecto completo"
	@echo "  $(GREEN)make install ENV=[dev|prod]$(NC)     - Instalar dependencias"
	@echo "  $(GREEN)make check-deps$(NC)                 - Verificar dependencias del sistema"
	@echo "  $(GREEN)make check-secrets$(NC)              - Verificar secrets en el código"
	@echo ""
	@echo "$(BLUE)Desarrollo:$(NC)"
	@echo "  $(GREEN)make run ENV=[dev|prod]$(NC)         - Ejecutar en desarrollo"
	@echo "  $(GREEN)make format$(NC)                     - Formatear código"
	@echo "  $(GREEN)make lint$(NC)                       - Ejecutar linters"
	@echo "  $(GREEN)make type-check$(NC)                 - Verificar tipos"
	@echo ""
	@echo "$(BLUE)Testing:$(NC)"
	@echo "  $(GREEN)make test ENV=[dev|prod]$(NC)        - Ejecutar todos los tests"
	@echo "  $(GREEN)make test-unit$(NC)                  - Ejecutar tests unitarios"
	@echo "  $(GREEN)make test-integration$(NC)           - Ejecutar tests de integración"
	@echo "  $(GREEN)make test-coverage$(NC)              - Generar reporte de cobertura"
	@echo ""
	@echo "$(BLUE)Docker:$(NC)"
	@echo "  $(GREEN)make docker-build ENV=[dev|prod]$(NC) - Construir contenedores"
	@echo "  $(GREEN)make docker-run ENV=[dev|prod]$(NC)   - Ejecutar contenedores"
	@echo "  $(GREEN)make docker-stop$(NC)                - Detener contenedores"
	@echo "  $(GREEN)make logs$(NC)                       - Ver logs de contenedores"
	@echo ""
	@echo "$(BLUE)Base de Datos:$(NC)"
	@echo "  $(GREEN)make migrate ENV=[dev|prod]$(NC)     - Ejecutar migraciones"
	@echo "  $(GREEN)make db-reset ENV=[dev|prod]$(NC)    - Resetear base de datos"
	@echo ""
	@echo "$(BLUE)Despliegue:$(NC)"
	@echo "  $(GREEN)make deploy ENV=[dev|prod]$(NC)      - Desplegar en producción"
	@echo "  $(GREEN)make heroku-deploy ENV=prod$(NC)     - Desplegar en Heroku"

# Instalación
install: check-env check-deps
	@echo "$(YELLOW)Instalando poetry...$(NC)"
	curl -sSL https://install.python-poetry.org | python3 -
	@echo "$(YELLOW)Configurando poetry...$(NC)"
	poetry config virtualenvs.in-project true
	@echo "$(YELLOW)Instalando dependencias de Python...$(NC)"
	poetry install $(if $(filter prod,$(ENV)),--only main$(comma)prod,)
	@echo "$(YELLOW)Instalando dependencias de frontend...$(NC)"
	$(MAKE) frontend-install ENV=$(ENV)
	@echo "$(GREEN)$(EMOJI_CHECK) Instalación completada$(NC)"

# Frontend
frontend-install:
	@echo "$(YELLOW)Instalando dependencias de frontend...$(NC)"
	cd $(FRONTEND_PATH) && npm install $(if $(filter prod,$(ENV)),--production,)

frontend-build:
	@echo "$(YELLOW)Construyendo frontend...$(NC)"
	cd $(FRONTEND_PATH) && npm run build

# Formateo y linting
format:
	@echo "$(YELLOW)Formateando código...$(NC)"
	poetry run black $(BACKEND_PATH) tests
	poetry run isort $(BACKEND_PATH) tests
	cd $(FRONTEND_PATH) && npm run format

lint:
	@echo "$(YELLOW)Ejecutando linters...$(NC)"
	poetry run flake8 $(BACKEND_PATH) tests
	poetry run pylint $(BACKEND_PATH) tests
	cd $(FRONTEND_PATH) && npm run lint

type-check:
	@echo "$(YELLOW)Verificando tipos...$(NC)"
	poetry run mypy $(BACKEND_PATH)

security-check:
	@echo "$(YELLOW)Ejecutando verificaciones de seguridad...$(NC)"
	poetry run safety check
	poetry run bandit -r $(BACKEND_PATH)
	cd $(FRONTEND_PATH) && npm audit
	$(MAKE) check-secrets

# Testing
test: test-unit test-integration

test-unit:
	@echo "$(YELLOW)Ejecutando tests unitarios...$(NC)"
	poetry run pytest tests/unit -v

test-integration:
	@echo "$(YELLOW)Ejecutando tests de integración...$(NC)"
	poetry run pytest tests/integration -v

test-coverage:
	@echo "$(YELLOW)Generando reporte de cobertura...$(NC)"
	poetry run pytest --cov=$(BACKEND_PATH) --cov-report=html --cov-report=term-missing

# Docker
docker-build: check-env
	@echo "$(YELLOW)Construyendo contenedores para $(ENV)...$(NC)"
	docker-compose --env-file $(ENV_FILE) build

docker-run: check-env
	@echo "$(YELLOW)Iniciando contenedores para $(ENV)...$(NC)"
	docker-compose --env-file $(ENV_FILE) up -d

docker-stop:
	@echo "$(YELLOW)Deteniendo contenedores...$(NC)"
	docker-compose down -v

# Logs
logs:
	@echo "$(YELLOW)Mostrando logs de contenedores...$(NC)"
	docker-compose --env-file $(ENV_FILE) logs -f

# Base de datos
migrate: check-env
	@echo "$(YELLOW)Ejecutando migraciones...$(NC)"
	poetry run alembic upgrade head

db-reset: check-env
	@echo "$(YELLOW)Reseteando base de datos...$(NC)"
	poetry run alembic downgrade base
	poetry run alembic upgrade head

# Desarrollo
run: check-env
	@echo "$(YELLOW)Iniciando servicios para $(ENV)...$(NC)"
	docker-compose --env-file $(ENV_FILE) up -d db redis
	@echo "$(YELLOW)Iniciando backend...$(NC)"
	poetry run uvicorn attendance_system.main:app --reload --port $(BACKEND_PORT) &
	@echo "$(YELLOW)Iniciando frontend...$(NC)"
	cd $(FRONTEND_PATH) && npm run dev

# Documentación
docs:
	@echo "$(YELLOW)Generando documentación...$(NC)"
	poetry run sphinx-build -b html $(DOCS_PATH)/source $(DOCS_PATH)/build

# Limpieza
clean:
	@echo "$(YELLOW)Limpiando archivos temporales...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf $(FRONTEND_PATH)/node_modules
	rm -rf $(FRONTEND_PATH)/dist
	rm -rf $(DOCS_PATH)/build
	@echo "$(GREEN)$(EMOJI_CHECK) Limpieza completada$(NC)"

# Deploy
deploy: check-env
	@if [ "$(ENV)" = "prod" ]; then \
		$(MAKE) security-check && \
		$(MAKE) test && \
		$(MAKE) docker-build ENV=prod && \
		$(MAKE) docker-run ENV=prod; \
	else \
		echo "$(RED)$(EMOJI_ERROR) El deploy solo está disponible para producción$(NC)"; \
		exit 1; \
	fi

# Heroku deploy
heroku-deploy: check-env
	@if [ "$(ENV)" = "prod" ]; then \
		echo "$(YELLOW)Desplegando en Heroku...$(NC)" && \
		heroku container:login && \
		heroku container:push web --app $(HEROKU_APP_NAME) && \
		heroku container:release web --app $(HEROKU_APP_NAME); \
	else \
		echo "$(RED)$(EMOJI_ERROR) El deploy a Heroku solo está disponible para producción$(NC)"; \
		exit 1; \
	fi

# Inicialización del proyecto
init: check-env check-deps install migrate
	@echo "$(GREEN)$(EMOJI_CHECK) Proyecto inicializado correctamente para $(ENV)$(NC)"

# Por defecto usar entorno de desarrollo
.DEFAULT_GOAL := help

# Heroku
heroku-deploy: check-env
	@if [ "$(ENV)" = "prod" ]; then \
		echo "$(YELLOW)Verificando configuración de Heroku...$(NC)" && \
		if [ -z "$$HEROKU_API_KEY" ]; then \
			echo "$(RED)ERROR: HEROKU_API_KEY no está configurada$(NC)" && exit 1; \
		fi && \
		if [ -z "$(HEROKU_APP_NAME)" ]; then \
			echo "$(RED)ERROR: HEROKU_APP_NAME no está configurado$(NC)" && exit 1; \
		fi && \
		echo "$(YELLOW)Configurando Heroku...$(NC)" && \
		heroku container:login && \
		heroku stack:set container --app $(HEROKU_APP_NAME) && \
		echo "$(YELLOW)Construyendo y subiendo contenedores...$(NC)" && \
		heroku container:push web worker --app $(HEROKU_APP_NAME) && \
		echo "$(YELLOW)Liberando contenedores...$(NC)" && \
		heroku container:release web worker --app $(HEROKU_APP_NAME) && \
		echo "$(YELLOW)Ejecutando migraciones...$(NC)" && \
		heroku run alembic upgrade head --app $(HEROKU_APP_NAME) && \
		echo "$(GREEN)$(EMOJI_CHECK) Despliegue completado$(NC)"; \
	else \
		echo "$(RED)$(EMOJI_ERROR) El deploy a Heroku solo está disponible para producción$(NC)"; \
		exit 1; \
	fi

heroku-logs:
	@if [ -z "$(HEROKU_APP_NAME)" ]; then \
		echo "$(RED)ERROR: HEROKU_APP_NAME no está configurado$(NC)" && exit 1; \
	fi
	@heroku logs --tail --app $(HEROKU_APP_NAME)

heroku-bash:
	@if [ -z "$(HEROKU_APP_NAME)" ]; then \
		echo "$(RED)ERROR: HEROKU_APP_NAME no está configurado$(NC)" && exit 1; \
	fi
	@heroku run bash --app $(HEROKU_APP_NAME)

heroku-db-reset: check-env
	@if [ "$(ENV)" = "prod" ]; then \
		if [ -z "$(HEROKU_APP_NAME)" ]; then \
			echo "$(RED)ERROR: HEROKU_APP_NAME no está configurado$(NC)" && exit 1; \
		fi && \
		echo "$(RED)¿Estás seguro de que quieres resetear la base de datos de producción? [y/N]$(NC)" && \
		read ans && [ $${ans:-N} = y ] && \
		heroku pg:reset --app $(HEROKU_APP_NAME) --confirm $(HEROKU_APP_NAME) && \
		heroku run alembic upgrade head --app $(HEROKU_APP_NAME); \
	else \
		echo "$(RED)$(EMOJI_ERROR) Este comando solo está disponible para producción$(NC)"; \
		exit 1; \
	fi
