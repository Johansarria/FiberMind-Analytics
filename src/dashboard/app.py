# ─────────────────────────────────────────────
# FiberMind Analytics - Dashboard Web (Multi-ISP)
# Streamlit con selector de ISP en sidebar
# ─────────────────────────────────────────────

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.config.isp_config import get_config, reload_config
from src.utils.plotting import generate_plot

# ─── Config ───
FIBERMIND_CONFIG = os.getenv("FIBERMIND_CONFIG", "")

st.set_page_config(page_title="FiberMind Analytics", page_icon="🔬", layout="wide")


# ─── Carga de ISP ───
@st.cache_resource
def load_config():
    return get_config(FIBERMIND_CONFIG)

config = load_config()


def get_isp_services(isp_id: str):
    """Retorna repo y network_service para el ISP seleccionado."""
    repo = config.get_repo(isp_id)
    ns = config.get_network_service(isp_id)
    return repo, ns


# ─── Sidebar ───
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 20px;'>
    <h1 style='font-size: 2.5rem; margin: 0;'>🔬</h1>
    <h2 style='margin: 0;'>FiberMind</h2>
    <p style='color: #888; font-size: 0.9rem; margin: 0;'>Analytics</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# ─── Selector de ISP ───
available_isps = config.get_available_isps()
if available_isps:
    isp_options = {isp_id: f"{config.get_isp(isp_id).name} ({isp_id})" for isp_id in available_isps}
    default_idx = list(available_isps).index(config.default_isp) if config.default_isp in available_isps else 0
    selected_isp = st.sidebar.selectbox(
        "🌐 ISP / Cliente",
        options=list(isp_options.keys()),
        format_func=lambda x: isp_options[x],
        index=default_idx,
        key="isp_selector",
    )

    # Mostrar info del ISP
    isp_info = config.get_isp(selected_isp)
    st.sidebar.markdown(f"""
    **{isp_info.name}**  
    🏙️ {isp_info.city or '—'}  
    🤖 {isp_info.ollama_model}  
    📍 `{isp_info.db_path}`
    """)
else:
    selected_isp = "default"
    st.sidebar.warning("No hay ISPs configurados.")

st.sidebar.markdown("---")
mode = st.sidebar.radio("Modo", ["Dashboard", "Consultas", "Auditoría", "Infraestructura", "Acerca de"])

# Recargar servicios si cambia el ISP
repo, network_service = get_isp_services(selected_isp)


# ─── Dashboard ───
if mode == "Dashboard":
    st.title(f"📊 {isp_info.name}")

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)

    try:
        results, _ = repo.execute_custom_query("SELECT COUNT(*) as total FROM eventos_otdr")
        total_events = results[0]['total'] if results else 0
    except:
        total_events = 0

    try:
        hilos, _ = repo.execute_custom_query("SELECT COUNT(DISTINCT id_hilo) as total FROM eventos_otdr")
        total_hilos = hilos[0]['total'] if hilos else 0
    except:
        total_hilos = 0

    try:
        criticos, _ = repo.execute_custom_query("SELECT COUNT(*) as total FROM eventos_otdr WHERE atenuacion_db > 0.5")
        total_criticos = criticos[0]['total'] if criticos else 0
    except:
        total_criticos = 0

    try:
        cables, _ = repo.execute_custom_query("SELECT COUNT(DISTINCT id_cable) as total FROM eventos_otdr")
        total_cables = cables[0]['total'] if cables else 0
    except:
        total_cables = 0

    col1.metric("📡 Eventos OTDR", total_events)
    col2.metric("🔌 Hilos monitoreados", total_hilos)
    col3.metric("⚠️ Críticos", total_criticos,
                delta=f"{total_criticos} alertas" if total_criticos > 0 else "0")
    col4.metric("📦 Cables", total_cables)

    if total_events > 0:
        # Tabla de eventos por tipo
        st.subheader("📋 Eventos por Tipo")
        try:
            tipos, cols = repo.execute_custom_query(
                "SELECT tipo_evento, COUNT(*) as count FROM eventos_otdr GROUP BY tipo_evento ORDER BY count DESC"
            )
            df = pd.DataFrame(tipos)
            st.dataframe(df, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error cargando datos: {e}")

        # Últimas trazas
        st.subheader("🕐 Últimas Trazas")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📊 Ver Traza Normal"):
                img = generate_plot(8, 285, "/tmp/fibermind_dash.png", repo)
                if img:
                    st.image(img, caption="Traza OTDR — Ruta Normal")
        with col_b:
            if st.button("⚠️ Ver Traza Crítica"):
                img = generate_plot(8, 102, "/tmp/fibermind_dash_crit.png", repo)
                if img:
                    st.image(img, caption="Traza OTDR — Falla Crítica")
    else:
        st.info("📭 No hay datos para este ISP aún. Corre `python scripts/setup_db.py` para cargar datos de prueba.")
        if isp_info.city:
            st.markdown(f"📍 **{isp_info.name}** — {isp_info.city}")
            st.markdown(f"📁 DB: `{isp_info.db_path}`")


# ─── Consultas ───
elif mode == "Consultas":
    st.title(f"🔍 Consulta de Hilos — {isp_info.name}")
    st.markdown("Consulta eventos OTDR por cable e hilo.")

    col1, col2 = st.columns(2)
    with col1:
        id_cable = st.number_input("ID Cable", min_value=1, value=8)
    with col2:
        id_hilo = st.number_input("ID Hilo", min_value=1, value=285)

    if st.button("🔎 Consultar", type="primary"):
        try:
            eventos = repo.get_hilo_events(id_cable, id_hilo)
            if not eventos:
                st.warning(f"No hay datos para Cable {id_cable}, Hilo {id_hilo}")
            else:
                st.success(f"✅ {len(eventos)} eventos encontrados")
                data = [
                    {"Distancia (km)": e.distancia_km, "Tipo Evento": e.tipo_evento,
                     "Atenuación (dB)": e.atenuacion_db}
                    for e in eventos
                ]
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

                img = generate_plot(id_cable, id_hilo, "/tmp/fibermind_query.png", repo)
                if img:
                    st.image(img, caption=f"Traza OTDR — Cable {id_cable}, Hilo {id_hilo}")
        except Exception as e:
            st.error(f"Error: {e}")


# ─── Auditoría ───
elif mode == "Auditoría":
    st.title(f"⚠️ Auditoría de Empalmes Críticos — {isp_info.name}")
    st.markdown("Detecta empalmes y curvaturas que superan el umbral de pérdida permitido.")

    col1, col2 = st.columns(2)
    with col1:
        limite_db = st.slider("Umbral crítico (dB)", 0.1, 3.0, 0.5, 0.1)
    with col2:
        id_cable = st.number_input("Filtrar por Cable (opcional)", min_value=0, value=8)

    if st.button("🔎 Ejecutar Auditoría", type="primary"):
        cable_param = id_cable if id_cable > 0 else None
        resultado = network_service.audit_critical_splices(limite_db, cable_param)

        if "limpia" in resultado.lower():
            st.success(resultado)
        else:
            st.warning(resultado)


# ─── Infraestructura ───
elif mode == "Infraestructura":
    st.title(f"📍 Infraestructura Geográfica — {isp_info.name}")

    try:
        results, cols = repo.execute_custom_query(
            "SELECT nombre_elemento, plano, x, y FROM inventario_geografico ORDER BY nombre_elemento"
        )
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True, hide_index=True)

            search = st.text_input("🔍 Buscar elemento", placeholder="Ej: EMPALME 3")
            if search:
                resultado = network_service.locate_element(search)
                st.info(resultado)
        else:
            st.warning("No hay elementos registrados en el inventario.")
    except Exception as e:
        st.error(f"Error: {e}")


# ─── Acerca de ───
elif mode == "Acerca de":
    st.title("🔬 FiberMind Analytics")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"""
        **Versión:** 0.3.0  
        **ISP activo:** {isp_info.name}  
        **Ciudad:** {isp_info.city or '—'}  
        **Base de datos:** `{isp_info.db_path}`  
        **Modelo IA:** {isp_info.ollama_model}  

        ### Capacidades
        - 📡 Inspección y decodificación de trazas OTDR
        - ⚠️ Detección automática de fallas críticas
        - 📊 Visualización gráfica de potencia óptica
        - 🔍 Consultas en lenguaje natural vía IA local
        - 🗺️ Localización geográfica de infraestructura
        - 🤖 Bot de Telegram para técnicos en campo
        - 🔌 Servidor MCP para integración con asistentes IA
        - 🌐 **Multi-ISP:** Un solo servidor, múltiples clientes
        """)
    with col2:
        isps = config.list_isps()
        if isps:
            st.markdown("### 🌐 ISPs Configurados")
            for isp in isps:
                icon = "✅" if isp["db_exists"] else "❌"
                city = config.get_isp(isp["id"]).city
                st.markdown(f"{icon} **{isp['name']}** ({isp['id']}) — {city or '—'}")

    st.markdown("---")
    st.markdown("💡 *Despliega con `docker compose --profile all up -d`*")
