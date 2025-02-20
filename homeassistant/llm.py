import requests
import json
import time
import psutil


class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def list_models(self):
        """Lista los modelos disponibles localmente."""
        response = requests.get(f"{self.base_url}/api/tags")
        return response.json()

    def pull_model(self, model_name):
        """Descarga un modelo."""
        print(f"Descargando modelo {model_name}...")
        response = requests.post(f"{self.base_url}/api/pull", json={"name": model_name})
        return response.status_code == 200

    def generate(self, model_name, prompt, max_tokens=100):
        """Genera texto usando el modelo especificado."""
        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            }
        )
        end_time = time.time()
        return {
            "response": response.json()["response"],
            "time_taken": end_time - start_time
        }


def test_models():
    client = OllamaClient()

    # Información del sistema
    print("Información del sistema:")
    print(f"RAM Total: {psutil.virtual_memory().total / (1024 ** 3):.1f} GB")
    print(f"CPU Cores: {psutil.cpu_count()}")
    print(f"Uso actual de RAM: {psutil.virtual_memory().percent}%")

    # Modelos a probar
    models = [
        "mistral",  # Modelo base Mistral
        "llama2",  # Llama 2 base
        "neural-chat"  # Optimizado para chat
    ]

    # Prueba cada modelo
    for model_name in models:
        print(f"\nProbando modelo: {model_name}")

        # Intenta descargar el modelo si no está disponible
        try:
            client.pull_model(model_name)
        except Exception as e:
            print(f"Error descargando {model_name}: {e}")
            continue

        # Prueba de generación
        prompt = "Explica brevemente qué es la domótica y cómo puede ayudar en el hogar."
        try:
            start_memory = psutil.Process().memory_info().rss / (1024 ** 3)
            result = client.generate(model_name, prompt)
            end_memory = psutil.Process().memory_info().rss / (1024 ** 3)

            print("\nResultados:")
            print(f"Tiempo de respuesta: {result['time_taken']:.2f} segundos")
            print(f"Memoria utilizada: {end_memory - start_memory:.2f} GB")
            print(f"Respuesta: {result['response']}\n")

        except Exception as e:
            print(f"Error en la generación: {e}")


if __name__ == "__main__":
    test_models()