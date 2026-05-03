import requests
import json
from typing import Optional, Dict, Any

class OllamaClient:
    """Cliente para interactuar con la API local de Ollama."""

    def __init__(self, url: str, model: str, timeout: int = 60):
        self.url = url
        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Envía un prompt a Ollama y devuelve la respuesta."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            }
            response = requests.post(self.url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error al conectar con Ollama: {e}")
        except Exception as e:
            raise RuntimeError(f"Error inesperado en el cliente Ollama: {e}")

    def clean_sql(self, sql_text: str) -> str:
        """Limpia el código SQL devuelto por la IA."""
        return sql_text.replace("```sql", "").replace("```", "").strip()
