# ─────────────────────────────────────────────
# FiberMind Analytics - Dashboard Web
# Streamlit para visualización y consultas
# ─────────────────────────────────────────────

import os
import sys
import streamlit as st
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.infrastructure.database.repository import FTTHRepository
from src.core.services.network_service import NetworkService
from src.utils.plotting import generate_plot

# ─── Config ───
DB_PATH = os.getenv("DB_PATH", "ftth_mantenimiento.db")
st.set_page_config(page_title="FiberMind Analytics", page_icon="🔬", layout="wide")

# ─── Inicialización ───
@st.cache_resource
def load_services():
    repo = FTTHRepository(DB_PATH)
    ns = NetworkService(repo)
    return repo, ns

repo, network_service = load_services()


# ─── Sidebar ───
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 20px;'>
    <h1 style='font-size: 2.5rem;'>🔬</h1>
    <h2 style='margin: 0;'>FiberMind</h2>
    <p style='color: #888; font-size: 0.9rem;'>Analytics</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
mode = st.sidebar.radio("Modo", ["Dashboard", "Consultas", "Auditoría", "Infraestructura", "Acerca de"])


# ─── Dashboard ───
if mode == "Dashboard":
    st.title("📊 Dashboard General")

    # Stats cards
    col1, col2, col3, col4 = st.columns(4)

    try:
        results, _ = repo.execute_custom_query("SELECT COUNT(*) as total FROM eventos_otdr")
        total_events = results[0]['total']

        hilos, _ = repo.execute_custom_query("SELECT COUNT(DISTINCT id_hilo) as total FROM eventos_otdr")
        total_hilos = hilos[0]['total']

        criticos, _ = repo.execute_custom_query("SELECT COUNT(*) as total FROM eventos_otdr WHERE atenuacion_db > 0.5")
        total_criticos = criticos[0]['total']

        cables, _ = repo.execute_custom_query("SELECT COUNT(DISTINCT id_cable) as total FROM eventos_otdr")
        total_cables = cables[0]['total']
    except Exception:
        total_events = total_hilos = total_criticos = total_cables = 0

    col1.metric("📡 Eventos OTDR", total_events)
    col2.metric("🔌 Hilos monitoreados", total_hilos)
    col3.metric("⚠️ Críticos", total_criticos, delta=f"{total_criticos} alertas" if total_criticos > 0 else "0")
    col4.metric("📦 Cables", total_cables)

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
        if st.button("📊 Ver Hilo Normal (C8 H285)"):
            img = generate_plot(8, 285, "/tmp/fibermind_dash.png", repo)
            if img:
                st.image(img, caption="Traza OTDR - Cable 8, Hilo 285 (Ruta Normal)")
    with col_b:
        if st.button("⚠️ Ver Hilo Crítico (C8 H102)"):
            img = generate_plot(8, 102, "/tmp/fibermind_dash_crit.png", repo)
            if img:
                st.image(img, caption="Traza OTDR - Cable 8, Hilo 102 (Falla Crítica)")


# ─── Consultas ───
elif mode == "Consultas":
    st.title("🔍 Consulta de Hilos")
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
                    {"Distancia (km)": e.distancia_km, "Tipo Evento": e.tipo_evento, "Atenuación (dB)": e.atenuacion_db}
                    for e in eventos
                ]
                st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

                # Plot
                img = generate_plot(id_cable, id_hilo, "/tmp/fibermind_query.png", repo)
                if img:
                    st.image(img, caption=f"Traza OTDR - Cable {id_cable}, Hilo {id_hilo}")
        except Exception as e:
            st.error(f"Error: {e}")


# ─── Auditoría ───
elif mode == "Auditoría":
    st.title("⚠️ Auditoría de Empalmes Críticos")
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
    st.title("📍 Infraestructura Geográfica")
    st.markdown("Elementos registrados en los planos de red.")

    try:
        results, cols = repo.execute_custom_query(
            "SELECT nombre_elemento, plano, x, y FROM inventario_geografico ORDER BY nombre_elemento"
        )
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Búsqueda
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
    st.markdown("""
    **Versión:** 0.2.0  
    **Propósito:** Plataforma de analítica e inteligencia artificial para infraestructura FTTH  

    ### Capacidades
    - 📡 Inspección y decodificación de trazas OTDR
    - ⚠️ Detección automática de fallas críticas en empalmes
    - 📊 Visualización gráfica de potencia óptica
    - 🔍 Consultas en lenguaje natural vía IA local
    - 🗺️ Localización geográfica de infraestructura
    - 🤖 Bot de Telegram para técnicos en campo
    - 🔌 Servidor MCP para integración con asistentes IA

    ### Tech Stack
    Python • SQLite/PostgreSQL • Ollama • MCP • FastAPI • Streamlit • Telegram Bot

    ### Licencia
    MIT © {year} Johan Sarria
    """.replace("{year}", "2026"))

    st.markdown("---")
    st.markdown("💡 *Listo para producción — despliega con `docker compose up -d`*")
