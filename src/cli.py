# ─────────────────────────────────────────────
# fibermind — CLI para gestión de ISPs
# ─────────────────────────────────────────────
# Uso:
#   python -m src.cli isps              → Listar ISPs
#   python -m src.cli isps --add        → Agregar ISP
#   python -m src.cli isps --id=nombre  → Ver detalle
#   python -m src.cli check             → Verificar estado
#   python -m src.cli init              → Inicializar config
# ─────────────────────────────────────────────

import sys, os, argparse, textwrap

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.isp_config import get_config, FiberMindConfig


def cmd_isps(args):
    """Lista y gestiona ISPs."""
    config = get_config()

    if args.detail:
        try:
            isp = config.get_isp(args.detail)
            print(f"\n🔌 ISP: {isp.id}")
            print(f"   Nombre:        {isp.name}")
            print(f"   DB:            {isp.db_path}")
            print(f"   Ollama URL:    {isp.ollama_url}")
            print(f"   Ollama Model:  {isp.ollama_model}")
            print(f"   Ciudad:        {isp.city}")
            print(f"   Coordenadas:   {isp.lat}, {isp.lon}")
            print(f"   Telegram:      {'✓ configurado' if isp.telegram_token else '✗ no configurado'}")
        except KeyError as e:
            print(f"❌ {e}")
        return

    isps = config.list_isps()
    if not isps:
        print("📭 No hay ISPs configurados.")
        return

    print(f"\n🔌 ISPs disponibles ({len(isps)})\n")
    print(f"   {'ID':<20} {'Nombre':<25} {'Ciudad':<15} {'DB'}")
    print(f"   {'─'*70}")
    for isp in isps:
        default_mark = "★" if isp["id"] == config.default_isp else " "
        db_status = "✓" if isp["db_exists"] else "✗"
        print(f"   {default_mark} {isp['id']:<18} {isp['name']:<25} {isp['city']:<15} {db_status}")
    print()


def cmd_check(args):
    """Verifica el estado de todos los ISPs."""
    config = get_config()

    print("\n🔬 FiberMind — Health Check\n")
    print(f"   Config loaded from: {config._loaded_path or 'defaults (env)'}")
    print(f"   Default ISP:        {config.default_isp}")
    print(f"   Total ISPs:         {len(config.isps)}\n")

    for isp_id in config.get_available_isps():
        isp = config.get_isp(isp_id)
        repo_ok = db_ok = False
        event_count = 0
        try:
            repo = config.get_repo(isp.id)
            results, _ = repo.execute_custom_query("SELECT COUNT(*) as total FROM eventos_otdr")
            event_count = results[0]['total']
            repo_ok = True
            db_ok = True
        except Exception as e:
            db_ok = str(e)

        status_icon = "✅" if repo_ok else "❌"
        print(f"   {status_icon} {isp.name} ({isp.id})")
        print(f"       DB:     {isp.db_path}")
        print(f"       State:  {'✓ conectada' if repo_ok else '✗ '+str(db_ok)}")
        print(f"       Events: {event_count}")
        print()


def cmd_init(args):
    """Inicializa un archivo de configuración por defecto."""
    example_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "fibermind.example.yml")
    target = args.file or "fibermind.yml"

    if os.path.exists(target):
        print(f"⚠️  {target} ya existe. No se sobrescribe.")
        return

    if os.path.exists(example_path):
        with open(example_path) as f:
            content = f.read()
        with open(target, "w") as f:
            f.write(content)
        print(f"✅ Config creada: {target}")
        print(f"   Edítala con: nano {target}")
    else:
        print(f"❌ No se encontró {example_path}")


def main():
    parser = argparse.ArgumentParser(
        prog="fibermind",
        description="FiberMind Analytics — Multi-ISP Configuration CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando")

    # isps
    p_isps = subparsers.add_parser("isps", help="Listar ISPs")
    p_isps.add_argument("--detail", "-d", type=str, default="", help="Ver detalle de un ISP específico")

    # check
    p_check = subparsers.add_parser("check", help="Verificar estado de todos los ISPs")

    # init
    p_init = subparsers.add_parser("init", help="Crear archivo de configuración inicial")
    p_init.add_argument("--file", "-f", type=str, default="fibermind.yml", help="Ruta del archivo a crear")

    args = parser.parse_args()

    if args.command == "isps":
        cmd_isps(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "init":
        cmd_init(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
