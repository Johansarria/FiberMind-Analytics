import requests
import json

def test_ollama():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5-coder:1.5b",
        "prompt": "Hola, responde con la palabra 'LISTO' si puedes leer esto.",
        "stream": False
    }
    try:
        print("Enviando petición a Ollama...")
        response = requests.post(url, json=payload, timeout=10)
        print(f"Respuesta de Ollama: {response.json()['response']}")
    except Exception as e:
        print(f"Error conectando con Ollama: {e}")

if __name__ == "__main__":
    test_ollama()
