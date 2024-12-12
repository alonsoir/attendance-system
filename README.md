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
- 🔄 CI/CD con GitHub Actions

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
- Docker 24.x, Docker Compose v2, Docker Swarm
- PostgreSQL 15
- Redis 7
- Nginx
- Prometheus
- Grafana

## 📋 Requisitos del Sistema

- Python 3.10.x
- Poetry 1.8.4
- Node.js 20.x
- Docker 24.x, Docker Compose v2, Docker Swarm
- Make
- Git

## 🔐 Configuración Segura

### Variables de Entorno

1. Copia los archivos de ejemplo:
```bash
# Desarrollo
cp .env-development.example .env-development

# Producción
cp .env-production.example .env-production
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

## 🚀 Opciones de Despliegue

### 1. Heroku (Recomendado para inicio rápido)

#### Prerequisitos

1. **Cuenta Heroku**
   - Crear cuenta gratuita en [Heroku](https://signup.heroku.com)
   - Instalar [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

2. **Add-ons Necesarios (Free Tier)**
   - Heroku Postgres
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
   - Heroku Redis
   ```bash
   heroku addons:create heroku-redis:hobby-dev
   ```

3. **Variables de Entorno en GitHub**
   Configurar en `Settings > Secrets and variables > Actions`:
   ```plaintext
   # Heroku
   HEROKU_API_KEY            # Tu API key de Heroku
   HEROKU_EMAIL             # Email de tu cuenta Heroku
   HEROKU_APP_NAME          # Nombre de tu aplicación en Heroku

   # Producción
   PROD_SECRET_KEY          # Clave secreta para producción
   PROD_ANTHROPIC_API_KEY   # API key de Claude/Anthropic
   PROD_META_API_KEY        # API key de WhatsApp/Meta
   ```

#### Despliegue en Heroku
```bash
# Manual
make heroku-deploy ENV=prod

# Automático (via GitHub Actions)
git push main
```

### 2. Alternativas de Hosting

#### Railway.app
- Similar a Heroku
- Tier gratuito disponible
- Soporte nativo para Docker
- PostgreSQL y Redis incluidos

#### Render
- Alternativa moderna
- Tier gratuito
- Despliegue automático desde GitHub
- Servicios gestionados

#### DigitalOcean App Platform
- PaaS completo
- Buena relación calidad/precio
- Servicios gestionados
- Escalabilidad sencilla

#### Google Cloud Run
- Serverless
- Pay-per-use
- Excelente para contenedores
- Integración con servicios GCP

### 3. Almacenamiento Adicional

Wasabi u otros servicios S3-compatibles pueden utilizarse para:
- Backups de base de datos
- Almacenamiento de logs
- Archivos estáticos/media
- Copias de configuración

[... continúa con las secciones anteriores de Troubleshooting, Estructura del Proyecto, etc. ...]

## 🤝 Contribuir

[... secciones anteriores de Contribuir, Licencia, etc. ...]

## 📝 Changelog

Ver [CHANGELOG.md](CHANGELOG.md) para detalles sobre cambios y versiones.

## 🔌 Integración con Servicios Externos

### Claude/Anthropic API
1. Crear cuenta en [Anthropic](https://www.anthropic.com/)
2. Obtener API key desde el dashboard
3. Configurar en variables de entorno:
   ```bash
   ANTHROPIC_API_KEY=your-api-key
   ```

### WhatsApp Business API
1. Crear cuenta en [Meta for Developers](https://developers.facebook.com/)
2. Configurar WhatsApp Business API
3. Obtener tokens necesarios
4. Configurar webhook

## 💼 Guía de Producción

### Checklist Pre-Despliegue
- [ ] Todas las variables de entorno configuradas
- [ ] Secrets revisados y actualizados
- [ ] Tests pasando al 100%
- [ ] Migraciones probadas
- [ ] Backups configurados
- [ ] Monitorización activada
- [ ] SSL/TLS configurado
- [ ] Firewall y seguridad revisados

### Backups
```bash
# Backup manual
make backup ENV=prod

# Restaurar backup
make restore ENV=prod BACKUP_FILE=backup_name.sql

# Programar backup automático
make schedule-backup ENV=prod
```

### Escalabilidad
- Configuración de auto-scaling
- Manejo de carga
- Optimización de recursos
- Políticas de caché

## 🔬 Ambiente de Testing

### Tipos de Tests
1. **Unitarios**: Componentes individuales
2. **Integración**: Interacción entre componentes
3. **E2E**: Flujos completos
4. **Performance**: Rendimiento bajo carga

### Datos de Prueba
```bash
# Generar datos de prueba
make generate-test-data

# Limpiar datos de prueba
make clean-test-data
```

## 📊 Métricas y KPIs

### Métricas de Negocio
- Tasa de respuesta de tutores
- Tiempo promedio de respuesta
- Efectividad de seguimiento
- Patrones de ausencia

### Métricas Técnicas
- Tiempo de respuesta API
- Uso de recursos
- Tasa de errores
- Disponibilidad del servicio

## 🔐 Seguridad

### Auditoría
```bash
# Ejecutar auditoría de seguridad
make security-audit

# Verificar dependencias
make check-dependencies

# Escanear vulnerabilidades
make scan-vulnerabilities
```

### Compliance
- GDPR/RGPD
- FERPA (para datos educativos)
- LOPD (España)
- Protección de datos de menores

### Mejores Prácticas
- Rotación regular de secretos
- Monitorización de accesos
- Logs de auditoría
- Planes de respuesta a incidentes

## 🌍 Internacionalización

### Idiomas Soportados
- 🇪🇸 Español (España)
- 🇺🇸 Inglés (US)

### Añadir Nuevo Idioma
1. Crear archivo de traducción
2. Actualizar configuración i18n
3. Validar traducciones
4. Actualizar documentación

## 📱 PWA Support

### Características
- Instalable en dispositivos móviles
- Funcionamiento offline
- Push notifications
- Sincronización en segundo plano

### Service Worker
```bash
# Construir service worker
make build-sw

# Probar funcionalidad offline
make test-offline
```

## 🤖 CI/CD

### GitHub Actions
- Build automático
- Tests en cada PR
- Análisis de código
- Despliegue automático

### Entornos
- Development
- Staging
- Production

### Rollback
```bash
# Revertir último despliegue
make rollback ENV=prod

# Listar despliegues anteriores
make list-deployments
```

## 📚 Documentación Adicional

### Guías
- [Manual de Usuario](docs/user-guide.md)
- [Guía de Desarrollo](docs/dev-guide.md)
- [Guía de Despliegue](docs/deployment-guide.md)
- [Guía de Troubleshooting](docs/troubleshooting-guide.md)

### API Docs
- [OpenAPI Spec](docs/api/openapi.yaml)
- [Postman Collection](docs/api/postman_collection.json)
- [Ejemplos de Integración](docs/api/examples)

### Arquitectura
- [Diagramas](docs/architecture/diagrams)
- [Decisiones de Diseño](docs/architecture/decisions)
- [Patrones Utilizados](docs/architecture/patterns)
- 
## 🔜 Roadmap

- [ ] Integración con sistemas escolares externos
- [ ] App móvil para tutores
- [ ] Sistema de reportes automáticos
- [ ] Análisis predictivo de ausencias
- [ ] Soporte para múltiples centros educativos
- [ ] API pública para integraciones de terceros

## 🆘 Soporte

- 📧 Email: alonsoir@gmail.com
- 💬 Discord: [Invitación al servidor](https://discord.gg/your-server)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/attendance-system/issues)
- 📝 Wiki: [GitHub Wiki](https://github.com/yourusername/attendance-system/wiki)

## 🙏 Agradecimientos

- [FastAPI](https://fastapi.tiangolo.com/)
- [Anthropic Claude](https://www.anthropic.com/)
- [WhatsApp Business API](https://www.whatsapp.com/business/api)
- [shadcn/ui](https://ui.shadcn.com/)

# Guía de Inicio Paso a Paso 🚀

## 1. Verificación Inicial del Sistema

```bash
# Verificar requisitos del sistema
make check-deps
```

Esto verificará que tengas instalado:
- Python 3.10.x
- Poetry 1.8.4
- Node.js 20.x
- Docker y Docker Compose
- Make

## 2. Configuración del Entorno de Desarrollo

```bash
# Copiar archivos de ejemplo
cp .env-development.example .env-development

# Editar .env-development con tus credenciales
nano .env-development
```

Variables críticas a configurar:
- ANTHROPIC_API_KEY
- SECRET_KEY
- Credenciales de base de datos local

## 3. Instalación de Dependencias

```bash
# Instalar dependencias de Python y Node.js
make install ENV=dev

# Verificar instalación
poetry env info
poetry show
```

## 4. Verificación de Código y Tests

```bash
# Ejecutar verificaciones de código
make lint
make type-check

# Ejecutar tests unitarios
make test-unit

# Verificar cobertura
make test-coverage
```

## 5. Iniciar Servicios Básicos (sin Docker)

```bash
# Iniciar PostgreSQL y Redis localmente si los tienes instalados
# O usar Docker solo para servicios de base de datos
docker-compose up -d db redis

# Ejecutar migraciones
make migrate ENV=dev

# Iniciar backend en modo desarrollo
poetry run uvicorn backend.main:app --reload --port 8000
```

## 6. Probar el Backend

```bash
# Verificar estado del servidor
curl http://localhost:8000/health

# Verificar documentación API
# Abrir en navegador: http://localhost:8000/docs
```

## 7. Iniciar Frontend en Desarrollo

```bash
# En otra terminal
cd frontend
npm run dev

# Abrir en navegador: http://localhost:3000
```

## 8. Construcción de Contenedores (opcional en desarrollo)

```bash
# Solo después de verificar que todo funciona localmente
make docker-build ENV=dev
make docker-run ENV=dev

# Verificar logs
make logs
```

## 9. Verificación Final del Sistema

```bash
# Verificar todos los servicios
curl http://localhost:8000/api/v1/status

# Verificar métricas
curl http://localhost:8000/metrics
```

## Troubleshooting Común

### Problemas de Dependencias
```bash
# Limpiar entorno
make clean

# Reinstalar todo
make install ENV=dev
```

### Problemas de Base de Datos
```bash
# Resetear base de datos
make db-reset ENV=dev
```

### Problemas de Docker
```bash
# Limpiar contenedores
docker-compose down -v
docker system prune -f

# Reconstruir
make docker-build ENV=dev
```

## Verificación de Funcionalidades

1. **Sistema Base**
   - [X] Servidor backend responde
   - [ ] Frontend carga correctamente
   - [X] Base de datos conectada
   - [ ] Redis funcionando

2. **Integraciones**
   - [X] Conexión con Claude API
   - [ ] WebSockets funcionando
   - [X] Sistema de logs activo
   - [ ] Integración con WhatsApp
   - [X] Integración con API de CallmeBot
   - [ ] Integración con docker swarm de todos los servicios backend. In progress.
   
3. **Características**
   - [ ] Autenticación funciona
   - [X] CRUD de ausencias
   - [ ] Notificaciones funcionan
   - [ ] Métricas disponibles
   - [ ] Sistema de reportes
   - [ ] Análisis de datos
   - [ ] Sistema de alertas
   - [ ] Comprobación de todo lo propuesto en el README.md
   - [ ] Creación del video demostración
   
## Notas Importantes

1. **Desarrollo Local**
   - Usar `make run ENV=dev` para desarrollo rápido
   - Los cambios en código se recargan automáticamente
   - Logs disponibles en tiempo real

2. **Docker**
   - Usar contenedores solo cuando sea necesario en desarrollo
   - Útil para probar el sistema completo
   - Consumirá más recursos que el desarrollo local

3. **Performance**
   - Desarrollo local es más rápido para iteraciones
   - Docker es mejor para probar el sistema completo
   - Usar profiling en desarrollo: `make profile ENV=dev`

4. **Testing**
   - Ejecutar todos los tests en local: `make test`
   - Ejecutar tests unitarios: `make test-unit`
   - Ejecutar tests de integración: `make test-integration`
   - Verificar cobertura: `make test-coverage`
   - Ejecutar tests en Docker: `make docker-test`
   - Ejecutar tests en producción: `make deploy ENV=prod`
   - Ejecutar tests en producción con Docker: `make docker-deploy ENV=prod`
   - Ejecutar tests en producción con Docker y Docker Compose: `make docker-compose-test ENV=prod`
   - Ejecutar tests en producción con Docker Compose: `make docker-compose-test ENV=prod`
   - Ejecutar tests en producción con Docker Compose y Docker Swarm: `make docker-compose-test ENV=prod`
   