```text
# Attendance System - Backend Component

Este es el componente backend del sistema de gestión de asistencia. Para la documentación completa del proyecto, consulta el [README principal](../../README.md).

## Stack Tecnológico

- Python 3.10
- FastAPI (framework web asíncrono)
- Poetry 1.8.4 (gestión de dependencias)
- PostgreSQL (base de datos principal)
- Redis (caché y gestión de sesiones)
- Vault (gestión segura de secretos)

## Arquitectura

El backend sigue una arquitectura limpia con las siguientes capas:
- API (interfaces HTTP/WebSocket)
- Servicios (lógica de negocio)
- Modelos (entidades de dominio)
- Repositorios (acceso a datos)

### Estructura de Directorios


backend/
├── api/                    # Endpoints y routers
│   └── endpoints/         # Definiciones de rutas por dominio
├── core/                  # Configuración central y utilidades
│   ├── app.py            # Configuración de FastAPI
│   └── settings.py       # Configuración y variables de entorno
├── db/                    # Capa de datos
│   ├── models/           # Modelos SQLAlchemy
│   └── repositories/     # Patrón repositorio
├── services/             # Lógica de negocio
├── scripts/              # Scripts de utilidad y seguridad
│   ├── fetch-secrets.sh
│   ├── init-vault.sh
│   ├── rotate-secrets.sh
│   └── secure-env.sh
└── tests/                # Suite de pruebas
    ├── unit/
    └── integration/
Seguridad
Medidas Implementadas

Gestión segura de secretos con Vault
Rate limiting y protección contra DDoS
Autenticación JWT
Encriptación de datos sensibles
Logging seguro
Escaneo continuo de dependencias
Contenedores mínimos y seguros

Buenas Prácticas

Principio de mínimo privilegio
Validación estricta de entrada
Sanitización de datos
Rotación automática de secretos
Monitorización con Prometheus/Grafana

Desarrollo
Prerrequisitos

Python 3.10+
Poetry 1.8.4+
Docker & Docker Compose
Make (opcional, pero recomendado)

Configuración del Entorno

Clonar el repositorio e ir al directorio backend:

bashCopycd attendance_system/backend

Instalar dependencias:

bashCopypoetry install

Configurar variables de entorno:

bashCopycp .env-development.example .env-development

Iniciar servicios necesarios:

bashCopymake docker-all
Comandos Útiles
bashCopy# Iniciar servidor de desarrollo
make dev

# Ejecutar tests
make test

# Verificar seguridad
make security-check

# Formatear código
make format

# Lint
make lint
Testing
Tipos de Tests

Unitarios: tests/unit/
Integración: tests/integration/
E2E: Con contenedores Docker

Ejecutar Tests
bashCopy# Todos los tests
make test

# Solo unitarios
make tests-unit

# Solo integración
make tests-integration

# Tests con contenedores
make test-with-containers-without-stored-procedures-acl-encryption
API Documentation
La documentación de la API está disponible en:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

Integración Continua
El backend utiliza GitHub Actions para:

Tests automatizados
Análisis de seguridad
Linting y verificación de tipos
Construcción y push de imágenes Docker

Monitorización

Healthcheck: /health
Métricas: /metrics (requiere autenticación)
Logs estructurados en formato JSON
Integración con Prometheus/Grafana

Contribuir

Crear una rama desde develop
Realizar cambios siguiendo las guías de estilo
Asegurar que los tests pasan
Crear PR contra develop

Guías de Estilo

Black para formateo
isort para imports
pylint para linting
mypy para tipos

## License

Proprietary and confidential
Copyright (c) 2024 Alonso Isidoro Román. All rights reserved.