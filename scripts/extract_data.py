import re
import os
import sys

# Asegurar encoding UTF-8 en Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def deep_scan_dwg_nomenclature(file_path):
    print(f"Re-analizando plano con terminología O&M: {os.path.basename(file_path)}")
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # Intentar decodificar como UTF-16LE y ASCII
        content_utf16 = content.decode('utf-16le', errors='ignore')
        content_ascii = content.decode('ascii', errors='ignore')
        
        # Patrones de búsqueda basados en el glosario
        patterns = [
            r'CTO\s*[\d-]+',
            r'EMP\s*[\d-]+',
            r'MUFA\s*[\d-]+',
            r'CA\s*[\d-]+',
            r'SCL\s*[\d-]+',
            r'SPLITTER\s*[\d/]+',
            r'PRADOS ORIENTE',
            r'CHIMINANGOS'
        ]
        
        found_elements = set()
        
        for text in [content_ascii, content_utf16]:
            for p in patterns:
                matches = re.findall(p, text, re.IGNORECASE)
                for m in matches:
                    found_elements.add(m.strip().upper())
        
        return sorted(list(found_elements))
    except Exception as e:
        return [f"Error de lectura: {e}"]

if __name__ == "__main__":
    plano_path = r"c:\MLpractica3\PLANOS\OT-00266858-CO2_PLANO DE RED_CL PRADOS ORIENTE_CA08_SCL16.dwg"
    elementos = deep_scan_dwg_nomenclature(plano_path)
    
    if elementos:
        print(f"Se identificaron {len(elementos)} elementos técnicos en el plano:")
        for el in elementos:
            print(f" - {el}")
    else:
        print("No se detectaron cadenas de texto legibles con la nomenclatura estándar en el binario.")
