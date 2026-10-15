import json
import urllib.request
import urllib.error
import time
import os
import sys
import argparse

# Directorio base del script para garantizar rutas relativas seguras
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_suite(suite_path):
    """Carga la suite de pruebas desde un archivo JSON."""
    try:
        with open(suite_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] No se pudo cargar el archivo de suite en '{suite_path}': {e}")
        return None

def query_ollama(api_url, model_name, prompt_text, temperature, max_tokens):
    """
    Envía una petición POST a la API local de Ollama y calcula 
    las métricas de rendimiento exigidas (TTFT y tokens/s).
    """
    data = {
        "model": model_name,
        "prompt": prompt_text,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens
        }
    }
    
    req = urllib.request.Request(
        api_url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        start_time = time.time()
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            total_elapsed = time.time() - start_time
            
            # Métricas oficiales devueltas por Ollama (convertidas de nanosegundos a segundos)
            prompt_eval_ns = res_data.get("prompt_eval_duration", 0)
            ttft_seconds = round(prompt_eval_ns / 1e9, 4) if prompt_eval_ns else 0.0
            
            eval_count = res_data.get("eval_count", 0)
            eval_duration_ns = res_data.get("eval_duration", 0)
            
            tokens_per_second = 0.0
            if eval_count and eval_duration_ns:
                tokens_per_second = round(eval_count / (eval_duration_ns / 1e9), 2)
            
            return {
                "response": res_data.get("response", ""),
                "total_time_seconds": round(total_elapsed, 2),
                "ttft_seconds": ttft_seconds,
                "tokens_generated": eval_count,
                "tokens_per_second": tokens_per_second
            }
            
    except urllib.error.URLError as e:
        print(f"[Error de Conexión] No se pudo conectar con Ollama en {api_url}: {e.reason}")
        print("-> Verifique que el servicio de Ollama esté iniciado en su equipo.")
        return None
    except json.JSONDecodeError:
        print("[Error de Formato] La respuesta de la API no devolvió un JSON válido.")
        return None
    except Exception as e:
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
    
    args = parser.parse_args()
    
    print(f"=== Iniciando evaluación local ===")
    print(f"Modelo: {args.model} | Temperatura: {args.temperature} | Max Tokens: {args.max_tokens}")
    
    suite_data = load_suite(args.suite)
    if not suite_data:
        sys.exit(1)
        
    results = []
    tests = suite_data.get("tests", [])
    
    for test in tests:
        test_id = test.get("id")
        category = test.get("category", "General")
        prompt = test.get("prompt", "")
        
        print(f"\n[Ejecutando] Test ID {test_id} [{category}]")
        
        # 1. Ejecución estándar con la temperatura configurada por argumento
        metrics = query_ollama(args.url, args.model, prompt, args.temperature, args.max_tokens)
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
            print(f" -> Tiempo total: {metrics['total_time_seconds']}s | TTFT: {metrics['ttft_seconds']}s | Tokens/s: {metrics['tokens_per_second']}")
        
        # 2. Experimento de variación de temperatura (0.2 y 0.9) para prompts específicos (ej. ID 1 y 9)
        if test_id in [1, 9]:
            print(f" -> Ejecutando variaciones de temperatura (0.2 y 0.9) para ID {test_id}...")
            for temp in [0.2, 0.9]:
                m_var = query_ollama(args.url, args.model, prompt, temp, args.max_tokens)
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

    # Guardar resultados estructurados en formato JSON dentro de results/
    results_dir = os.path.join(SCRIPT_DIR, "..", "results")
    os.makedirs(results_dir, exist_ok=True, mode=0o777)
    output_file = os.path.join(results_dir, "evaluation_results.json")
    
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"\n[✔] Evaluación finalizada con éxito. Resultados guardados en: {output_file}")
    except Exception as e:
        print(f"[Error] No se pudo guardar el archivo de resultados: {e}")

if __name__ == "__main__":
    main()