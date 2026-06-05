from pyotdr.read import sorparse
import sys
import json

def probe_sor(file_path):
    try:
        # Forzar salida en UTF-8 para la terminal
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
            
        status, results, tracedata = sorparse(file_path)
        if status != "ok":
            print(f"Error parsing: {status}")
            return

        print(f"--- Probing: {file_path} ---")
        
        key_events = results.get('KeyEvents', {})
        print("KeyEvents structure:", key_events.keys())
        events = key_events.get('events', [])
        print(f"Number of events: {len(events)}")
        if events:
            print("First event details:", events[0])
        else:
            print("No events found in 'events' list. Checking raw block...")
            print("Raw KeyEvents content:", key_events)
            
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Inspecciona estructura de un archivo .sor")
    parser.add_argument("file_path", help="Ruta al archivo .sor")
    args = parser.parse_args()
    probe_sor(args.file_path)
