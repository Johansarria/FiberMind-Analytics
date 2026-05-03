import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from src.infrastructure.database.repository import FTTHRepository
from src.core.services.network_service import NetworkService

# Configuración
DB_PATH = os.getenv("DB_PATH", "ftth_mantenimiento.db")

# Inicialización de dependencias
mcp = FastMCP("Inspector Optico FTTH MCP")
repo = FTTHRepository(DB_PATH)
network_service = NetworkService(repo)

@mcp.tool()
def consultar_ruta_hilo(id_cable: int, id_hilo: int) -> str:
    """Consulta eventos ópticos para un cable e hilo específicos."""
    return network_service.get_hilo_radiography(id_cable, id_hilo)

@mcp.tool()
def auditar_empalmes_criticos(limite_db: float, id_cable: Optional[int] = None) -> str:
    """Busca empalmes o curvaturas que superen un umbral de pérdida."""
    return network_service.audit_critical_splices(limite_db, id_cable)

@mcp.tool()
def localizar_infraestructura_plano(nombre_elemento: str) -> str:
    """Busca coordenadas y plano de un elemento físico."""
    return network_service.locate_element(nombre_elemento)

if __name__ == "__main__":
    mcp.run()
