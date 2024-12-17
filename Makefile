# =============================================================================
# DECLARACIÓN DE PHONY TARGETS (actualizado)
# =============================================================================
.PHONY: help check-docker check-environment check-deps validate-versions check-env \
        generate-secret install backend-build frontend-install frontend-build \
        dev prod run format lint test tests-unit tests-integration \
        test-with-containers-without-stored-procedures-acl-encryption \
        test-with-containers-with-stored-procedures-acl-encryption test-in-docker \
        docker-build docker-run docker-stop docker-all \
        db-init db-reset db-seed db-setup \
        postgres-acl-build  postgres-acl-scale postgres-acl-replicate \
        postgres-acl-remove postgres-acl-all security-check security-bandit security-safety security-gitguardian

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

POSTGRES_PATH = postgresql
POSTGRES_VERSION = 15
POSTGRES_IMAGE_NAME = test-postgres-encrypted
POSTGRES_SERVICE_NAME = test-postgres-encrypted
POSTGRES_REPLICAS = 3
POSTGRES_SCALE = 5

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
	@if [ -n "$$CI" ]; then \
		echo "$(GREEN)$(EMOJI_CHECK) Ejecutando en CI - no se requiere entorno virtual.$(NC)"; \
	elif [ -z "$(VIRTUAL_ENV)" ]; then \
		poetry shell || (echo "$(RED)$(EMOJI_ERROR) No se pudo activar el entorno virtual!$(NC)" && exit 1); \
	else \
		echo "$(GREEN)$(EMOJI_CHECK) Entorno virtual activo.$(NC)"; \
	fi
	@echo "$(GREEN)$(EMOJI_CHECK) Entorno virtual verificado.$(NC)"
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

frontend-build:
	@echo "$(BLUE)$(EMOJI_INFO) Construyendo frontend...$(NC)"
	@cd $(FRONTEND_PATH) && npm run build
	@echo "$(GREEN)$(EMOJI_CHECK) Frontend construido.$(NC)"

# =============================================================================
# FORMATEO Y LINTING
# =============================================================================
format: format-backend format-frontend
	@echo "$(GREEN)$(EMOJI_CHECK) Formateo completado.$(NC)"

format-backend: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Formateando código backend...$(NC)"
	@cd $(BACKEND_PATH) && poetry run black .
	@cd $(BACKEND_PATH) && poetry run isort .
	@echo "$(GREEN)$(EMOJI_CHECK) Código backend formateado.$(NC)"

format-frontend:
	@echo "$(BLUE)$(EMOJI_INFO) Formateando código frontend...$(NC)"
	@cd $(FRONTEND_PATH) && npm run format
	@echo "$(GREEN)$(EMOJI_CHECK) Código frontend formateado.$(NC)"

lint: lint-backend lint-frontend
	@echo "$(GREEN)$(EMOJI_CHECK) Linting completado.$(NC)"

lint-backend: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando linting en backend...$(NC)"
	@cd $(BACKEND_PATH) && poetry run flake8 .
	@cd $(BACKEND_PATH) && poetry run mypy .
	@cd $(BACKEND_PATH) && poetry run pylint **/*.py
	@echo "$(GREEN)$(EMOJI_CHECK) Linting backend completado.$(NC)"

lint-frontend:
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando linting en frontend...$(NC)"
	@cd $(FRONTEND_PATH) && npm run lint
	@echo "$(GREEN)$(EMOJI_CHECK) Linting frontend completado.$(NC)"

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

db-seed: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Sembrando datos iniciales...$(NC)"
	@python -m backend.db.seed_db
	@echo "$(GREEN)$(EMOJI_CHECK) Datos iniciales sembrados.$(NC)"

# =============================================================================
# TESTS
# =============================================================================
test: check-environment tests-unit tests-integration test-with-containers-without-stored-procedures-acl-encryption test-with-containers-with-stored-procedures-acl-encryption
	@echo "$(GREEN)$(EMOJI_CHECK) Tests completados.$(NC)"

tests-unit: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando tests unitarios...$(NC)"
	poetry run pytest tests/unit/ --junitxml=../$(LOG_DIR)/unit-tests.xml

tests-integration: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando tests de integración...$(NC)"
	poetry run pytest tests/integration/ --junitxml=../$(LOG_DIR)/integration-tests.xml

test-with-containers-without-stored-procedures-acl-encryption: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando tests con contenedores...$(NC)"
	cd $(BACKEND_PATH) && PYTHONPATH=. pytest -v tests/test_db.py -s --log-cli-level=INFO

test-with-containers-with-stored-procedures-acl-encryption: check-environment 
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando tests con contenedores...$(NC)"
	cd $(BACKEND_PATH) && PYTHONPATH=. pytest -v tests/stored_procedures/test_stored_procedures.py -s --log-cli-level=INFO

# =============================================================================
# DOCKER
# =============================================================================
docker-all: docker-build docker-run

docker-build: check-docker check-env
	@echo "$(BLUE)$(EMOJI_INFO) Construyendo contenedores...$(NC)"
	@docker-compose --env-file $(ENV_FILE) -f $(DOCKER_COMPOSE_FILE) build \
		--build-arg BACKEND_PATH=$(BACKEND_PATH) \
		--build-arg FRONTEND_PATH=$(FRONTEND_PATH)
	@echo "$(GREEN)$(EMOJI_CHECK) Contenedores construidos.$(NC)"

docker-run: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Iniciando contenedores...$(NC)"
	@docker-compose --env-file $(ENV_FILE) -f $(DOCKER_COMPOSE_FILE) up -d
	@echo "$(GREEN)$(EMOJI_CHECK) Contenedores iniciados.$(NC)"

docker-stop: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Deteniendo contenedores...$(NC)"
	@docker-compose --env-file $(ENV_FILE) -f $(DOCKER_COMPOSE_FILE) down
	@echo "$(GREEN)$(EMOJI_CHECK) Contenedores detenidos.$(NC)"

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
# POSTGRESQL CON ACL Y ENCRIPTACIÓN
# =============================================================================
postgres-acl-all: postgres-acl-build 

postgres-acl-build: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Construyendo imagen PostgreSQL personalizada con ACL y encriptación...$(NC)"
	@cd $(POSTGRES_PATH) && ./build_pg_container_acl_encrypt_decrypt_test.sh
	@echo "$(GREEN)$(EMOJI_CHECK) Imagen PostgreSQL personalizada construida.$(NC)"

postgres-acl-scale: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Escalando servicio PostgreSQL...$(NC)"
	@cd $(POSTGRES_PATH) && ./scale_postgres_encrypted.sh $(POSTGRES_SCALE)
	@echo "$(GREEN)$(EMOJI_CHECK) Servicio PostgreSQL escalado a $(POSTGRES_SCALE) instancias.$(NC)"

postgres-acl-replicate: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Creando réplicas de PostgreSQL...$(NC)"
	@cd $(POSTGRES_PATH) && ./replica_postgres_encrypted.sh $(POSTGRES_REPLICAS)
	@echo "$(GREEN)$(EMOJI_CHECK) Creadas $(POSTGRES_REPLICAS) réplicas de PostgreSQL.$(NC)"

postgres-acl-remove: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Removiendo servicios PostgreSQL...$(NC)"
	@cd $(POSTGRES_PATH) && ./remove_postgres_encrypted.sh
	@echo "$(GREEN)$(EMOJI_CHECK) Servicios PostgreSQL removidos.$(NC)"

postgres-acl-status: check-docker
	@echo "$(BLUE)$(EMOJI_INFO) Estado de servicios PostgreSQL:$(NC)"
	@docker service ls | grep $(POSTGRES_SERVICE_NAME)
	@echo "$(BLUE)$(EMOJI_INFO) Nodos del swarm:$(NC)"
	@docker node ls
	@echo "$(BLUE)$(EMOJI_INFO) Contenedores en ejecución:$(NC)"
	@docker ps | grep $(POSTGRES_SERVICE_NAME)

# Actualizar las dependencias de los tests
test-with-containers-with-stored-procedures-acl-encryption: check-environment postgres-acl-build
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando tests con contenedores...$(NC)"
	PYTHONPATH=. pytest -v backend/tests/stored_procedures/test_stored_procedures.py -s --log-cli-level=INFO

# =============================================================================
# SECURITY CHECKS
# =============================================================================

security-check: check-environment security-bandit security-safety security-gitguardian
	@echo "$(GREEN)$(EMOJI_CHECK) Verificaciones de seguridad completadas.$(NC)"

security-bandit: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando análisis de seguridad con Bandit...$(NC)"
	@cd $(BACKEND_PATH) && bandit -r . -f json -o ../$(LOG_DIR)/bandit-results.json
	@echo "$(GREEN)$(EMOJI_CHECK) Análisis Bandit completado.$(NC)"

security-safety: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Verificando dependencias con Safety...$(NC)"
	@cd $(BACKEND_PATH) && safety check
	@echo "$(GREEN)$(EMOJI_CHECK) Verificación Safety completada.$(NC)"

security-gitguardian: check-environment
	@echo "$(BLUE)$(EMOJI_INFO) Ejecutando escaneo con GitGuardian...$(NC)"
	@if [ -z "$$GITGUARDIAN_API_KEY" ]; then \
		echo "$(RED)$(EMOJI_ERROR) GITGUARDIAN_API_KEY no está configurada$(NC)" && exit 1; \
	fi
	@cd $(BACKEND_PATH) && ggshield secret scan path .
	@echo "$(GREEN)$(EMOJI_CHECK) Escaneo GitGuardian completado.$(NC)"


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
	@echo "  Calidad de código:"
	@echo "    make format               - Formatear todo el código"
	@echo "    make format-backend       - Formatear código backend"
	@echo "    make format-frontend      - Formatear código frontend"
	@echo "    make lint                 - Ejecutar linting en todo el código"
	@echo "    make lint-backend         - Ejecutar linting en backend"
	@echo "    make lint-frontend        - Ejecutar linting en frontend"
	@echo ""
	@echo "  Base de datos:"
	@echo "    make db-setup             - Configurar base de datos completa"
	@echo "    make db-init              - Inicializar base de datos"
	@echo "    make db-reset             - Resetear base de datos"
	@echo "    make db-seed              - Sembrar datos iniciales"
	@echo ""
	@echo "  Tests:"
	@echo "    make test                 - Ejecutar todos los tests"
	@echo "    make tests-unit           - Ejecutar tests unitarios"
	@echo "    make tests-integration    - Ejecutar tests de integración"
	@echo "    make test-with-containers-without-stored-procedures-acl-encryption    - Ejecutar tests con contenedores sin SP"
	@echo "    make test-with-containers-with-stored-procedures-acl-encryption      - Ejecutar tests con contenedores con SP"
	@echo ""
	@echo "  Docker:"
	@echo "    make docker-build         - Construir contenedores"
	@echo "    make docker-run           - Iniciar contenedores"
	@echo "    make docker-stop          - Detener contenedores"
	@echo "    make docker-all           - Construir e iniciar contenedores"
	@echo "    make docker-clean         - Detener y eliminar contenedores"@echo ""
	@echo "  PostgreSQL con ACL y Encriptación:"
	@echo "    make postgres-acl-all          - Construir e iniciar PostgreSQL con ACL"
	@echo "    make postgres-acl-build        - Construir imagen PostgreSQL personalizada"
	@echo "    make       - Iniciar servicio PostgreSQL en Swarm"
	@echo "    make postgres-acl-scale        - Escalar servicio PostgreSQL"
	@echo "    make postgres-acl-replicate    - Crear réplicas de PostgreSQL"
	@echo "    make postgres-acl-remove       - Remover servicios PostgreSQL"
	@echo "    make postgres-acl-status       - Ver estado de servicios PostgreSQL"

.DEFAULT_GOAL := help