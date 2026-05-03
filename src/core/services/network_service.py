from typing import List, Optional
from src.infrastructure.database.repository import FTTHRepository
from src.core.domain.models import OTDREvent, InventoryElement

class NetworkService:
    """Lógica técnica para auditoría y análisis de la infraestructura de fibra."""

    def __init__(self, repository: FTTHRepository):
        self.repository = repository

    def get_hilo_radiography(self, id_cable: int, id_hilo: int) -> str:
        """Genera un reporte textual de la ruta de un hilo."""
        eventos = self.repository.get_hilo_events(id_cable, id_hilo)
        
        if not eventos:
            return f"El hilo {id_hilo} no tiene registros. Probablemente esté activo."
            
        resultado = f"Radiografía - Cable {id_cable}, Hilo {id_hilo}:\n"
        for ev in eventos:
            resultado += f" - {ev.distancia_km} km | {ev.tipo_evento} | {ev.atenuacion_db} dB\n"
            
        return resultado

    def audit_critical_splices(self, threshold_db: float, id_cable: Optional[int] = None) -> str:
        """Busca fallas críticas que superan el umbral."""
        eventos = self.repository.get_critical_events(threshold_db, id_cable)
        
        if not eventos:
            return f"Auditoría limpia (> {threshold_db} dB)."
            
        resultado = f"⚠️ ALERTAS CRÍTICAS (> {threshold_db} dB) ⚠️\n"
        for ev in eventos:
            resultado += f" - C:{ev.id_cable} H:{ev.id_hilo} | {ev.distancia_km} km | {ev.atenuacion_db} dB\n"
            
        return resultado

    def locate_element(self, name: str) -> str:
        """Localiza un elemento en los planos."""
        element = self.repository.find_infrastructure(name)
        if element:
            return f"📍 '{element.nombre_element}' en {element.plano}. X:{element.x}, Y:{element.y}"
        return f"❌ Elemento '{name}' no encontrado."
