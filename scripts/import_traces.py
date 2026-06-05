import os
import sqlite3
import sys
import argparse

from pyotdr.read import sorparse

# Configuración
DB_PATH = "ftth_mantenimiento.db"


def import_traces(trazas_dir: str, id_cable: int):
    """Importa trazas OTDR desde archivos .sor a la base de datos.

    Args:
        trazas_dir: Directorio con archivos .sor.
        id_cable: Número de cable asociado a las trazas.
    """
    # Forzar salida en UTF-8
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    if not os.path.exists(trazas_dir):
        print(f"Error: Directorio no encontrado {trazas_dir}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Opcional: Limpiar datos previos de este cable para evitar duplicados
    cursor.execute("DELETE FROM eventos_otdr WHERE id_cable = ?", (id_cable,))
    
    files = [f for f in os.listdir(trazas_dir) if f.endswith('.sor')]
    print(f"Encontrados {len(files)} archivos .sor en {trazas_dir}")

    imported_count = 0
    for filename in files:
        file_path = os.path.join(trazas_dir, filename)
        
        # Extraer ID de hilo del nombre del archivo (ej: "61.sor" -> 61)
        # Algunos archivos pueden tener espacios o texto extra (ej: "135 corregir.sor")
        try:
            hilo_str = filename.split('.')[0].split(' ')[0]
            id_hilo = int(hilo_str)
        except ValueError:
            print(f"Saltando archivo con nombre no estándar: {filename}")
            continue

        status, results, _ = sorparse(file_path)
        if status != "ok":
            print(f"Error parseando {filename}: {status}")
            continue

        key_events_block = results.get('KeyEvents', {})
        num_events = key_events_block.get('num events', 0)
        
        eventos_a_insertar = []
        for i in range(1, num_events + 1):
            ev_key = f"event {i}"
            ev_data = key_events_block.get(ev_key)
            if not ev_data:
                continue
            
            distancia = float(ev_data.get('distance', 0))
            tipo = ev_data.get('type', 'Unknown')
            # Limpiar tipo de evento de códigos raros (ej: "1S9999LS {auto}")
            if '{auto}' in tipo:
                tipo = tipo.split('{auto}')[1].strip()
            
            atenuacion = float(ev_data.get('splice loss', 0))
            
            eventos_a_insertar.append((ID_CABLE, id_hilo, distancia, tipo, atenuacion))

        if eventos_a_insertar:
            cursor.executemany('''
                INSERT INTO eventos_otdr (id_cable, id_hilo, distancia_km, tipo_evento, atenuacion_db)
                VALUES (?, ?, ?, ?, ?)
            ''', eventos_a_insertar)
            imported_count += 1

    conn.commit()
    conn.close()
    print(f"Importación completada. Se procesaron {imported_count} hilos de fibra.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importa trazas OTDR a la base de datos.")
    parser.add_argument("trazas_dir", help="Directorio con archivos .sor")
    parser.add_argument("--cable", type=int, default=1, help="Número de cable (default: 1)")
    args = parser.parse_args()
    import_traces(args.trazas_dir, args.cable)
