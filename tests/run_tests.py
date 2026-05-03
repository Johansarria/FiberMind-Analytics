import asyncio
from ai_engine import ask_ai

async def run_documentation_tests():
    print("--- INICIANDO PRUEBAS DE SISTEMA FIBERMIND v1.0 ---")
    
    test_questions = [
        "¿Cuántos registros de eventos tenemos en total?",
        "¿Qué hilos del CA01 tienen fallas críticas (>0.5 dB)?",
        "¿Dónde está el EMPALME 5 según los planos?",
        "Para el hilo 144, ¿cuál es la potencia estimada de llegada si salimos con +3 dBm?"
    ]
    
    results = []
    for q in test_questions:
        print(f"Pregunta: {q}")
        response = await ask_ai(q)
        results.append(f"**Pregunta:** {q}\n**Respuesta:** {response}\n")
        print(f"Respuesta obtenida.\n")
        
    with open("pruebas_sistema_v1.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    
    print("--- PRUEBAS COMPLETADAS Y GUARDADAS EN pruebas_sistema_v1.txt ---")

if __name__ == "__main__":
    asyncio.run(run_documentation_tests())
