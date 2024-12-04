# =============================================================================
# DECLARACIÓN DE PHONY TARGETS
# =============================================================================
.PHONY: help check-docker check-environment check-deps validate-versions check-env \
        generate-secret install backend-build frontend-install frontend-build \
        dev prod run format lint test tests-unit tests-integration \
        test-with-containers test-in-docker docker-build docker-run docker-stop \
        db-init db-reset db-seed db-setup

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
ENV = development
ENV_FILE = .env-$(ENV)
LOG_FILE = make.log
LOG_DIR = logs
FRONTEND_PATH = frontend
BACKEND_PATH = backend
DOCKER_COMPOSE_FILE = docker-compose.yml

# Colores y emojis
include mk/colors.mk

# =============================================================================
# VERIFICACIONES BÁSICAS
# =============================================================================
check-docker:
	@echo "$(BLUE)$(EMOJI_INFO) Verificando Docker...$(NC)"
	@docker info > /dev/null 2>&1 || (echo "$(RED)$(EMOJI_ERROR) Docker no está corriendo!$(NC)" && exit 1)
	@echo "$(GREEN)$(EMOJI_CHECK) Docker está corriendo.$(NC)"

check-environment:
	@echo "$(BLUE)$(EMOJI_INFO) Verificando entorno virtual...$(NC)"
	@if [ -z "$(VIRTUAL_ENV)" ]; then \
		poetry shell || (echo "$(RED)$(EMOJI_ERROR) No se pudo activar el entorno virtual!$(NC)" && exit 1); \
	fi
	@echo "$(GREEN)$(EMOJI_CHECK) Entorno virtual activo.$(NC)"

# =============================================================================
# VERIFICACIONES DE SISTEMA
# =============================================================================
check-deps: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Verificando dependencias...$(NC)"
	@command -v docker >/dev/null 2>&1 || (echo "$(RED)$(EMOJI_ERROR) Docker no encontrado$(NC)" && exit 1)
	@command -v npm >/dev/null 2>&1 || (echo "$(RED)$(EMOJI_ERROR) npm no encontrado$(NC)" && exit 1)
	@command -v poetry >/dev/null 2>&1 || (echo "$(RED)$(EMOJI_ERROR) Poetry no encontrado$(NC)" && exit 1)
	@echo "$(GREEN)$(EMOJI_CHECK) Todas las dependencias instaladas.$(NC)"

validate-versions: check-deps
	@echo "$(BLUE)$(EMOJI_INFO) Validando versiones...$(NC)"
	@python3 -c 'import sys; assert sys.version.startswith("$(PYTHON_VERSION)")' || \
		(echo "$(RED)$(EMOJI_ERROR) Python $(PYTHON_VERSION) requerido$(NC)" && exit 1)
	@echo "$(GREEN)$(EMOJI_CHECK) Versiones correctas.$(NC)"

# =============================================================================
# INSTALACIÓN Y CONSTRUCCIÓN
# =============================================================================
install: check-deps backend-build frontend-install frontend-build
	@echo "$(GREEN)$(EMOJI_CHECK) Instalación completada.$(NC)"

backend-build: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Construyendo backend...$(NC)"
	@cd $(BACKEND_PATH) && poetry install
	@echo "$(GREEN)$(EMOJI_CHECK) Backend construido.$(NC)"

frontend-install:
	@echo "$(BLUE)$(EMOJI_INFO) Instalando dependencias frontend...$(NC)"
	@cd $(FRONTEND_PATH) && npm ci
	@echo "$(GREEN)$(EMOJI_CHECK) Frontend instalado.$(NC)"

# =============================================================================
# BASE DE DATOS
# =============================================================================
db-setup: db-reset db-init db-seed
	@echo "$(GREEN)$(EMOJI_CHECK) Base de datos configurada.$(NC)"

db-init: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Inicializando base de datos...$(NC)"
	@python -m backend.db.init_db
	@echo "$(GREEN)$(EMOJI_CHECK) Base de datos inicializada.$(NC)"

db-reset: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Reseteando base de datos...$(NC)"
	@python -m backend.db.reset_db
	@echo "$(GREEN)$(EMOJI_CHECK) Base de datos reseteada.$(NC)"

# =============================================================================
# TESTS
# =============================================================================
test: check-environment tests-unit tests-integration
	@echo "$(GREEN)$(EMOJI_CHECK) Tests completados.$(NC)"

tests-unit: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando tests unitarios...$(NC)"
	@poetry run pytest tests/unit/ --junitxml=$(LOG_DIR)/unit-tests.xml

tests-integration: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando tests de integración...$(NC)"
	@poetry run pytest tests/integration/ --junitxml=$(LOG_DIR)/integration-tests.xml

test-with-containers: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando tests con contenedores...$(NC)"
	@poetry run pytest -v backend/tests/test_db.py -s --log-cli-level=INFO

# =============================================================================
# DOCKER
# =============================================================================
docker-all: docker-build docker-run

docker-build: check-docker check-env
	@echo "$(BLUE)$(EMOJI_INFO) Construyendo contenedores...$(NC)"
	@docker-compose --env-file $(ENV_FILE) -f $(DOCKER_COMPOSE_FILE) build
	@echo "$(GREEN)$(EMOJI_CHECK) Contenedores construidos.$(NC)"

# =============================================================================
# DESARROLLO Y PRODUCCIÓN
# =============================================================================
dev: check-environment check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Iniciando modo desarrollo...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) up --build $(APP_NAME)-backend $(APP_NAME)-frontend

prod: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Iniciando modo producción...$(NC)"
	@docker-compose -f $(DOCKER_COMPOSE_FILE) up $(APP_NAME)-backend $(APP_NAME)-frontend

# =============================================================================
# AYUDA
# =============================================================================
help:
	@echo "Comandos disponibles:"
	@echo "  Desarrollo:"
	@echo "    make dev                  - Iniciar en modo desarrollo"
	@echo "    make prod                 - Iniciar en modo producción"
	@echo "    make install              - Instalar todas las dependencias"
	@echo ""
	@echo "  Base de datos:"
	@echo "    make db-setup             - Configurar base de datos completa"
	@echo "    make db-init              - Inicializar base de datos"
	@echo "    make db-reset             - Resetear base de datos"
	@echo ""
	@echo "  Tests:"
	@echo "    make test                 - Ejecutar todos los tests"
	@echo "    make tests-unit           - Ejecutar tests unitarios"
	@echo "    make tests-integration    - Ejecutar tests de integración"
	@echo "    make test-with-containers - Ejecutar tests con contenedores"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-build         - Construir contenedores"
	@echo "    make docker-run           - Iniciar contenedores"
	@echo "    make docker-stop          - Detener contenedores"

.DEFAULT_GOAL := help
