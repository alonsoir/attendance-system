# Attendance System 🏫

Un sistema de gestión de asistencia escolar moderno que utiliza IA (Claude) y WhatsApp para la comunicación automática con tutores sobre ausencias estudiantiles.

## ✨ Características

- 🤖 Integración con Claude para procesamiento inteligente de mensajes
- 📱 Comunicación bidireccional a través de WhatsApp
- 🌐 API RESTful con FastAPI
- 📊 Dashboard en tiempo real con React
- 🔄 Actualizaciones en tiempo real vía WebSocket
- 🔒 Sistema de autenticación y autorización
- 🌍 Soporte multiidioma (ES, EN)
- 📈 Monitorización con Prometheus y Grafana
- 💾 Persistencia con PostgreSQL
- 🚀 Caché con Redis
- 🐳 Containerización completa con Docker
- 🔄 CI/CD con Heroku

## 🛠️ Stack Tecnológico

### Backend
- Python 3.10
- FastAPI
- SQLAlchemy + Alembic
- Poetry 1.8.4
- Claude API (Anthropic)
- WhatsApp Business API

### Frontend
- React 18
- TypeScript 5
- Tailwind CSS 3
- shadcn/ui
- Vite

### Infraestructura
- Docker 24.x y Docker Compose v2
- PostgreSQL 14
- Redis 7
- Nginx
- Prometheus
- Grafana

## 📋 Requisitos del Sistema

- Python 3.10.x
- Poetry 1.8.4
- Node.js 20.x
- Docker 24.x y Docker Compose v2
- Make
- Git

## 🔐 Configuración Segura

### Variables de Entorno

1. Copia los archivos de ejemplo:
```bash
# Desarrollo
cp .env-dev.example .env-dev

# Producción
cp .env-prod.example .env-prod
```

2. Configura las variables sensibles:
- Genera una SECRET_KEY segura
- Configura las credenciales de base de datos
- Añade las API keys necesarias
- Configura las credenciales de email

3. Verifica la configuración:
```bash
make check-env ENV=dev  # o ENV=prod
```

### Buenas Prácticas de Seguridad

1. Nunca commitees archivos .env
2. Usa secrets seguros en producción
3. Rota las credenciales regularmente
4. Utiliza diferentes valores para desarrollo y producción
5. Mantén las API keys privadas

### Verificación de Secrets

El proyecto usa ggshield para prevenir la exposición de secrets:

```bash
# Instalar ggshield
pip install ggshield

# Verificar archivos por secrets
make check-secrets
```

## 🚀 Inicio Rápido

### 1. Clonar el Repositorio
```bash
git clone https://github.com/yourusername/attendance-system.git
cd attendance-system
```

### 2. Verificar Dependencias
```bash
make check-deps
```

### 3. Inicializar el Proyecto
```bash
# Desarrollo
make init ENV=dev

# Producción
make init ENV=prod
```

### 4. Iniciar el Sistema
```bash
# Desarrollo
make run ENV=dev

# Producción
make deploy ENV=prod
```

## 🛠️ Comandos Make Disponibles

### Instalación y Configuración
```bash
make init ENV=[dev|prod]        # Inicializar proyecto completo
make install ENV=[dev|prod]     # Instalar dependencias
make check-deps                 # Verificar dependencias del sistema
make check-secrets             # Verificar secrets en el código
```

### Desarrollo
```bash
make run ENV=[dev|prod]         # Ejecutar en desarrollo
make format                     # Formatear código
make lint                       # Ejecutar linters
make type-check                # Verificar tipos
```

### Testing
```bash
make test ENV=[dev|prod]        # Ejecutar todos los tests
make test-unit                 # Ejecutar tests unitarios
make test-integration         # Ejecutar tests de integración
make test-coverage            # Generar reporte de cobertura
```

### Docker
```bash
make docker-build ENV=[dev|prod] # Construir contenedores
make docker-run ENV=[dev|prod]   # Ejecutar contenedores
make docker-stop                # Detener contenedores
make logs                       # Ver logs de contenedores
```

### Base de Datos
```bash
make migrate ENV=[dev|prod]     # Ejecutar migraciones
make db-reset ENV=[dev|prod]    # Resetear base de datos
```

## 📊 Monitorización y Métricas

### Acceso a Servicios

| Servicio    | Desarrollo                | Producción               | Notas                    |
|-------------|---------------------------|-------------------------|--------------------------|
| Frontend    | http://localhost:3000     | https://your-domain    | Interfaz principal      |
| API Docs    | http://localhost:8000/docs| https://api.domain/docs| Documentación OpenAPI   |
| Grafana     | http://localhost:3001     | https://metrics.domain | Métricas y dashboards   |
| Prometheus  | http://localhost:9090     | Internal only          | Recolección de métricas |

### Endpoints de Estado
- `/health` - Estado general del sistema
- `/metrics` - Métricas de Prometheus
- `/api/v1/status` - Estado detallado de servicios

## 🔍 Troubleshooting

### Verificación de Estado
```bash
# Estado general
curl http://localhost:8000/health

# Estado de servicios
curl http://localhost:8000/api/v1/status
```

### Logs y Diagnóstico
```bash
# Todos los servicios
make logs

# Servicio específico
docker-compose logs api
```

### Problemas Comunes

1. Error de conexión a BD:
```bash
make db-reset ENV=dev
```

2. Dependencias:
```bash
make clean
make install ENV=dev
```

3. Tipos:
```bash
make type-check
```

## 📦 Estructura del Proyecto

```
attendance_system/
├── attendance_system/        # Backend
│   ├── api/                 # Endpoints
│   ├── core/               # Configuración
│   ├── db/                 # Modelos
│   └── services/           # Servicios
├── frontend/               # Frontend React
│   ├── src/               # Código fuente
│   └── public/            # Archivos estáticos
├── migrations/             # Migraciones DB
├── tests/                 # Tests
│   ├── unit/             # Tests unitarios
│   └── integration/      # Tests de integración
├── docs/                 # Documentación
├── Dockerfile           # Backend container
├── docker-compose.yml   # Servicios
└── Makefile            # Automatización
```

## 🤝 Contribuir

1. Fork del repositorio

2. Configurar entorno:
```bash
make init ENV=dev
```

3. Crear rama:
```bash
git checkout -b feature/amazing-feature
```

4. Verificar código:
```bash
make format
make lint
make type-check
make test
```

5. Crear Pull Request

### Guía de Pull Request

1. Asegúrate de que todos los tests pasan
2. Actualiza la documentación si es necesario
3. Sigue las convenciones de código existentes
4. Añade tests para nuevas funcionalidades
5. Actualiza el CHANGELOG.md

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

- 📧 Email: your.email@example.com
- 💬 Discord: [Invitación al servidor](https://discord.gg/your-server)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/attendance-system/issues)
- 📝 Wiki: [GitHub Wiki](https://github.com/yourusername/attendance-system/wiki)

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno y rápido
- [Anthropic Claude](https://www.anthropic.com/) - API de IA avanzada
- [WhatsApp Business API](https://www.whatsapp.com/business/api) - Comunicación con tutores
- [shadcn/ui](https://ui.shadcn.com/) - Componentes de UI accesibles

## 📝 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para detalles sobre cambios y versiones.

## 🔜 Roadmap

- [ ] Integración con sistemas escolares externos
- [ ] App móvil para tutores
- [ ] Sistema de reportes automáticos
- [ ] Análisis predictivo de ausencias
- [ ] Soporte para múltiples centros educativos
- [ ] API pública para integraciones de terceros