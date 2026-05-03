import sys
from pyotdr.read import sorparse

def probe_datapts(file_path):
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    status, results, tracedata = sorparse(file_path)
    if status != "ok":
        print(f"Error parsing: {status}")
        return

    print(f"--- Probing DataPts: {file_path} ---")
    print(f"Tracedata type: {type(tracedata)}")
    if isinstance(tracedata, list):
        print(f"Tracedata length: {len(tracedata)}")
        if len(tracedata) > 0:
            print(f"First 5 points: {tracedata[:5]}")
            print(f"Last 5 points: {tracedata[-5:]}")
    elif isinstance(tracedata, dict):
        print("Tracedata keys:", tracedata.keys())

if __name__ == "__main__":
    probe_datapts(r"C:\MLpractica3\TRAZAS\Centrales\Chiminangos\CABLE 1\144.sor")
