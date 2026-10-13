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
            #Calcula las metricas entregadas por Ollama
            prompt_eval_ns = res_data.get("prompt_eval_duration", 0)
            ttft_seconds = round(prompt_eval_ns / 1e9, 4) if prompt_eval_ns else 0
            
            eval_count = res_data.get("eval_count", 0)
            eval_duration_ns = res_data.get("eval_duration", 0)
            
            tokens_per_second = 0
            if eval_count and eval_duration_ns:
                tokens_per_second = round(eval_count / (eval_duration_ns / 1e9), 2) 
            
            return {
                "response": res_data.get("response", ""),
                "total_time_s": round(elapsed, 2),
                "ttft_s": ttft_seconds,
                "tokens_generated": eval_count,
                "tokens_per_second": tokens_per_second
                
                
            }
    except urllib.error.URLError as e:
        print(f"Error al intentar conectarse con Ollama: {e.reason}") 
        print("Por favor, asegurese de tener Ollama abierto en su PC")
        return None   
        
#Definir el archivo de prompts de prueba
def main():
    suite_path = os.path.join("..","prompts", "suite.json")
    
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
        metrics = query_ollama(prompt, temperature=0.7)
        if metrics:
            results.append({
                "id": test_id,
                "category": category,
                "prompt": prompt,
                "temperature": 0.7,
                "response": metrics["response"],
                "time_seconds": metrics["total_time_s"],
                "ttft_seconds": metrics["ttft_s"],
                "tokens_generated": metrics["tokens_generated"],
                "tokens_per_second": metrics["tokens_per_second"]
                
            })

        # Repetir 2 prompts (ID 1 y ID 9) con temperaturas 0.2 y 0.9 para comparar
        if test_id in [1, 9]:
            print(f" -> Probando variaciones de temperatura de 0.2 y 0.9 para ID {test_id}...")
            for temp in [0.2, 0.9]:
                m_temp= query_ollama(prompt, temperature=temp)
                if m_temp:
                    results.append({
                        "id": f"{test_id}_temp_{temp}",
                        "category": category,
                        "prompt": prompt,
                        "temperature": 0.7,
                        "response": metrics["response"],
                        "time_seconds": metrics["total_time_s"],
                        "ttft_seconds": metrics["ttft_s"],
                        "tokens_generated": metrics["tokens_generated"],
                        "tokens_per_second": metrics["tokens_per_second"]
                    })
                if test_id in [1, 9]:
                    print(f" -> Probando variaciones de temperatura de 0.2 y 0.9 para ID {test_id}...")
                    for temp in [0.2, 0.9]:
                        m_temp= query_ollama(prompt, temperature=temp)
                        if m_temp:
                            results.append({
                                "id": f"{test_id}_temp_{temp}",
                                "category": category,
                                "prompt": prompt,
                                "temperature": temp,
                                "response": m_temp["response"],
                                "time_seconds": m_temp["total_time_s"],
                                "ttft_seconds": m_temp["ttft_s"],
                                "tokens_generated": m_temp["tokens_generated"],
                                "tokens_per_second": m_temp["tokens_per_second"]
                            }) 

    # Guardar resultados en la carpeta results/
    results_dir = os.path.join("..", "results")
    os.makedirs(results_dir, exist_ok=True)
    output_file = os.path.join(results_dir, "evaluation_results.json")
    # Guardar los resultados en un archivo JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"\n¡Pruebas finalizadas con éxito! Resultados guardados en '{output_file}'.")

if __name__ == "__main__":
    main()