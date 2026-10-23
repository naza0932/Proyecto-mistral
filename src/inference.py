import json
import urllib.request
import urllib.error
import time
import os
import sys
import argparse

# Se obtiene la carpeta donde se encuentra el scritp
#Se construye las rutas de los archivos del proyecto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_suite(suite_path):
    """Carga la suite de pruebas desde un archivo JSON."""
    try:
        #Se abre el archivo, se convierte el contenido JSON en datos de Python
        with open(suite_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        #Se informa si ocurre un error a la hora de abrir o leer el archivo
        print(f"[Error] No se pudo cargar el archivo de suite en '{suite_path}': {e}")
        return None

def query_ollama(api_url, model_name, prompt_text, temperature, max_tokens):
    """
    Envía una petición POST a la API local de Ollama y calcula 
    las métricas de rendimiento exigidas (TTFT y tokens/s).
    """
    #Prepara los datos que se envian a la API de Ollama
    data = {
        "model": model_name,
        "prompt": prompt_text,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    #Se convierte los datos a JSON, se prepara la solicutd de HTTP
    req = urllib.request.Request(
        api_url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        #Registro al momento de inciar para calcular el tiempo total
        start_time = time.time()
        #Envia la solicitud y recibe la repuesta de Ollama
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            #Va a calcular el tiempo total que tardó la solicitud 
            total_elapsed = time.time() - start_time
            
            # Métricas oficiales devueltas por Ollama (convertidas de nanosegundos a segundos)
            prompt_eval_ns = res_data.get("prompt_eval_duration", 0)
            ttft_seconds = round(prompt_eval_ns / 1e9, 4) if prompt_eval_ns else 0.0
            #Obtiene la cantidad de tokens generados y el tiempo de generación 
            eval_count = res_data.get("eval_count", 0)
            eval_duration_ns = res_data.get("eval_duration", 0)
            #Se calcula la velocidad de generación en tokens por segundo
            tokens_per_second = 0.0
            if eval_count and eval_duration_ns:
                tokens_per_second = round(eval_count / (eval_duration_ns / 1e9), 2)
            #Devuelve la repuesta y las métricas recopiladas
            return {
                "response": res_data.get("response", ""),
                "total_time_seconds": round(total_elapsed, 2),
                "ttft_seconds": ttft_seconds,
                "tokens_generated": eval_count,
                "tokens_per_second": tokens_per_second
            }
            
    except urllib.error.URLError as e:
        #Informara si no se logra conectar con el servidor de Ollama
        print(f"[Error de Conexión] No se pudo conectar con Ollama en {api_url}: {e.reason}")
        print("-> Verifique que el servicio de Ollama esté iniciado en su equipo.")
        return None
    except json.JSONDecodeError:
         #Informara si la respuesta recibida no tiene un formato JSON que sea valido
        print("[Error de Formato] La respuesta de la API no devolvió un JSON válido.")
        return None
    except Exception as e:
       #Va a capturar otros errores inesperados
        print(f"[Error Inesperado] {e}")
        return None

def main():
    # Configuración de argumentos por línea de comandos (CLI) según rúbrica
    parser = argparse.ArgumentParser(description="Script de inferencia para evaluación de Ministral con Ollama.")
    parser.add_argument("--suite", type=str, default=os.path.join(SCRIPT_DIR, "..", "prompts", "suite.json"),
                        help="Ruta relativa o absoluta al archivo JSON de la suite.")
    parser.add_argument("--model", type=str, default=os.environ.get("OLLAMA_MODEL", "ministral-3:3b"),
                        help="Nombre del modelo de Ollama a ejecutar.")
    parser.add_argument("--url", type=str, default=os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate"),
                        help="URL de la API de generación de Ollama.")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Temperatura de muestreo estándar (por defecto 0.7).")
    parser.add_argument("--max-tokens", type=int, default=512,
                        help="Número máximo de tokens a generar por respuesta.")
    #Lee los argumentos ingresados por el usuario
    args = parser.parse_args()
    #Muestra la configuración con lo que se ejecutaran las pruebas
    print(f"=== Iniciando evaluación local ===")
    print(f"Modelo: {args.model} | Temperatura: {args.temperature} | Max Tokens: {args.max_tokens}")
    #Se carga el archivo que contiene los prompts de la suite
    suite_data = load_suite(args.suite)
    #Si no se puede cargar la suite, se va a finalizar el prorgama con error
    if not suite_data:
        sys.exit(1)
    #Prepara una lista vacía para almacenar los resultados de las pruebas   
    results = []
    #Se obtiene la lista de casos de prueba del archivo JSON
    tests = suite_data.get("tests", [])
    #Recorre los casos de prueba uno por uno
    for test in tests:
        test_id = test.get("id")
        category = test.get("category", "General")
        prompt = test.get("prompt", "")
        #Informa que prueba se esta ejecutando 
        print(f"\n[Ejecutando] Test ID {test_id} [{category}]")
        
        #Envia el prompt al modelo con la configuración seleccionada 
        metrics = query_ollama(args.url, args.model, prompt, args.temperature, args.max_tokens)
        #Si se recibio una respuesta, almacena sus datos y metricas
        if metrics:
            results.append({
                "id": test_id,
                "category": category,
                "prompt": prompt,
                "temperature": args.temperature,
                "response": metrics["response"],
                "time_seconds": metrics["total_time_seconds"],
                "ttft_seconds": metrics["ttft_seconds"],
                "tokens_generated": metrics["tokens_generated"],
                "tokens_per_second": metrics["tokens_per_second"]
            })
            #Muestra algunas metricas en la terminal
            print(f" -> Tiempo total: {metrics['total_time_seconds']}s | TTFT: {metrics['ttft_seconds']}s | Tokens/s: {metrics['tokens_per_second']}")
        
        #Repite las pruebas 1 y 9 con las temperaturas de 0.2 y 0.9
        if test_id in [1, 9]:
            print(f" -> Ejecutando variaciones de temperatura (0.2 y 0.9) para ID {test_id}...")
            for temp in [0.2, 0.9]:
                #Ejecuta nuevamente el mismo prompt con otra temperatura
                m_var = query_ollama(args.url, args.model, prompt, temp, args.max_tokens)
                #Guarda los resultados de la variación si se recibio respuestas
                if m_var:
                    results.append({
                        "id": f"{test_id}_temp_{temp}",
                        "category": category,
                        "prompt": prompt,
                        "temperature": temp,
                        "response": m_var["response"],
                        "time_seconds": m_var["total_time_seconds"],
                        "ttft_seconds": m_var["ttft_s"] if "ttft_s" in m_var else m_var["ttft_seconds"],
                        "tokens_generated": m_var["tokens_generated"],
                        "tokens_per_second": m_var["tokens_per_second"]
                    })

    #Crea la carpeta de resultados si todavia no existe
    results_dir = os.path.join(SCRIPT_DIR, "..", "results")
    os.makedirs(results_dir, exist_ok=True, mode=0o777)
    #Define el archivo donde se guarda los resultados
    output_file = os.path.join(results_dir, "evaluation_results.json")
    
    try:
        #Escribe todos los resultados en un archivo JSON legible
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"\n[✔] Evaluación finalizada con éxito. Resultados guardados en: {output_file}")
    except Exception as e:
        #Informa si ocurre un problema al guardar el archivo
        print(f"[Error] No se pudo guardar el archivo de resultados: {e}")
#Ejecuta la función principal cuando se inicia este archivo directamente
if __name__ == "__main__":
    main()