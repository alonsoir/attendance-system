# =============================================================================
# VARIABLES Y CONFIGURACIÓN
# =============================================================================
SHELL := /bin/bash

PYTHON_VERSION = 3.10.15
POETRY_VERSION = 1.8.4
NODE_VERSION = 22.9.0
DOCKER_VERSION = 27.3.1
NPM_VERSION = 10.8.3
APP_NAME = attendance-system
HEROKU_APP_NAME = your-heroku-app-name
ENV = development
ENV_FILE = .env-$(ENV)
LOG_FILE = make.log
LOG_DIR = logs
TIMESTAMP = $(shell date '+%Y-%m-%d %H:%M:%S')
FRONTEND_PATH = frontend
BACKEND_PATH = backend
DOCKER_COMPOSE_FILE = docker-compose.yml

# Emojis y colores (corrección de caracteres de escape para colores)
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m
EMOJI_INFO = ℹ️
EMOJI_CHECK = ✅
EMOJI_ERROR = ❌
EMOJI_WARN = ⚠️

# =============================================================================
# VERIFICACIONES Y DEPENDENCIAS
# =============================================================================

check-docker:
	@echo "$(BLUE)$(EMOJI_INFO) Verificando que Docker esté corriendo...$(NC)"
	@docker info > /dev/null 2>&1 || (echo "$(RED)$(EMOJI_ERROR) Docker no está corriendo!$(NC)" && exit 1)
	@echo "$(GREEN)$(EMOJI_CHECK) Docker está corriendo.$(NC)"

check-enviroment:
	@echo "$(BLUE)$(EMOJI_INFO) Verificando el entorno...$(NC)"
	@if [ -z "$(VIRTUAL_ENV)" ]; then \
		echo "$(RED)$(EMOJI_ERROR) El entorno virtual no está activado!$(NC)"; \
		echo "$(BLUE)$(EMOJI_INFO) Activando el entorno virtual...$(NC)"; \
		poetry shell || source /path/to/your/virtualenv/bin/activate; \
		if [ -z "$(VIRTUAL_ENV)" ]; then \
			echo "$(RED)$(EMOJI_ERROR) No se pudo activar el entorno virtual!$(NC)"; \
			exit 1; \
		else \
			echo "$(GREEN)$(EMOJI_CHECK) El entorno virtual está activado.$(NC)"; \
		fi \
	else \
		echo "$(GREEN)$(EMOJI_CHECK) El entorno virtual está activado.$(NC)"; \
	fi

# =============================================================================
# MODO DESARROLLO
# =============================================================================
dev: check-enviroment check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Levantando la aplicación en modo desarrollo...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) up --build $(APP_NAME)-backend $(APP_NAME)-frontend

# =============================================================================
# MODO PRODUCCIÓN
# =============================================================================
prod: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Levantando la aplicación en modo producción...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) up $(APP_NAME)-backend $(APP_NAME)-frontend

check-deps:
	$(call log_info, "Verificando dependencias del sistema")
	@command -v docker >/dev/null 2>&1 || $(call log_error, "Docker no encontrado")
	@command -v npm >/dev/null 2>&1 || $(call log_error, "npm no encontrado")
	@command -v poetry >/dev/null 2>&1 || $(call log_error, "Poetry no encontrado")
	$(call log_success, "Todas las dependencias están instaladas")

validate-versions:
	$(call log_info, "Validando versiones del sistema")
	@python3 -c 'import sys; assert sys.version.startswith("$(PYTHON_VERSION)")' || \
	$(call log_error, "Python $(PYTHON_VERSION) requerido")
	@node -v | grep -q "v$(NODE_VERSION)" || \
	$(call log_error, "Node.js $(NODE_VERSION) requerido")
	@poetry --version | grep -q "$(POETRY_VERSION)" || \
	$(call log_error, "Poetry $(POETRY_VERSION) requerido")
	@docker --version | grep -q "$(DOCKER_VERSION)" || \
	$(call log_error, "Docker $(DOCKER_VERSION) requerido")
	@npm --version | grep -q "$(NPM_VERSION)" || \
	$(call log_error, "npm $(NPM_VERSION) requerido")
	$(call log_success, "Todas las versiones son correctas")

check-env:
	$(call log_info, "Verificando archivo de entorno $(ENV_FILE)")
	@if [[ ! -f $(ENV_FILE) ]]; then \
		$(call log_error, "Archivo $(ENV_FILE) no encontrado"); \
		exit 1; \
	fi
	$(call log_success, "Archivo $(ENV_FILE) verificado correctamente")

generate-secret: $(LOG_DIR)
	$(call log_info, "Generando nueva SECRET_KEY en $(ENV_FILE)")
	@if [[ -f $(ENV_FILE) ]]; then \
		cp $(ENV_FILE) $(ENV_FILE).backup-$(shell date +%Y%m%d%H%M%S); \
	fi
	@SECRET_KEY=$$(python3 -c "import secrets; print(secrets.token_urlsafe(32))") && \
	echo "SECRET_KEY=$$SECRET_KEY" >> $(ENV_FILE) && \
	$(call log_success, "SECRET_KEY generada y añadida en $(ENV_FILE)")

# =============================================================================
# INSTALACIÓN Y CONSTRUCCIÓN
# =============================================================================

install: check-enviroment $(LOG_DIR) check-deps backend-build frontend-install frontend-build
	$(call log_success, "Instalación completada")

backend-build:
	$(call log_info, "Construyendo backend")
	@cd $(BACKEND_PATH) && poetry install
	$(call log_success, "Backend construido")

frontend-install:
	$(call log_info, "Instalando dependencias del frontend")
	@cd $(FRONTEND_PATH) && npm ci
	$(call log_success, "Dependencias frontend instaladas")

frontend-build:
	$(call log_info, "Construyendo frontend")
	@cd $(FRONTEND_PATH) && npm run build
	$(call log_success, "Frontend construido")

# =============================================================================
# OTRAS REGLAS
# =============================================================================
run: check-enviroment check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando la aplicación...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) up $(APP_NAME)-backend $(APP_NAME)-frontend

# =============================================================================
# FORMATO Y LINTERS
# =============================================================================
# =============================================================================
# FASE DE PRUEBAS
# =============================================================================




format:
	$(call log_info, "Formateando código")
	@poetry run black $(BACKEND_PATH) tests
	@poetry run isort $(BACKEND_PATH) tests
	@cd $(FRONTEND_PATH) && npm run format
	$(call log_success, "Código formateado")

lint:
	$(call log_info, "Ejecutando linters")
	@poetry run flake8 $(BACKEND_PATH) tests
	@poetry run pylint $(BACKEND_PATH) tests
	@cd $(FRONTEND_PATH) && npm run lint
	$(call log_success, "Lint completado")

test:
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando las pruebas del backend...$(NC)"
	@poetry run pytest tests > $(LOG_DIR)/backend-test.log; tail -n 10 $(LOG_DIR)/backend-test.log


# Ejecuta solo los tests unitarios
tests-unit:
	@poetry run pytest tests/unit/ > $(LOG_DIR)/backend-unit-test.log; tail -n 10 $(LOG_DIR)/backend-unit-test.log

# Ejecuta solo los tests de integración
tests-integration:
	@poetry run pytest tests/integration/ > $(LOG_DIR)/backend-integration-test.log; tail -n 10 $(LOG_DIR)/backend-integration-test.log
# =============================================================================
# DOCKER
# =============================================================================
test-in-docker: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando las pruebas del backend...$(NC)"
	@docker-compose exec $(APP_NAME)-backend pytest /app/tests > $(LOG_DIR)/backend-test.log; tail -n 10 $(LOG_DIR)/backend-test.log

docker-build: check-env
	$(call log_info, "Construyendo contenedores")
	@docker-compose --env-file $(ENV_FILE) -f $(DOCKER_COMPOSE_FILE) build
	$(call log_success, "Contenedores construidos")

docker-run: check-env
	$(call log_info, "Iniciando contenedores")
	@docker-compose --env-file $(ENV_FILE) -f $(DOCKER_COMPOSE_FILE) up -d
	$(call log_success, "Contenedores iniciados")

docker-stop:
	$(call log_info, "Deteniendo contenedores")
	@docker-compose -f $(DOCKER_COMPOSE_FILE) down -v
	$(call log_success, "Contenedores detenidos")

# =============================================================================
# OTROS
# =============================================================================

help:
	@echo "Comandos disponibles:"
	@echo "  make install            - Instalar dependencias y construir proyecto"
	@echo "  make validate-versions  - Validar versiones de herramientas"
	@echo "  make docker-build       - Construir contenedores Docker"
	@echo "  make docker-run         - Iniciar contenedores Docker"
	@echo "  make docker-stop        - Detener contenedores Docker"
	@echo "  make format             - Formatear código"
	@echo "  make lint               - Ejecutar linters"

.DEFAULT_GOAL := help
