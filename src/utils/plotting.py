import matplotlib.pyplot as plt
import os
from typing import Optional
from src.infrastructure.database.repository import FTTHRepository

def generate_plot(id_cable: int, id_hilo: int, output_path: str, repo: FTTHRepository) -> Optional[str]:
    """Genera una gráfica de la traza OTDR para un hilo específico."""
    try:
        eventos = repo.get_hilo_events(id_cable, id_hilo)
        
        if not eventos:
            return None

        distancias = [ev.distancia_km for ev in eventos]
        # Simulamos una curva de potencia descendente basada en la atenuación acumulada
        potencias = []
        p_actual = 3.0 # Potencia inicial en ODF
        for ev in eventos:
            p_actual -= ev.atenuacion_db
            potencias.append(p_actual)

        plt.figure(figsize=(10, 5))
        plt.step(distancias, potencias, where='post', color='cyan', linewidth=2)
        plt.fill_between(distancias, potencias, step="post", alpha=0.2, color='cyan')
        
        plt.title(f"Traza OTDR Estimada - Cable {id_cable} Hilo {id_hilo}")
        plt.xlabel("Distancia (km)")
        plt.ylabel("Potencia Estimada (dBm)")
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.axhline(y=-22, color='red', linestyle='--', label='Umbral Crítico (-22 dBm)')
        plt.legend()

        plt.savefig(output_path, facecolor='#121212')
        plt.close()
        
        return output_path

    except Exception as e:
        print(f"Error generando plot: {e}")
        return None
