from src.infrastructure.ai.ollama_client import OllamaClient
from src.infrastructure.database.repository import FTTHRepository
from src.config.prompts import SYSTEM_PROMPT, get_interpretation_prompt

class AIService:
    """Orquesta el razonamiento de la IA sobre los datos de la red."""

    def __init__(self, ai_client: OllamaClient, repository: FTTHRepository):
        self.ai_client = ai_client
        self.repository = repository

    def is_greeting(self, text: str) -> bool:
        text = text.lower().strip()
        greetings = ["hola", "buenos dias", "buenas", "hey", "hola bot", "saludos", "que tal", "quien eres"]
        return any(greeting in text for greeting in greetings) and len(text) < 15

    async def process_question(self, question: str) -> str:
        """Procesa una pregunta del usuario y devuelve una respuesta técnica."""
        if self.is_greeting(question):
            return "¡Hola! 👋 Soy FiberMind Analytics, tu Agente IA local. Estoy listo para analizar la red. ¿Qué consulta técnica tienes?"

        try:
            # 1. Generar SQL
            prompt_sql = f"{SYSTEM_PROMPT}\nPregunta: {question}"
            sql_raw = self.ai_client.generate(prompt_sql, temperature=0.0)
            sql = self.ai_client.clean_sql(sql_raw)

            if not sql.lower().startswith("select"):
                return sql # Respuesta directa si no es SQL

            # 2. Consultar DB
            results, columns = self.repository.execute_custom_query(sql)

            # 3. Interpretar
            prompt_interpret = get_interpretation_prompt(question, sql, results, columns)
            final_answer = self.ai_client.generate(prompt_interpret, temperature=0.5)
            
            return final_answer

        except ConnectionError as e:
            return f"❌ Error de conexión: {e}"
        except Exception as e:
            return f"❌ Error en el procesamiento de IA: {e}"
