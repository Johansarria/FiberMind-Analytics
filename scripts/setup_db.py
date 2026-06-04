import sqlite3
import os

def crear_base_datos_prueba(db_path: str = 'ftth_mantenimiento.db'):
    """Crea la base de datos SQLite con datos de prueba completos."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ─── Tabla: eventos_otdr ───
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

    # ─── Tabla: inventario_geografico ───
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventario_geografico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_elemento TEXT,
        plano TEXT,
        x REAL,
        y REAL
    )
    ''')

    # ─── Limpiar datos existentes ───
    cursor.execute('DELETE FROM eventos_otdr')
    cursor.execute('DELETE FROM inventario_geografico')

    # ─── Datos de prueba: Cable 8, Hilo 285 (Ruta Normal) ───
    eventos_normales = [
        (8, 285, 0.0, 'Salida ODF (Conector)', 0.5),
        (8, 285, 2.5, 'Empalme de Fusión', 0.1),
        (8, 285, 5.0, 'Splitter 1x8 (1er Nivel)', 10.6),
        (8, 285, 8.2, 'Empalme de Fusión', 0.2),
        (8, 285, 10.5, 'Splitter 1x8 (2do Nivel CTO)', 10.4),
        (8, 285, 10.6, 'Fin de Fibra (Macrobend/Corte)', 0.0)
    ]

    # ─── Datos de prueba: Cable 8, Hilo 102 (Ruta con Falla Crítica) ───
    eventos_criticos = [
        (8, 102, 0.0, 'Salida ODF (Conector)', 0.4),
        (8, 102, 1.2, 'Empalme de Mantenimiento', 1.8),   # ⚠️ Falla Crítica
        (8, 102, 4.0, 'Splitter 1x8 (1er Nivel)', 10.5),
        (8, 102, 6.5, 'Curvatura (Macrobend)', 0.8),      # ⚠️ Falla Crítica
        (8, 102, 9.0, 'Splitter 1x8 (2do Nivel CTO)', 10.5)
    ]

    cursor.executemany('''
        INSERT INTO eventos_otdr (id_cable, id_hilo, distancia_km, tipo_evento, atenuacion_db)
        VALUES (?, ?, ?, ?, ?)
    ''', eventos_normales + eventos_criticos)

    # ─── Datos de prueba: Inventario Geográfico ───
    elementos = [
        ('EMPALME 1', 'PLANO_RED_CHIMINANGOS', 452.3, 125.7),
        ('EMPALME 2', 'PLANO_RED_CHIMINANGOS', 523.1, 189.4),
        ('EMPALME 3', 'PLANO_RED_CHIMINANGOS', 612.8, 234.2),
        ('EMPALME 4', 'PLANO_RED_CHIMINANGOS', 745.6, 312.9),
        ('EMPALME 5', 'PLANO_RED_CHIMINANGOS', 834.2, 401.5),
        ('CTO-01', 'PLANO_RED_CHIMINANGOS', 890.1, 445.3),
        ('CTO-02', 'PLANO_RED_CHIMINANGOS', 923.7, 478.8),
        ('MUFA PRINCIPAL', 'PLANO_RED_CHIMINANGOS', 350.0, 95.0),
        ('CA08', 'PLANO_RED_CHIMINANGOS', 280.0, 80.0),
        ('SCL-16', 'PLANO_RED_CHIMINANGOS', 410.0, 110.0),
    ]

    cursor.executemany('''
        INSERT INTO inventario_geografico (nombre_elemento, plano, x, y)
        VALUES (?, ?, ?, ?)
    ''', elementos)

    conn.commit()
    conn.close()
    print(f"✅ Base de datos '{db_path}' creada con {len(eventos_normales) + len(eventos_criticos)} eventos OTDR y {len(elementos)} elementos geográficos.")

if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else 'ftth_mantenimiento.db'
    crear_base_datos_prueba(path)
