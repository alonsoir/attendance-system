# Etapa de compilación
FROM node:20-alpine as builder

# Carpeta de trabajo
WORKDIR /app

# Copiar y construir
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Etapa de producción
FROM nginx:alpine

# Copiar archivos generados
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Script de inicio
COPY frontend-entrypoint.sh /frontend-entrypoint.sh
RUN chmod +x /frontend-entrypoint.sh

ENTRYPOINT ["/frontend-entrypoint.sh"]
