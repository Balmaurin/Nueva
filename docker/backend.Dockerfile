# Usar imagen base de Python
FROM python:3.12-slim-bullseye

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    wget \
    software-properties-common \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Crear entorno virtual
RUN python3 -m venv /opt/venv

# Activar entorno virtual
ENV PATH="/opt/venv/bin:$PATH"

# Copiar archivos de requisitos
COPY requirements.txt /app/
COPY modules/rewards/requirements.txt /app/rewards_requirements.txt

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r rewards_requirements.txt

# Instalar modelos de SpaCy
RUN python -m spacy download es_core_news_lg

# Copiar código fuente
COPY . /app/

# Configurar variables de entorno para recompensas
ENV SHAILI_REWARDS_VAULT=/app/rewards/vault
ENV SHAILI_REWARDS_SESSIONS=/app/rewards/sessions

# Crear directorios para recompensas
RUN mkdir -p /app/rewards/vault /app/rewards/sessions

# Comando por defecto
CMD ["python", "-m", "core.inference.server"]
