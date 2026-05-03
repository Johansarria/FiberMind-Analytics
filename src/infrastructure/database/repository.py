import sqlite3
from typing import List, Optional, Tuple
from src.core.domain.models import OTDREvent, InventoryElement

class FTTHRepository:
    """Maneja la persistencia de datos en SQLite."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_hilo_events(self, id_cable: int, id_hilo: int) -> List[OTDREvent]:
        """Obtiene todos los eventos de un hilo específico."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = '''
                SELECT id, id_cable, id_hilo, distancia_km, tipo_evento, atenuacion_db 
                FROM eventos_otdr 
                WHERE id_cable = ? AND id_hilo = ?
                ORDER BY distancia_km ASC
            '''
            cursor.execute(query, (id_cable, id_hilo))
            rows = cursor.fetchall()
            return [OTDREvent(**dict(row)) for row in rows]

    def get_critical_events(self, threshold_db: float, id_cable: Optional[int] = None) -> List[OTDREvent]:
        """Obtiene eventos que superan un umbral de atenuación, excluyendo splitters."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if id_cable is not None:
                query = '''
                    SELECT id, id_cable, id_hilo, distancia_km, tipo_evento, atenuacion_db 
                    FROM eventos_otdr 
                    WHERE atenuacion_db > ? 
                    AND id_cable = ?
                    AND LOWER(tipo_evento) NOT LIKE '%splitter%'
                    ORDER BY atenuacion_db DESC
                '''
                cursor.execute(query, (threshold_db, id_cable))
            else:
                query = '''
                    SELECT id, id_cable, id_hilo, distancia_km, tipo_evento, atenuacion_db 
                    FROM eventos_otdr 
                    WHERE atenuacion_db > ? 
                    AND LOWER(tipo_evento) NOT LIKE '%splitter%'
                    ORDER BY atenuacion_db DESC
                '''
                cursor.execute(query, (threshold_db,))
            
            rows = cursor.fetchall()
            return [OTDREvent(**dict(row)) for row in rows]

    def find_infrastructure(self, name: str) -> Optional[InventoryElement]:
        """Busca un elemento de inventario por nombre."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nombre_elemento as nombre_element, plano, x, y FROM inventario_geografico WHERE nombre_elemento LIKE ?", 
                (f"%{name}%",)
            )
            row = cursor.fetchone()
            if row:
                return InventoryElement(**dict(row))
            return None

    def execute_custom_query(self, sql: str) -> Tuple[List[dict], List[str]]:
        """Ejecuta una consulta SQL personalizada (usada por el motor de IA)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(row) for row in results], columns
