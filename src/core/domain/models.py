from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class OTDREvent:
    """Representa un evento óptico detectado por el OTDR."""
    id_cable: int
    id_hilo: int
    distancia_km: float
    tipo_evento: str
    atenuacion_db: float
    id: Optional[int] = None

@dataclass(frozen=True)
class InventoryElement:
    """Representa un elemento físico en el plano (Mufa, CTO, etc)."""
    nombre_element: str
    plano: str
    x: float
    y: float
    id: Optional[int] = None

@dataclass(frozen=True)
class FiberStatus:
    """Resumen del estado de una fibra específica."""
    id_cable: int
    id_hilo: int
    eventos: List[OTDREvent]
    potencia_estimada_dbm: float
    es_critica: bool
