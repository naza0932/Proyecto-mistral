# Proyecto de Investigación e Inferencia Local con Minstral 3B
Dicho repositorio contiene la implementación, pruebas y contenerización con Docker Desktop de una suite de inferencia. Para el modelo de lenguaje de Ministral 3B, el cual se ejecuta localmente a través de Ollama

# Especificaciones del Hardware y su justificación
*Sistema operativo: Windows 11 pro
*Procesador/memoria: Entorno con recursos de RAM/CPU estándar, además, sin GPU dedicada de gran VRAM
*Modelo seleccionado: El modelo seleccionado es ministral-3:3b, cuantización Q4_K_M
*Justificación: Se selecciono Ministral 3B, ya que ofrece un rendimiento óptimo de latencia, uso de la memoria RAM en los equipos personales sin la necesidad de requerir GPU dedicada. Además, mantiene alta precisión en tareas de lenguaje y razonamiento

# Requisitos previos 
*Sistema operativo: Windows 11 pro (Otros pueden ser Linux o macOS)
*Lenguaje: Python 3.11+
*Motor de inferencia: Ollama
Contenerización: Docker Desktop e integración con WSL2

# Instalación y preparación del modelo
Paso 1: Se debe asegurar de tener Ollama instalado, además, este debe estar ejecutandose en segundo plano
Paso 2: Descargar e iniciar el modelo ejecutandose en la terminal:
ollama run ministral-3:3b ( o bien mistral:latest, esto depende del nombre registrado en el entorno local de ollama)

# Ejecución del proyecto
Primera opción: Se puede hacer una ejecución local
1. Se entra a la terminal en Visual Studio Code, y se accede a la carpeta de código fuente y se ejecuta el script:
cd src
py inference.py

Segunda opción: Ejecución aislada con Docker Dekstop
1. Desde la terminal en Visual Studio Code, se construye la imagen local:
docker build -t mistral-eval:latest .

2. Se verifica la imagen creada y su tamaño:
docker images

3. Se ejecuta la suite dentro del contenedor:
docker run --rm --add-host=host.docker.internal:host-gateway -e OLLAMA_URL="http://host.docker.internal:11434/api/generate" -v "${PWD}/results:/app/results" mistral-eval:latest

# Ejemplo de salida genereda
El archivo se va a guardar en la carpeta results, bajo el nombre evaluation_results.json, se almacena la repuesta estructurada del modelo y sus métricas. Un ejemplo de como se veria: 
{
  "id": 10,
  "category": "Razonamiento y    veracidad",
  "prompt": "Pregunta factual: ¿Quién fue el que creó el lenguaje de programación Python y cuál fue su año de lanzamiento por primera vez?",
  "temperature": 0.7,
  "response": "El lenguaje de programación Python fue creado por Guido van Rossum, y fue lanzado por primera vez en 1991.",
  "time_seconds": 20.29,
  "ttft_seconds": 4.4414,
  "tokens_generated": 34,
  "tokens_per_second": 2.57
}



