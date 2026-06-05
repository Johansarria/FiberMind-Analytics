"""Test básicos del backend FiberMind."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.infrastructure.database.repository import FTTHRepository
from src.core.domain.models import OTDREvent


class TestFTTHRepository:
    """Pruebas unitarias del repositorio usando base de datos en memoria."""

    def setup_method(self):
        self.repo = FTTHRepository(":memory:")

    def test_get_hilo_events_returns_empty_when_no_data(self):
        """Debe retornar lista vacía cuando no hay eventos."""
        events = self.repo.get_hilo_events(1, 1)
        assert events == []

    def test_otdr_event_creation(self):
        """Debe crear un evento OTDR con todos sus campos."""
        event = OTDREvent(
            id=1, id_cable=1, id_hilo=1,
            distancia_km=10.5, tipo_evento="Empalme",
            atenuacion_db=0.15
        )
        assert event.id_cable == 1
        assert event.tipo_evento == "Empalme"
        assert event.atenuacion_db == 0.15
        assert event.distancia_km == 10.5
