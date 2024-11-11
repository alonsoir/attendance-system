# =============================================================================
# VARIABLES Y CONFIGURACIÓN
# =============================================================================

# Versiones y nombres
PYTHON_VERSION=3.12.4
POETRY_VERSION=1.8.4
NODE_VERSION=20
DOCKER_VERSION=20.10.21
NPM_VERSION=8.19.2
APP_NAME=attendance-system
HEROKU_APP_NAME=your-heroku-app-name

# Entorno y archivos
ENV=dev
ENV_FILE=.env-$(ENV)
LOG_FILE=make.log
LOG_DIR=logs
TIMESTAMP=$(shell date '+%Y-%m-%d %H:%M:%S')

# Paths
BACKEND_PATH=attendance_system
FRONTEND_PATH=frontend
DOCS_PATH=docs

# Cargar variables de entorno si existe el archivo
-include $(ENV_FILE)
export

# Colores y Emojis para logs
CYAN=\033[0;36m
GREEN=\033[0;32m
YELLOW=\033[1;33m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m

EMOJI_CHECK=✅
EMOJI_ERROR=❌
EMOJI_WARN=⚠️
EMOJI_INFO=ℹ️

# Crear directorio de logs si no existe
$(shell mkdir -p $(LOG_DIR))

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

validate-versions:
	echo "Validando versiones del sistema"
	@python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))') \
	if [[ "$$python_version" != "$(PYTHON_VERSION)" ]]; then \
		echo "Versión de Python incorrecta. Se requiere $(PYTHON_VERSION), se encontró $$python_version" \
	fi
	node_version=$(node -v | cut -d'v' -f1); \
	if [[ "$node_version" != "$(NODE_VERSION)" ]]; then \
		echo "Versión de Node.js incorrecta. Se requiere $(NODE_VERSION), se encontró v$$node_version" \

	fi
	poetry_version=$(poetry --version | awk '{print $$3}'); \
	if [[ "$poetry_version" != "$(POETRY_VERSION)" ]]; then \
		echo "Versión de Poetry incorrecta. Se requiere $(POETRY_VERSION), se encontró $$poetry_version" \
	fi
	docker_version=$(docker --version | awk '{print $$3}' | cut -d',' -f1); \
	if [[ "$docker_version" != "$(DOCKER_VERSION)" ]]; then \
		echo "Versión de Docker incorrecta. Se requiere $(DOCKER_VERSION), se encontró $$docker_version") \

	fi
	npm_version=$(npm --version); \
	if [[ "$npm_version" != "$(NPM_VERSION)" ]]; then \
		echo "Versión de npm incorrecta. Se requiere $(NPM_VERSION), se encontró $$npm_version") \

	fi
	echo "Todas las versiones son correctas"

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

generate-secret:
	$(call log_info, "Generando nueva SECRET_KEY")
	@if [[ -f $(ENV_FILE) ]]; then \
		cp $(ENV_FILE) $(ENV_FILE).backup-$(shell date +%Y%m%d%H%M%S) \
	fi
	@SECRET_KEY=$$(python3 -c "import secrets; print(secrets.token_urlsafe(32))") \
	echo "SECRET_KEY=$$SECRET_KEY" >> $(ENV_FILE) \
	$(call log_success, "SECRET_KEY generada y añadida en $(ENV_FILE)")

# =============================================================================
# INSTALACIÓN Y CONSTRUCCIÓN
# =============================================================================

# Makefile

# Instalar dependencias de Webpack y otros paquetes de desarrollo
install-webpack-dependencies:
	npm install webpack webpack-cli webpack-dev-server html-webpack-plugin babel-loader style-loader css-loader --save-dev

start:
	npm run dev

install: install-webpack-dependencies check-env check-deps
	$(call log_info, "Iniciando instalación de dependencias")
	@poetry install 2>> $(LOG_DIR)/$(LOG_FILE)
	@cd $(FRONTEND_PATH) && npm install 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Instalación completada")

frontend-build:
	$(call log_info, "Construyendo frontend")
	@cd $(FRONTEND_PATH) && npm run build 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Frontend construido")

# =============================================================================
# DESARROLLO Y TESTING
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
	$(call log_info, "Ejecutando tests")
	@poetry run pytest tests -v 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Tests completados")

# =============================================================================
# DOCKER
# =============================================================================

docker-build: check-env
	$(call log_info, "Construyendo contenedores para $(ENV)")
	@docker-compose --env-file $(ENV_FILE) build 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Contenedores construidos")

docker-run: check-env
	$(call log_info, "Iniciando contenedores para $(ENV)")
	@docker-compose --env-file $(ENV_FILE) up -d 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Contenedores iniciados")

docker-stop:
	$(call log_info, "Deteniendo contenedores")
	@docker-compose down -v 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Contenedores detenidos")

# =============================================================================
# BASE DE DATOS
# =============================================================================

migrate:
	$(call log_info, "Ejecutando migraciones")
	@poetry run alembic upgrade head 2>> $(LOG_DIR)/$(LOG_FILE)
	$(call log_success, "Migraciones completadas")

db-reset:
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
