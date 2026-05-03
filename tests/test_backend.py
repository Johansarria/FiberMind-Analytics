from ftth_mcp_server import consultar_ruta_hilo, auditar_empalmes_criticos
import sys

# Forzar salida en UTF-8 para manejar emojis en la terminal de Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def run_tests():
    print("=== TEST: Consultar Ruta (Hilo Real 61 - Cable 1) ===")
    print(consultar_ruta_hilo(1, 61))
    
    print("\n=== TEST: Auditoría de Empalmes Críticos (> 0.2 dB en Cable 1) ===")
    print(auditar_empalmes_criticos(0.2, id_cable=1))

if __name__ == "__main__":
    run_tests()
