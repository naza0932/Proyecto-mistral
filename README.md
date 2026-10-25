# Proyecto de Investigación e Inferencia Local con Minstral 3B
Dicho repositorio contiene las implementaciones así como evaluaciones de la suite de inferencia local, para el modelo con el que se esta trabajando llamado Ministral 3B, se ejecutan pruebas mediante Ollama y se incluye alternativas de ejecución asialada, estas realizadas mediante Docker Desktop.

# Especificaciones del Hardware y su justificación
*Sistema operativo: Windows 11 pro
*Procesador: Intel Core i5.10210U
*Memoria RAM: 8 GB DDR4
*Gráficos: Intel UHD Graphics integrada
*Modelo seleccionado: El modelo seleccionado es Ministral 3B
*Cuantización: Q4_K_M
*Motor de inferencia: Ollama
*Justificación: Se seleccionó Ministral 3B con cuantización Q4_K_M, esto por las limitaciones de hardware que presenta el equipo en el que se esta trabajando. Puesto que cuenta solo con 8 GB de RAM y no cuenta con una GPU dedicada con memoria de video propia.
La cuantización reduce lo que son los requisitos de memoria del modelo, facilita su ejecución en el equipo, por lo tanto, fueron las razones que se consideraron para seleccionar dicho modelo y poder estudiar la inferencia local en un entorno con recursos limitados.

# Requisitos previos 
*Sistema operativo: Windows 11 pro, se puede adapatar a otros sistemas que sean compatibles
*Lenguaje: Python 3.11+
*Motor de inferencia: Ollama, instalado y ejecutándose en el equipo
Docker Desktop: Es necesario para las ejecuciones de la suite dentro de un contenedor
WSL 2: Se necesita para la configuración habitual de Docker Desktop en Windows, su moto debe estar basado en WSL 2
Visual Studio Code: Este es el editor recomendado para poder trabajar el repositorio

# Instalación y preparación del modelo
Paso 1: Se debe descargar ollama e instalar, se busca desde su sitio oficial https://ollama.com/
Paso 2: Descargar e iniciar el modelo, desde la terminal de powershell, visual studio code o cmd se ejecuta el siguiente comando:
ollama run ministral-3:3b

Dicho comando descarga el modelo

Como paso de comprobación de que esta instalado se ejecuta en la terminal el siguiente comando:
ollama list

# Ejecución del proyecto
Primera opción: Se puede hacer una ejecución local
1. Primero se abre ollama, para que quede en segundo plano, despues desde el repositorio en Visual Studio Code, se abre una terminal, y se accede a la carpeta de código fuente:
cd src

Luego de esto, se ejecuta el script de inferencia:
py inference.py

Segunda opción: Ejecución mediante Docker Dekstop
1. Primero se abre Docker Dekstop, este debe estar ejecutandose en segundo plano, luego se abre ollama, para que también se este ejecutando en suendo plano, luego en Visual Studio Code, asegurandose de estar en la carpeta raíz del reposotrio, se abre una terminal y se ejecuta los siguientes comandos:
docker build -t ministral-3b-eval:latest .
Este comando sirve para construir la imagen

2. Se verifica la imagen creada y su tamaño:
docker images

3. Se ejecuta la suite dentro del contenedor:
docker run --rm --add-host=host.docker.internal:host-gateway -e OLLAMA_URL="http://host.docker.internal:11434/api/generate" -v "${PWD}/results:/app/results" ministral-3b-eval:latest --model ministral-3:3b

# Ejemplo de salida genereda
El archivo se va a guardar en la carpeta results, bajo el nombre evaluation_results.json, se almacena la repuesta estructurada del modelo y sus métricas. Un ejemplo de como se veria: 
"id": 3,
"category": "Corrección y traducción",
"prompt": "Corrige los errores ortográficos: 'Hola, me gustaría saber si puueden enbiar el informe antes del 27 de octubre. En caso contrario, ¿poddrian avizarme con al menos 3 dias de antelación? Gracias por su atencióón.'",
"temperature": 0.7,
"response": "Aquí está tu mensaje corregido:\n\n---\n**Hola, me gustaría saber si podrían enviar el informe antes del 27 de octubre.**\n**En caso contrario, ¿podrían avisarme con al menos tres días de antelación?**\n**Gracias por su atención.**\n\n---\n\n*Cambios realizados:*\n- **\"puueden\"** → **\"podrían\"**\n- **\"enbiar\"** → **\"enviar\"**\n- **\"poddrian\"** → **\"podrían\"**\n- **\"antelación\"** → **\"antelación\"** (se mantuvo correcto, pero se ajustó para mayor claridad en \"3 días de antelación\").\n- **\"atencióón\"** → **\"atención\"** (corrección ortográfica).",
"time_seconds": 32.14,
"ttft_seconds": 3.2601,
"tokens_generated": 154,
"tokens_per_second": 5.36

