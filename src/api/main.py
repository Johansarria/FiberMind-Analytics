# ─────────────────────────────────────────────
# FiberMind Analytics - REST API (Multi-ISP)
# FastAPI con soporte multi-cliente via X-ISP-ID
# ─────────────────────────────────────────────

import logging
import os
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.config.isp_config import get_config, reload_config
from src.utils.plotting import generate_plot

# ─── Inicialización ───
logger = logging.getLogger(__name__)

config = get_config(os.getenv("FIBERMIND_CONFIG"))

app = FastAPI(
    title="FiberMind Analytics API",
    description="API REST multi-ISP para análisis de infraestructura FTTH — Consultas OTDR, "
                "auditoría de fallas y localización geográfica. "
                "Usa header X-ISP-ID para seleccionar el cliente.",
    version="0.3.0",
    contact={"name": "Johan Sarria", "email": "johansarria59@gmail.com"},
    license_info={"name": "MIT"},
)

# ─── CORS (permitir acceso multiplataforma) ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Helpers ───

def resolve_isp(x_isp_id: Optional[str] = None):
    """Resuelve ISP desde header o default. Retorna el ISPConfig."""
    try:
        return config.get_isp(x_isp_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ─── Schemas ───

class AuditBody(BaseModel):
    limite_db: float = 0.5
    id_cable: Optional[int] = None

class QueryBody(BaseModel):
    question: str


# ─── Endpoints ───

@app.get("/health", tags=["Info"])
def health(x_isp_id: Optional[str] = Header(None)):
    """Health check para un ISP específico."""
    try:
        isp = resolve_isp(x_isp_id)
        repo = config.get_repo(isp.id)
        results, _ = repo.execute_custom_query("SELECT COUNT(*) as total FROM eventos_otdr")
        total = results[0]['total']
        db_ok = True
    except Exception as exc:
        logger.warning("Health check falló para ISP %s: %s", x_isp_id or 'default', exc)
        total = 0
        db_ok = False
        isp = resolve_isp(x_isp_id)

    return {
        "status": "ok" if db_ok else "degraded",
        "version": "0.3.0",
        "isp": isp.id,
        "isp_name": isp.name,
        "db_connected": db_ok,
        "total_events": total,
        "ollama_model": isp.ollama_model,
        "city": isp.city,
        "mode": os.getenv("FIBERMIND_MODE", "development"),
    }


@app.get("/isps", tags=["Multi-ISP"])
def list_isps():
    """Lista todos los ISPs disponibles."""
    return {
        "default": config.default_isp,
        "isps": config.list_isps(),
        "loaded_from": config._loaded_path or "defaults (env vars)",
    }


@app.get("/traces/{id_cable}/{id_hilo}", tags=["OTDR"])
def get_trace(id_cable: int, id_hilo: int, x_isp_id: Optional[str] = Header(None)):
    """Obtiene los eventos OTDR para un cable/hilo de un ISP específico."""
    isp = resolve_isp(x_isp_id)
    try:
        repo = config.get_repo(isp.id)
        eventos = repo.get_hilo_events(id_cable, id_hilo)
        if not eventos:
            raise HTTPException(
                status_code=404,
                detail=f"No hay datos para {isp.name}: Cable {id_cable}, Hilo {id_hilo}"
            )
        return {
            "isp": isp.id,
            "isp_name": isp.name,
            "id_cable": id_cable,
            "id_hilo": id_hilo,
            "total_eventos": len(eventos),
            "eventos": [
                {"distancia_km": ev.distancia_km, "tipo_evento": ev.tipo_evento, "atenuacion_db": ev.atenuacion_db}
                for ev in eventos
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/traces/{id_cable}/{id_hilo}/plot", tags=["OTDR"])
def get_trace_plot(id_cable: int, id_hilo: int, x_isp_id: Optional[str] = Header(None)):
    """Genera y descarga el gráfico de traza OTDR para un ISP específico."""
    isp = resolve_isp(x_isp_id)
    try:
        repo = config.get_repo(isp.id)
        img_path = f"/tmp/fibermind_{isp.id}_c{id_cable}_h{id_hilo}.png"
        result = generate_plot(id_cable, id_hilo, img_path, repo)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No hay datos para graficar en {isp.name}: Cable {id_cable}, Hilo {id_hilo}"
            )
        return FileResponse(img_path, media_type="image/png", filename=f"{isp.id}_c{id_cable}_h{id_hilo}.png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/audit", tags=["Auditoría"])
def audit(body: AuditBody, x_isp_id: Optional[str] = Header(None)):
    """Audita empalmes críticos que superen un umbral para un ISP específico."""
    isp = resolve_isp(x_isp_id)
    try:
        ns = config.get_network_service(isp.id)
        resultado = ns.audit_critical_splices(body.limite_db, body.id_cable)
        return {
            "isp": isp.id,
            "isp_name": isp.name,
            "limite_db": body.limite_db,
            "id_cable": body.id_cable,
            "resultado": resultado,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/infrastructure/search", tags=["Infraestructura"])
def search_infrastructure(q: str = Query(..., description="Nombre del elemento"), x_isp_id: Optional[str] = Header(None)):
    """Busca elementos de infraestructura en los planos de un ISP."""
    isp = resolve_isp(x_isp_id)
    try:
        ns = config.get_network_service(isp.id)
        resultado = ns.locate_element(q)
        return {"isp": isp.id, "isp_name": isp.name, "query": q, "resultado": resultado}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/infrastructure", tags=["Infraestructura"])
def list_infrastructure(x_isp_id: Optional[str] = Header(None)):
    """Lista todos los elementos de infraestructura de un ISP."""
    isp = resolve_isp(x_isp_id)
    try:
        repo = config.get_repo(isp.id)
        results, columns = repo.execute_custom_query(
            "SELECT nombre_elemento, plano, x, y FROM inventario_geografico ORDER BY nombre_elemento"
        )
        return {"isp": isp.id, "isp_name": isp.name, "total": len(results), "elementos": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", tags=["IA"])
async def query(body: QueryBody, x_isp_id: Optional[str] = Header(None)):
    """Consulta en lenguaje natural usando IA local (requiere Ollama)."""
    isp = resolve_isp(x_isp_id)
    try:
        from src.infrastructure.ai.ollama_client import OllamaClient
        from src.core.services.ai_service import AIService

        ai_client = OllamaClient(isp.ollama_url, isp.ollama_model)
        repo = config.get_repo(isp.id)
        ai_service = AIService(ai_client, repo)

        respuesta = await ai_service.process_question(body.question)
        return {
            "isp": isp.id,
            "isp_name": isp.name,
            "question": body.question,
            "respuesta": respuesta,
            "model": isp.ollama_model,
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Ollama no disponible para {isp.name}: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", tags=["Estadísticas"])
def get_stats(x_isp_id: Optional[str] = Header(None)):
    """Estadísticas generales de la red de un ISP."""
    isp = resolve_isp(x_isp_id)
    try:
        repo = config.get_repo(isp.id)

        tipos, _ = repo.execute_custom_query(
            "SELECT tipo_evento, COUNT(*) as count FROM eventos_otdr GROUP BY tipo_evento ORDER BY count DESC"
        )
        hilos, _ = repo.execute_custom_query(
            "SELECT id_cable, COUNT(DISTINCT id_hilo) as hilos FROM eventos_otdr GROUP BY id_cable"
        )
        criticos, _ = repo.execute_custom_query(
            "SELECT COUNT(*) as total FROM eventos_otdr WHERE atenuacion_db > 0.5"
        )

        return {
            "isp": isp.id,
            "isp_name": isp.name,
            "total_eventos": sum(tipo['count'] for tipo in tipos),
            "por_tipo": tipos,
            "hilos_por_cable": hilos,
            "eventos_criticos": criticos[0]['total'] if criticos else 0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Dashboard HTML estático ───
DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), "..", "dashboard-html")

if os.path.isdir(DASHBOARD_DIR):
    app.mount("/app", StaticFiles(directory=DASHBOARD_DIR, html=True), name="dashboard")

    @app.get("/")
    async def root():
        """Redirige al dashboard."""
        return FileResponse(os.path.join(DASHBOARD_DIR, "index.html"))
else:
    @app.get("/")
    async def root():
        return {"status": "FiberMind API", "version": "0.3.0", "dashboard": "Not installed"}
