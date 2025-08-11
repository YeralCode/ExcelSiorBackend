# Dockerfile para ExcelSior API
# Multi-stage build para optimizar el tamaño de la imagen

# Etapa de construcción
FROM python:3.12-slim as builder

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt pyproject.toml ./

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa de producción
FROM python:3.12-slim as production

# Instalar dependencias del sistema necesarias para runtime
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN groupadd -r excelsior && useradd -r -g excelsior excelsior

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias de Python desde la etapa de construcción
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /tmp/excelsior && \
    chown -R excelsior:excelsior /app /tmp/excelsior

# Cambiar al usuario no-root
USER excelsior

# Exponer puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV TEMP_DIR=/tmp/excelsior

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando por defecto
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Etapa de desarrollo (opcional)
FROM production as development

# Instalar dependencias de desarrollo
USER root
RUN pip install --no-cache-dir pytest pytest-cov black flake8 mypy

# Volver al usuario no-root
USER excelsior

# Comando para desarrollo
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"] 