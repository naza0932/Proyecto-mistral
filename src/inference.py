import json
import urllib.request
import urllib.error
import time
import os
#Configuración de la parte principal del modelo y la ruta del servidor local
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral:latest"
#Configuración de la función para realizar consultas al modelo Ollama
def query_ollama(prompt_text, temperature=0.7):
    data = {
        "model": MODEL_NAME,
        "prompt": prompt_text,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }
    req = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        start_time = time.time()
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            elapsed = time.time() - start_time
            return res_data.get("response", ""), elapsed
    except urllib.error.URLError as e:
        print(f"Error al querer conectarse cpn Ollama: {e.reason}")
        print("¿Asegurese de tener Ollama abierto en tu PC?")
        return None, 0
#Definir el archivo de prompts de prueba
def main():
    suite_path = os.path.join("prompts", "suite.json")
    
    if not os.path.exists(suite_path):
        print(f"Hay un error, no se encuentra el archivo {suite_path}. Revisa la ruta por favor.")
        return
    #Se carga el archivo JSON con los prompts de prueba
    with open(suite_path, "r", encoding="utf-8") as f:
        suite = json.load(f)

    results = []
    print(f"Iniciando las pruebas con el modelo '{MODEL_NAME}'...\n")
    #Iterar sobre cada prueba en el archivo JSON
    for test in suite["tests"]:
        test_id = test["id"]
        category = test["category"]
        prompt = test["prompt"]

        print(f"Procesando el Test ID {test_id} [{category}]...")
        
        # Ejecución estandar con temperatura por defecto (0.7)
        response_text, elapsed = query_ollama(prompt, temperature=0.7)
        
        results.append({
            "id": test_id,
            "category": category,
            "prompt": prompt,
            "temperature": 0.7,
            "response": response_text,
            "time_seconds": round(elapsed, 2)
        })

        # Repetir 2 prompts (ID 1 y ID 9) con temperaturas 0.2 y 0.9 para comparar
        if test_id in [1, 9]:
            print(f" -> Probando variaciones de temperatura de 0.2 y 0.9 para ID {test_id}...")
            for temp in [0.2, 0.9]:
                resp_temp, elapsed_temp = query_ollama(prompt, temperature=temp)
                results.append({
                    "id": f"{test_id}_temp_{temp}",
                    "category": category,
                    "prompt": prompt,
                    "temperature": temp,
                    "response": resp_temp,
                    "time_seconds": round(elapsed_temp, 2)
                })

    # Guardar resultados en la carpeta results/
    os.makedirs("../results", exist_ok=True)
    output_file = os.path.join("..", "results", "evaluation_results.json")
    # Guardar los resultados en un archivo JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\n¡Pruebas finalizadas con éxito! Resultados guardados en '{output_file}'.")

if __name__ == "__main__":
    main()