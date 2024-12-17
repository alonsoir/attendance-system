# ============================================================================
# Etapa de compilación
# ============================================================================
FROM node:20-alpine AS builder

# Instalar dependencias del sistema y Vault
RUN apk add --no-cache \
    curl \
    jq \
    bash \
    ca-certificates \
    gnupg \
    # Instalar Vault
    && wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && wget -O /etc/apk/keys/vault.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub \
    && wget https://github.com/sgerrand/alpine-pkg-vault/releases/download/1.13.3/vault-1.13.3-r0.apk \
    && apk add --no-cache vault-1.13.3-r0.apk \
    && rm vault-1.13.3-r0.apk

WORKDIR /app

# Copiar archivos de configuración y scripts
COPY package*.json ./package*.json
COPY ./attendance_system/frontend/scripts/fetch-vault-secrets.sh /app/scripts/
RUN chmod 500 /app/scripts/fetch-vault-secrets.sh

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY ./attendance_system/frontend ./

# Ejecutar escaneos de seguridad
RUN npm audit \
    && npm run lint \
    # Aquí puedes añadir más verificaciones de seguridad si las necesitas

# Construir la aplicación
RUN npm run build

# ============================================================================
# Etapa de producción
# ============================================================================
FROM nginx:alpine

# Instalar dependencias necesarias
RUN apk add --no-cache \
    curl \
    jq \
    bash \
    ca-certificates \
    # Instalar Vault igual que en la etapa de builder
    && wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && wget -O /etc/apk/keys/vault.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub \
    && wget https://github.com/sgerrand/alpine-pkg-vault/releases/download/1.13.3/vault-1.13.3-r0.apk \
    && apk add --no-cache vault-1.13.3-r0.apk \
    && rm vault-1.13.3-r0.apk

# Crear usuario no root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copiar configuración de nginx
COPY --chown=appuser:appgroup ./attendance_system/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos construidos
COPY --from=builder --chown=appuser:appgroup /app/dist /usr/share/nginx/html

# Copiar scripts. El fetch-vault-secrets.sh se ejecutará en el entrypoint.sh
# COPY --chown=appuser:appgroup fetch-vault-secrets.sh /app/scripts/
COPY --chown=appuser:appgroup frontend-entrypoint.sh /app/entrypoint.sh
RUN chmod 500 /app/scripts/fetch-vault-secrets.sh /app/entrypoint.sh

# Configurar permisos
RUN chown -R appuser:appgroup /var/cache/nginx \
    && chown -R appuser:appgroup /var/log/nginx \
    && chown -R appuser:appgroup /etc/nginx/conf.d \
    && touch /var/run/nginx.pid \
    && chown -R appuser:appgroup /var/run/nginx.pid \
    && chmod -R 550 /usr/share/nginx/html \
    && chmod -R 550 /etc/nginx/conf.d

# Cambiar al usuario no root
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl --fail --silent http://localhost:80/health || exit 1

# Eliminar la configuración por defecto de nginx
RUN rm -rf /etc/nginx/conf.d/*

# Copiar archivos construidos
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

ENTRYPOINT ["/app/entrypoint.sh"]