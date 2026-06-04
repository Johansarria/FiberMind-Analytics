# ─────────────────────────────────────────────
# FiberMind Analytics - REST API
# FastAPI con endpoints para integración con
# dashboards, NOCs y sistemas externos
# ─────────────────────────────────────────────

import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Asegurar que el paquete src sea importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.infrastructure.database.repository import FTTHRepository
from src.core.services.network_service import NetworkService
from src.utils.plotting import generate_plot

# ─── Configuración ───
DB_PATH = os.getenv("DB_PATH", "ftth_mantenimiento.db")

# ─── Inicialización ───
repo = FTTHRepository(DB_PATH)
network_service = NetworkService(repo)

app = FastAPI(
    title="FiberMind Analytics API",
    description="API REST para análisis de infraestructura FTTH - Consultas OTDR, auditoría de fallas y localización geográfica",
    version="0.2.0",
    contact={
        "name": "Johan Sarria",
        "email": "johansarria59@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
)


# ─── Schemas ───

class HealthResponse(BaseModel):
    status: str
    version: str
    db_connected: bool
    total_events: int
    mode: str

class TraceQuery(BaseModel):
    id_cable: int
    id_hilo: int

class AuditQuery(BaseModel):
    limite_db: float = 0.5
    id_cable: Optional[int] = None

class LocateQuery(BaseModel):
    nombre_elemento: str

class QuestionQuery(BaseModel):
    question: str


# ─── Endpoints ───

@app.get("/", tags=["Info"])
def root():
    return {
        "name": "FiberMind Analytics",
        "version": "0.2.0",
        "docs": "/docs",
        "status": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
def health():
    """Health check - verifica que la DB y el servicio estén operativos."""
    try:
        results, _ = repo.execute_custom_query("SELECT COUNT(*) as total FROM eventos_otdr")
        total = results[0]['total']
        db_ok = True
    except Exception:
        total = 0
        db_ok = False

    return HealthResponse(
        status="ok" if db_ok else "degraded",
        version="0.2.0",
        db_connected=db_ok,
        total_events=total,
        mode=os.getenv("FIBERMIND_MODE", "development"),
    )


@app.get("/traces/{id_cable}/{id_hilo}", tags=["OTDR"])
def get_trace(id_cable: int, id_hilo: int):
    """Obtiene los eventos OTDR registrados para un cable e hilo."""
    try:
        eventos = repo.get_hilo_events(id_cable, id_hilo)
        if not eventos:
            raise HTTPException(status_code=404, detail=f"No hay datos para Cable {id_cable}, Hilo {id_hilo}")
        return {
            "id_cable": id_cable,
            "id_hilo": id_hilo,
            "total_eventos": len(eventos),
            "eventos": [
                {
                    "distancia_km": e.distancia_km,
                    "tipo_evento": e.tipo_evento,
                    "atenuacion_db": e.atenuacion_db,
                }
                for e in eventos
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/traces/{id_cable}/{id_hilo}/plot", tags=["OTDR"])
def get_trace_plot(id_cable: int, id_hilo: int):
    """Genera y descarga la gráfica de la traza OTDR de un hilo."""
    try:
        img_path = f"/tmp/fibermind_trace_{id_cable}_{id_hilo}.png"
        result = generate_plot(id_cable, id_hilo, img_path, repo)
        if not result:
            raise HTTPException(status_code=404, detail=f"No hay datos para graficar Cable {id_cable}, Hilo {id_hilo}")
        return FileResponse(img_path, media_type="image/png", filename=f"trace_c{id_cable}_h{id_hilo}.png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/audit", tags=["Auditoría"])
def audit(body: AuditQuery):
    """Audita empalmes críticos que superen un umbral de pérdida."""
    try:
        resultado = network_service.audit_critical_splices(body.limite_db, body.id_cable)
        return {
            "limite_db": body.limite_db,
            "id_cable": body.id_cable,
            "resultado": resultado,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/infrastructure/search", tags=["Infraestructura"])
def search_infrastructure(q: str = Query(..., description="Nombre del elemento a buscar")):
    """Busca elementos de infraestructura en los planos geográficos."""
    try:
        resultado = network_service.locate_element(q)
        return {"query": q, "resultado": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/infrastructure", tags=["Infraestructura"])
def list_infrastructure():
    """Lista todos los elementos de infraestructura registrados."""
    try:
        results, columns = repo.execute_custom_query(
            "SELECT nombre_elemento, plano, x, y FROM inventario_geografico ORDER BY nombre_elemento"
        )
        return {"total": len(results), "elementos": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", tags=["IA"])
async def query(body: QuestionQuery):
    """
    Consulta en lenguaje natural usando IA local (requiere Ollama).
    Ej: "qué hilos tienen pérdidas mayores a 0.5 dB?"
    """
    try:
        from src.infrastructure.ai.ollama_client import OllamaClient
        from src.core.services.ai_service import AIService

        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")

        ai_client = OllamaClient(ollama_url, ollama_model)
        ai_service = AIService(ai_client, repo)

        respuesta = await ai_service.process_question(body.question)
        return {"question": body.question, "respuesta": respuesta}
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Ollama no disponible: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["Estadísticas"])
def get_stats():
    """Estadísticas generales de la red."""
    try:
        # Total eventos por tipo
        tipos, _ = repo.execute_custom_query(
            "SELECT tipo_evento, COUNT(*) as count FROM eventos_otdr GROUP BY tipo_evento ORDER BY count DESC"
        )
        # Total hilos monitoreados
        hilos, _ = repo.execute_custom_query(
            "SELECT id_cable, COUNT(DISTINCT id_hilo) as hilos FROM eventos_otdr GROUP BY id_cable"
        )
        # Críticos
        criticos, _ = repo.execute_custom_query(
            "SELECT COUNT(*) as total FROM eventos_otdr WHERE atenuacion_db > 0.5"
        )

        return {
            "total_eventos": sum(t['count'] for t in tipos),
            "por_tipo": tipos,
            "hilos_por_cable": hilos,
            "eventos_criticos": criticos[0]['total'] if criticos else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
