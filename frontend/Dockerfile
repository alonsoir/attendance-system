# ============================================================================
# Etapa de compilación
# ============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Instalar dependencias del sistema
RUN apk add --no-cache curl bash ca-certificates jq

# Copiar archivos de configuración
COPY package*.json ./

# Crear directorio para scripts
RUN mkdir -p /app /app/scripts

COPY scripts/fetch-vault-secrets.sh /app/scripts/fetch-vault-secrets.sh
RUN chmod 500 /app/scripts/fetch-vault-secrets.sh

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . ./

# Ejecutar escaneos de seguridad
RUN npm audit || true
RUN npm run lint || true

# Construir la aplicación
RUN npm run build

# ============================================================================
# Etapa de producción
# ============================================================================
FROM nginx:alpine

# Crear usuario no root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Configuración de nginx
COPY --chown=appuser:appgroup nginx/conf/conf.d /etc/nginx/conf.d/
COPY --chown=appuser:appgroup nginx/conf/nginx.conf /etc/nginx/nginx.conf

# Copiar archivos construidos
COPY --from=builder --chown=appuser:appgroup /app/dist /usr/share/nginx/html

# Copiar script de entrada
COPY frontend-entrypoint.sh /app/entrypoint.sh
RUN chmod 500 /app/entrypoint.sh

# Configurar permisos
RUN chown -R appuser:appgroup /var/cache/nginx \
    && chown -R appuser:appgroup /var/log/nginx \
    && touch /var/run/nginx.pid \
    && chown -R appuser:appgroup /var/run/nginx.pid \
    && chmod -R 550 /usr/share/nginx/html \
    && chmod -R 550 /etc/nginx/conf.d

# Cambiar al usuario no root
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl --fail --silent http://localhost:80/health || exit 1

EXPOSE 80

ENTRYPOINT ["/app/entrypoint.sh"]
