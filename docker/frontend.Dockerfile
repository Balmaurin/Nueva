# Usar imagen base de Node.js
FROM node:20-alpine AS build

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY interface/web/frontend/package.json interface/web/frontend/package-lock.json* ./

# Instalar dependencias
RUN npm ci --silent

# Copiar código fuente
COPY interface/web/frontend/ .

# Construir aplicación para producción
RUN npm run build

# Imagen final con Nginx
FROM nginx:alpine

# Copiar archivos de construcción
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración de Nginx
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 3000

# Comando para ejecutar Nginx
CMD ["nginx", "-g", "daemon off;"]
