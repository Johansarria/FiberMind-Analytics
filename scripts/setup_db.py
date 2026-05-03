import sqlite3

def crear_base_datos_prueba():
    conn = sqlite3.connect('ftth_mantenimiento.db')
    cursor = conn.cursor()

    # Crear tabla de eventos OTDR
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS eventos_otdr (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cable INTEGER,
        id_hilo INTEGER,
        distancia_km REAL,
        tipo_evento TEXT,
        atenuacion_db REAL
    )
    ''')

    # Limpiar tabla si ya existía para evitar duplicados en cada ejecución
    cursor.execute('DELETE FROM eventos_otdr')

    # Insertar datos de prueba para Cable 8, Hilo 285 (Ruta Normal)
    eventos_normales = [
        (8, 285, 0.0, 'Salida ODF (Conector)', 0.5),
        (8, 285, 2.5, 'Empalme de Fusión', 0.1),
        (8, 285, 5.0, 'Splitter 1x8 (1er Nivel)', 10.6),
        (8, 285, 8.2, 'Empalme de Fusión', 0.2),
        (8, 285, 10.5, 'Splitter 1x8 (2do Nivel CTO)', 10.4),
        (8, 285, 10.6, 'Fin de Fibra (Macrobend/Corte)', 0.0)
    ]
    
    # Insertar datos de prueba para Cable 8, Hilo 102 (Ruta con Falla Crítica)
    eventos_criticos = [
        (8, 102, 0.0, 'Salida ODF (Conector)', 0.4),
        (8, 102, 1.2, 'Empalme de Mantenimiento', 1.8), # Falla Crítica
        (8, 102, 4.0, 'Splitter 1x8 (1er Nivel)', 10.5),
        (8, 102, 6.5, 'Curvatura (Macrobend)', 0.8), # Falla Crítica
        (8, 102, 9.0, 'Splitter 1x8 (2do Nivel CTO)', 10.5)
    ]

    cursor.executemany('''
        INSERT INTO eventos_otdr (id_cable, id_hilo, distancia_km, tipo_evento, atenuacion_db)
        VALUES (?, ?, ?, ?, ?)
    ''', eventos_normales + eventos_criticos)

    conn.commit()
    conn.close()
    print("Base de datos de prueba 'ftth_mantenimiento.db' creada con éxito.")

if __name__ == "__main__":
    crear_base_datos_prueba()
