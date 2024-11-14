# =============================================================================
# VARIABLES Y CONFIGURACIÓN
# =============================================================================

# Versiones y nombres
PYTHON_VERSION=3.10.15
POETRY_VERSION=1.8.4
NODE_VERSION=22.9.0
DOCKER_VERSION=27.3.1
NPM_VERSION=10.8.3
APP_NAME=attendance-system
HEROKU_APP_NAME=your-heroku-app-name
# Entorno y archivos
ENV=dev
ENV_FILE=.env-$(ENV)
LOG_FILE=make.log
LOG_DIR=logs
TIMESTAMP=$(shell date '+%Y-%m-%d %H:%M:%S')
FRONTEND_PATH=frontend
BACKEND_PATH=attendance_system

# Emojis y Colores
EMOJI_INFO = ℹ️
EMOJI_CHECK = ✅
EMOJI_ERROR = ❌
EMOJI_WARN = ⚠️
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m

# Crear el directorio de logs si no existe
$(LOG_DIR):
	@mkdir -p $(LOG_DIR)

# Definiciones de log
define log
	@echo "[$(TIMESTAMP)] $(1)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

define log_error
	@echo "$(RED)$(EMOJI_ERROR) ERROR: $(1)$(NC)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

define log_success
	@echo "$(GREEN)$(EMOJI_CHECK) $(1)$(NC)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

define log_warn
	@echo "$(YELLOW)$(EMOJI_WARN) WARNING: $(1)$(NC)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

define log_info
	@echo "$(BLUE)$(EMOJI_INFO) $(1)$(NC)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

# Lista de todos los targets que no son archivos
.PHONY: all help install build test run deploy clean docker-build docker-run docker-stop \
        heroku-deploy init check-env check-deps format lint type-check security-check \
        docs test-coverage migrate db-reset frontend-install frontend-build logs check-secrets \
        generate-secret setup-env backup-env show-logs clean-logs rotate-logs validate-versions \
        check-services log-info

# =============================================================================
# FUNCIONES DE LOGGING
# =============================================================================

define log
	@echo "[$(TIMESTAMP)] $(1)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

define log_error
	@echo "$(RED)$(EMOJI_ERROR) ERROR: $(1)$(NC)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

define log_success
	@echo "$(GREEN)$(EMOJI_CHECK) $(1)$(NC)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

define log_warn
	@echo "$(YELLOW)$(EMOJI_WARN) WARNING: $(1)$(NC)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

define log_info
	@echo "$(BLUE)$(EMOJI_INFO) $(1)$(NC)" | tee -a $(LOG_DIR)/$(LOG_FILE)
endef

# Inicializar nuevo archivo de log con cabecera
$(shell echo "\n=== New Make Session Started $(TIMESTAMP) ===" >> $(LOG_DIR)/$(LOG_FILE))

# =============================================================================
# VERIFICACIONES Y VALIDACIONES
# =============================================================================
test-python-version:
    @python_version=$$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))') && \
    if [[ "$$python_version" != "$(PYTHON_VERSION)" ]]; then \
        $(call log_error, "Versión de Python incorrecta. Se requiere $(PYTHON_VERSION), se encontró $$python_version"); \
    fi \
	if [[ "$$python_version" == "$(PYTHON_VERSION)" ]]; then \
        $(call log_success, "Versión de Python correcta. "); \
	fi \

test-node-version:
    @node_version=$$(node -v | cut -d'v' -f1) && \
    if [[ "$$node_version" != "$(NODE_VERSION)" ]]; then \
    	$(call log_error, "Versión de Node.js incorrecta. Se requiere $(NODE_VERSION), se encontró v$$node_version"); \
	fi \

test-poetry-version:
    poetry_version=$(poetry --version | awk '{print $$3}'); \
	if [[ "$poetry_version" != "$(POETRY_VERSION)" ]]; then \
		$(call log_error, "Versión de Poetry incorrecta. Se requiere $(POETRY_VERSION), se encontró $$poetry_version"); \
	fi

test-docker-version:
    docker_version=$(docker --version | awk '{print $$3}' | cut -d',' -f1); \
	if [[ "$docker_version" != "$(DOCKER_VERSION)" ]]; then \
		$(call log_error, "Versión de Docker incorrecta. Se requiere $(DOCKER_VERSION), se encontró $$docker_version"); \
	fi

test-npm-version:
    npm_version=$(npm --version); \
	if [[ "$npm_version" != "$(NPM_VERSION)" ]]; then \
		$(call log_error, "Versión de npm incorrecta. Se requiere $(NPM_VERSION), se encontró $$npm_version"); \
	fi

validate-versions:test-python-version test-node-version test-poetry-version test-docker-version test-npm-version
	$(call log_info, "Validando versiones del sistema")

	$(call log_success, "Todas las versiones son correctas")

check-deps:
	$(call log_info, "Verificando dependencias del sistema")
	@command -v docker >/dev/null 2>&1 || { $(call log_error, "Docker no encontrado"); exit 1; }
	@command -v npm >/dev/null 2>&1 || { $(call log_error, "npm no encontrado"); exit 1; }
	$(call log_success, "Todas las dependencias están instaladas")

check-env:
	$(call log_info, "Verificando archivo de entorno $(ENV_FILE)")
	@if [[ ! -f $(ENV_FILE) ]]; then \
		$(call log_error, "Archivo $(ENV_FILE) no encontrado"); \
		exit 1; \
	fi
	$(call log_success, "Archivo $(ENV_FILE) verificado correctamente")

# Regla para generar SECRET_KEY
generate-secret: $(LOG_DIR)
	$(call log_info, "Generando nueva SECRET_KEY en $(ENV_FILE)")
	@if [[ -f $(ENV_FILE) ]]; then \
		cp $(ENV_FILE) $(ENV_FILE).backup-$(shell date +%Y%m%d%H%M%S); \
	fi
	@SECRET_KEY=$$(python3 -c "import secrets; print(secrets.token_urlsafe(32))") && \
	echo "SECRET_KEY=$$SECRET_KEY" >> $(ENV_FILE) && \
	echo "$(GREEN)✅ SECRET_KEY generada y añadida en $(ENV_FILE)$(NC)"


# =============================================================================
# INSTALACIÓN Y CONSTRUCCIÓN
# =============================================================================

install: $(LOG_DIR) check-env check-deps compile-backend frontend-install-ci frontend-build
	$(call log_info, "Iniciando instalación de dependencias")

	$(call log_success, "Instalación completada")

frontend-install-ci:
	$(call log_info, "Instalando dependencias del frontend para el ci")
	@cd $(FRONTEND_PATH) && npm ci 2>> ../logs/make.log
	$(call log_success, "Dependencias frontend instaladas")

# Eliminar el entorno virtual y el archivo poetry.lock
clean-poetry:
	@rm -rf $(BACKEND_PATH)/.venv
	@cd $(BACKEND_PATH) && rm -f poetry.lock
	@echo "✅ Limpieza completa de entorno poetry realizada."

# Actualizar el archivo poetry.lock sin cambiar versiones de dependencias
poetry-lock:
	@cd $(BACKEND_PATH) && poetry lock --no-update
	@echo "✅ Archivo poetry.lock actualizado."

# Instalar las dependencias en un entorno limpio
poetry-install:
	@cd $(BACKEND_PATH) && poetry install
	@echo "✅ Dependencias instaladas desde poetry.lock."

# Compilación completa en secuencia
compile-backend: clean-poetry poetry-lock poetry-install
	@echo "✅ Compilación de backend completada con éxito."

frontend-build:
	$(call log_info, "Construyendo frontend")
	@cd $(FRONTEND_PATH) && npm run build
	$(call log_success, "Frontend construido")

# =============================================================================
# DESARROLLO Y TESTING
# =============================================================================

format: $(LOG_DIR)
	$(call log_info, "Formateando código")
	@poetry run black $(BACKEND_PATH) tests
	@poetry run isort $(BACKEND_PATH) tests
	@cd $(FRONTEND_PATH) && npm run format
	$(call log_success, "Código formateado")

lint: $(LOG_DIR)
	$(call log_info, "Ejecutando linters")
	@poetry run flake8 $(BACKEND_PATH) tests
	@poetry run pylint $(BACKEND_PATH) tests
	@cd $(FRONTEND_PATH) && npm run lint
	$(call log_success, "Lint completado")

test: $(LOG_DIR)
	$(call log_info, "Ejecutando tests")
	@poetry run pytest tests -v 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Tests completados")

# =============================================================================
# DOCKER
# =============================================================================

docker-build: $(LOG_DIR) check-env
	$(call log_info, "Construyendo contenedores para $(ENV)")
	@docker-compose --env-file $(ENV_FILE) build 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Contenedores construidos")

docker-run: $(LOG_DIR) check-env
	$(call log_info, "Iniciando contenedores para $(ENV)")
	@docker-compose --env-file $(ENV_FILE) up -d 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Contenedores iniciados")

docker-stop: $(LOG_DIR)
	$(call log_info, "Deteniendo contenedores")
	@docker-compose down -v 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Contenedores detenidos")

# =============================================================================
# BASE DE DATOS
# =============================================================================

migrate: $(LOG_DIR)
	$(call log_info, "Ejecutando migraciones")
	@poetry run alembic upgrade head 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Migraciones completadas")

db-reset: $(LOG_DIR)
	$(call log_warn, "Esta operación eliminará todos los datos. ¿Continuar? [y/N]")
	@read confirm; \
	if [[ "$$confirm" == "y" ]]; then \
		$(call log_info, "Reseteando base de datos..."); \
		poetry run alembic downgrade base 2>> $(LOG_DIR)/$(LOG_FILE); \
		poetry run alembic upgrade head 2>> $(LOG_DIR)/$(LOG_FILE); \
		$(call log_success, "Base de datos reseteada"); \
	else \
		$(call log_warn, "Operación cancelada"); \
	fi

# =============================================================================
# EJECUCIÓN
# =============================================================================

run: $(LOG_DIR) check-env check-deps
	$(call log_info, "Iniciando servicios para $(ENV)")
	@docker-compose --env-file $(ENV_FILE) up -d db redis
	$(call log_info, "Iniciando backend")
	@poetry run uvicorn attendance_system.main:app --reload --port $(BACKEND_PORT) &
	$(call log_info, "Iniciando frontend")
	@cd $(FRONTEND_PATH) && npm run start
	$(call log_success, "Servicios iniciados")

# =============================================================================
# AYUDA Y COMANDOS POR DEFECTO
# =============================================================================

help:
	@echo "$(CYAN)Comandos disponibles:$(NC)"
	@echo ""
	@echo "$(BLUE)Configuración:$(NC)"
	@echo "  $(GREEN)make setup-env ENV=[dev|prod]$(NC)    - Configurar entorno inicial"
	@echo "  $(GREEN)make generate-secret$(NC)             - Generar nueva SECRET_KEY"
	@echo ""
	@echo "$(BLUE)Desarrollo:$(NC)"
	@echo "  $(GREEN)make install$(NC)                     - Instalar dependencias"
	@echo "  $(GREEN)make run$(NC)                         - Ejecutar en desarrollo"
	@echo "  $(GREEN)make test$(NC)                        - Ejecutar tests"
	@echo "  $(GREEN)make format$(NC)                      - Formatear código"
	@echo "  $(GREEN)make lint$(NC)                        - Ejecutar linters"
	@echo ""
	@echo "$(BLUE)Docker:$(NC)"
	@echo "  $(GREEN)make docker-build$(NC)                - Construir contenedores"
	@echo "  $(GREEN)make docker-run$(NC)                  - Ejecutar contenedores"
	@echo "  $(GREEN)make docker-stop$(NC)                 - Detener contenedores"
	@echo ""
	@echo "$(BLUE)Base de datos:$(NC)"
	@echo "  $(GREEN)make migrate$(NC)                     - Ejecutar migraciones"
	@echo "  $(GREEN)make db-reset$(NC)                    - Resetear base de datos"
	@echo ""
	@echo "$(BLUE)Mantenimiento:$(NC)"
	@echo "  $(GREEN)make show-logs$(NC)                   - Mostrar logs recientes"

.DEFAULT_GOAL := help