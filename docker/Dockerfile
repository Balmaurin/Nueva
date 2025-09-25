# Dockerfile principal para NeuroFusion AI
FROM python:3.12-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración
COPY requirements.txt .
COPY package.json .
COPY config/ ./config/
COPY modules/ ./modules/

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar dependencias de Node.js
RUN npm install

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p data logs cache

# Configurar permisos
RUN chmod +x start_sistema_unificado.sh
RUN chmod +x verificar_sistema.sh

# Exponer puertos
EXPOSE 8000 3000 9090 3100

# Comando por defecto
CMD ["./start_sistema_unificado.sh"]
