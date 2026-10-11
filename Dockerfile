# Imagen ligera oficial de Python con versión fija
FROM python:3.11-slim

# Crear el directorio de trabajo dentro del contenedor
WORKDIR /app

# Crear un usuario que no sea root (no root) por seguridad
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Instalar dependencias si las hubiera y copiar requerimientos
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copiar código fuente y la suite de prompts
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser prompts/ ./prompts/

# Crear una carpeta de resultados dentro del contenedor
RUN mkdir -p /app/results

# Comando por defecto al ejecutar el contenedor
CMD ["python", "src/inference.py"]