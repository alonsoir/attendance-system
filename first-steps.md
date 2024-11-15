# Guía de Inicio Paso a Paso 🚀

## 1. Verificación Inicial del Sistema

```bash
# Verificar requisitos del sistema
make check-deps

Makefile:261: warning: overriding commands for target `heroku-deploy'
Makefile:242: warning: ignoring old commands for target `heroku-deploy'
ℹ️ Verificando dependencias del sistema... 
✅ Todas las dependencias están instaladas 

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
cp .env-dev.example .env-dev

# Editar .env-dev con tus credenciales
nano .env-dev
```

Variables críticas a configurar:
- ANTHROPIC_API_KEY
  - SECRET_KEY
      Para generar esta clave secreta, puedes utilizar la siguiente línea de código en Python:
      ```python
        ┌<▸> ~/g/a/attendance_system 
        └➤ python -c "import secrets; print(secrets.token_urlsafe(32))"
        N6rTMNk__0oKGy3HXe5spXgNXft8wuQVyTNv-lG1edA      
      ```
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
   - [ ] Servidor backend responde
   - [ ] Frontend carga correctamente
   - [ ] Base de datos conectada
   - [ ] Redis funcionando

2. **Integraciones**
   - [ ] Conexión con Claude API
   - [ ] WebSockets funcionando
   - [ ] Sistema de logs activo

3. **Características**
   - [ ] Autenticación funciona
   - [ ] CRUD de ausencias
   - [ ] Notificaciones funcionan
   - [ ] Métricas disponibles

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

¿Necesitas que detalle algún paso específico o que añada más información sobre algún aspecto en particular?