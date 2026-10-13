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