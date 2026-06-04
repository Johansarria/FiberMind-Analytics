# ─────────────────────────────────────────────
# FiberMind Analytics — Dashboard NOC
# Estilo oscuro premium, tipo SaaS profesional
# ─────────────────────────────────────────────
# No parece Streamlit. Se ve como producto real.
# ─────────────────────────────────────────────

import os, sys, json, time, textwrap
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

from src.config.isp_config import get_config
from src.utils.plotting import generate_plot

# ─── Config ─────────────────────────────────
FIBERMIND_CONFIG = os.getenv("FIBERMIND_CONFIG", "")
st.set_page_config(page_title="FiberMind", page_icon="🔬", layout="wide", initial_sidebar_state="expanded")

# ─── Tema oscuro premium ────────────────────
C = {
    "bg": "#0A0E17",
    "card": "#111827",
    "card_border": "#1E293B",
    "card_hover": "#1A2332",
    "text": "#E2E8F0",
    "text_dim": "#64748B",
    "accent": "#00D4AA",       # verde fibra
    "accent_dim": "#059669",
    "blue": "#3B82F6",
    "red": "#EF4444",
    "amber": "#F59E0B",
    "purple": "#8B5CF6",
    "divider": "#1E293B",
}

CSS = f"""
<style>
    /* === Reset Streamlit === */
    #MainMenu, header, footer, .stAppDeployButton, .stDecoration, .stToolbar {{
        display: none !important;
    }}
    .stApp {{
        background: {C['bg']};
        color: {C['text']};
    }}
    div[data-testid="stSidebar"] {{
        background: {C['card']} !important;
        border-right: 1px solid {C['card_border']} !important;
    }}
    div[data-testid="stSidebar"] .sidebar-content {{
        background: {C['card']};
    }}
    .stSelectbox label, .stRadio label, .stSlider label {{
        color: {C['text_dim']} !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    div[data-testid="stSelectbox"] > div:first-child {{
        background: {C['bg']} !important;
        border: 1px solid {C['card_border']} !important;
        border-radius: 8px !important;
        color: {C['text']} !important;
    }}
    div[data-testid="stSelectbox"] > div:first-child:hover {{
        border-color: {C['accent']} !important;
    }}
    /* Metric Cards */
    div[data-testid="metric-container"] {{
        background: {C['card']};
        border: 1px solid {C['card_border']};
        border-radius: 12px;
        padding: 16px 20px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }}
    div[data-testid="metric-container"]:hover {{
        border-color: {C['accent']}33;
        box-shadow: 0 0 20px {C['accent']}11;
        background: {C['card_hover']};
    }}
    div[data-testid="metric-container"] label {{
        color: {C['text_dim']} !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    div[data-testid="metric-container"] div[data-testid="metric-value"] {{
        color: {C['text']} !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        line-height: 1.2;
    }}
    /* Botones */
    .stButton button {{
        background: linear-gradient(135deg, {C['accent']}, {C['accent_dim']}) !important;
        color: {C['bg']} !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 24px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px {C['accent']}44 !important;
    }}
    .stButton button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 16px {C['accent']}66 !important;
    }}
    .stButton button:active {{
        transform: translateY(0);
    }}
    /* DataFrames */
    div[data-testid="stDataFrame"] {{
        background: transparent !important;
    }}
    div[data-testid="stDataFrame"] div[data-testid="stDataFrameContainer"] {{
        background: {C['card']} !important;
        border: 1px solid {C['card_border']} !important;
        border-radius: 12px !important;
        padding: 4px;
    }}
    div[data-testid="stDataFrame"] thead tr th {{
        background: {C['bg']} !important;
        color: {C['text_dim']} !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 1px solid {C['card_border']} !important;
    }}
    /* Expander / Info boxes */
    div[data-testid="stExpander"] {{
        border: 1px solid {C['card_border']} !important;
        border-radius: 12px !important;
        background: {C['card']} !important;
    }}
    .stInfo, .stAlert {{
        background: {C['card']} !important;
        border: 1px solid {C['card_border']} !important;
        border-radius: 12px !important;
        color: {C['text']} !important;
    }}
    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {C['bg']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {C['card_border']};
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {C['text_dim']};
    }}
    /* Titles */
    h1, h2, h3, h4 {{
        color: {C['text']} !important;
    }}
    /* Multi-ISP badge */
    .isp-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: {C['bg']};
        border: 1px solid {C['card_border']};
        border-radius: 20px;
        padding: 4px 14px 4px 10px;
        font-size: 0.8rem;
        color: {C['text_dim']};
    }}
    .isp-badge .dot {{
        width: 8px; height: 8px;
        border-radius: 50%;
        display: inline-block;
    }}
    .isp-badge .dot.online {{ background: {C['accent']}; }}
    .isp-badge .dot.offline {{ background: {C['red']}; }}
    /* Header */
    .app-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 24px;
    }}
    .app-header h1 {{
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .app-header .header-right {{
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.8rem;
        color: {C['text_dim']};
    }}
    .status-dot {{
        width: 10px; height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }}
    .status-dot.online {{ background: {C['accent']}; box-shadow: 0 0 8px {C['accent']}66; }}
    .status-dot.offline {{ background: {C['red']}; box-shadow: 0 0 8px {C['red']}66; }}
    /* Card title */
    .card-title {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {C['text_dim']};
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    /* Plotly overrides */
    .js-plotly-plot .plotly .main-svg {{ background: transparent !important; }}
    /* Images (trazas) */
    .stImage img {{
        border-radius: 12px;
        border: 1px solid {C['card_border']};
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }}
</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

# ─── Carga ─────────────────────────────────
@st.cache_resource
def load_config():
    return get_config(FIBERMIND_CONFIG)

config = load_config()

def get_isp_services(isp_id: str):
    repo = config.get_repo(isp_id)
    ns = config.get_network_service(isp_id)
    return repo, ns

# ─── Header ────────────────────────────────
def render_header(isp_name: str, is_online: bool):
    status_cls = "online" if is_online else "offline"
    now = datetime.now().strftime("%b %d, %Y · %H:%M")
    st.markdown(f"""
    <div class="app-header">
        <h1>
            <span style="color: {C['accent']};">◈</span>
            FiberMind
            <span style="font-weight:400; font-size:1.1rem; color:{C['text_dim']};">{isp_name}</span>
        </h1>
        <div class="header-right">
            <span class="status-dot {status_cls}"></span>
            <span>{'Online' if is_online else 'Offline'}</span>
            <span style="color:{C['divider']};">|</span>
            <span>🕐 {now}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Metric Cards ──────────────────────────
def render_metric_cards(total_events, total_hilos, total_criticos, total_cables):
    cols = st.columns(4)
    metrics = [
        ("📡 Eventos OTDR", total_events, C['blue']),
        ("🔌 Hilos Activos", total_hilos, C['accent']),
        ("⚠️ Alertas Críticas", total_criticos, C['red'] if total_criticos > 0 else C['accent']),
        ("📦 Cables", total_cables, C['purple']),
    ]
    for i, (label, value, color) in enumerate(metrics):
        with cols[i]:
            st.markdown(f"""
            <div style="background:{C['card']}; border:1px solid {C['card_border']};
                        border-radius:12px; padding:16px 20px; border-left:3px solid {color};">
                <div style="color:{C['text_dim']}; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:4px;">
                    {label}
                </div>
                <div style="color:{C['text']}; font-size:2rem; font-weight:700;">
                    {value}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─── Gráficos ──────────────────────────────
def render_event_pie_chart(tipos):
    """Gráfico de dona: distribución de tipos de evento."""
    df = pd.DataFrame(tipos)
    if df.empty:
        return

    colors = [C['blue'], C['accent'], C['amber'], C['red'], C['purple']]
    fig = go.Figure(data=[go.Pie(
        labels=df['tipo_evento'],
        values=df['count'],
        hole=0.55,
        marker=dict(colors=colors[:len(df)], line=dict(color=C['card'], width=3)),
        textinfo='label+percent',
        textfont=dict(color=C['text'], size=12),
        hoverlabel=dict(bgcolor=C['card'], font_color=C['text']),
    )])
    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def render_bar_chart(hilos_por_cable):
    """Gráfico de barras: hilos por cable."""
    df = pd.DataFrame(hilos_por_cable)
    if df.empty:
        return

    fig = go.Figure(data=[go.Bar(
        x=[f"Cable {r['id_cable']}" for r in hilos_por_cable],
        y=[r['hilos'] for r in hilos_por_cable],
        marker_color=C['blue'],
        marker_line=dict(color=C['accent'], width=1),
        hovertemplate='<b>%{x}</b><br>Hilos: %{y}<extra></extra>',
    )])
    fig.update_layout(
        margin=dict(l=20, r=20, t=10, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, color=C['text_dim']),
        yaxis=dict(showgrid=True, gridcolor=C['card_border'], color=C['text_dim']),
        height=280,
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# ─── Sidebar ───────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo / Brand
        st.markdown(f"""
        <div style="text-align:center; padding:20px 0 12px;">
            <div style="font-size:2.8rem; line-height:1;">◈</div>
            <div style="font-size:1.3rem; font-weight:700; color:{C['text']};">FiberMind</div>
            <div style="font-size:0.75rem; color:{C['text_dim']};">Network Intelligence</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<hr style='border-color:{C['card_border']}; margin:12px 0;'>", unsafe_allow_html=True)

        # ISP Selector
        available = config.get_available_isps()
        if available:
            isp_opts = {i: f"{config.get_isp(i).name}" for i in available}
            default_idx = list(available).index(config.default_isp) if config.default_isp in available else 0
            sel = st.selectbox("ISP / Cliente", options=list(isp_opts.keys()),
                               format_func=lambda x: isp_opts[x], index=default_idx,
                               key="sidebar_isp")
        else:
            sel = "default"
            st.warning("Sin ISPs configurados")

        # ISP info
        isp = config.get_isp(sel)
        db_exists = Path(isp.db_path).exists() if isp.db_path else False
        st.markdown(f"""
        <div style="background:{C['bg']}; border:1px solid {C['card_border']}; border-radius:10px; padding:12px; margin:8px 0;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
                <span class="status-dot {'online' if db_exists else 'offline'}"></span>
                <span style="font-size:0.85rem; font-weight:500;">{isp.name}</span>
            </div>
            <div style="font-size:0.75rem; color:{C['text_dim']}; line-height:1.8;">
                {'🏙️ ' + isp.city if isp.city else ''}<br>
                🤖 {isp.ollama_model}<br>
                📁 {isp.db_path.split('/')[-1] if isp.db_path else '—'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<hr style='border-color:{C['card_border']}; margin:16px 0;'>", unsafe_allow_html=True)

        # Navigation
        nav = st.radio("", ["📊 Panel Principal", "🔍 Consulta de Hilos", "⚠️ Auditoría", "📍 Infraestructura", "ℹ️ Acerca de"],
                       label_visibility="collapsed")

        st.markdown(f"<hr style='border-color:{C['card_border']}; margin:16px 0;'>", unsafe_allow_html=True)

        # System status footer
        st.markdown(f"""
        <div style="font-size:0.7rem; color:{C['text_dim']}; text-align:center; padding:8px 0;">
            FiberMind v0.3.0<br>
            {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>
        """, unsafe_allow_html=True)

        return sel, nav

# ─── Pages ─────────────────────────────────

def page_panel(repo, ns, isp):
    st.markdown(f"<div class='card-title'>📊 Resumen de Red</div>", unsafe_allow_html=True)

    # Cargar stats
    try:
        r, _ = repo.execute_custom_query("SELECT COUNT(*) as t FROM eventos_otdr")
        total_events = r[0]['t']
    except: total_events = 0
    try:
        r, _ = repo.execute_custom_query("SELECT COUNT(DISTINCT id_hilo) as t FROM eventos_otdr")
        total_hilos = r[0]['t']
    except: total_hilos = 0
    try:
        r, _ = repo.execute_custom_query("SELECT COUNT(*) as t FROM eventos_otdr WHERE atenuacion_db > 0.5")
        total_criticos = r[0]['t']
    except: total_criticos = 0
    try:
        r, _ = repo.execute_custom_query("SELECT COUNT(DISTINCT id_cable) as t FROM eventos_otdr")
        total_cables = r[0]['t']
    except: total_cables = 0

    render_metric_cards(total_events, total_hilos, total_criticos, total_cables)

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='card-title' style='margin-top:16px;'>📈 Distribución por Tipo</div>", unsafe_allow_html=True)
        tipos, _ = repo.execute_custom_query(
            "SELECT tipo_evento, COUNT(*) as count FROM eventos_otdr GROUP BY tipo_evento ORDER BY count DESC")
        render_event_pie_chart(tipos)
    with col2:
        st.markdown(f"<div class='card-title' style='margin-top:16px;'>📊 Hilos por Cable</div>", unsafe_allow_html=True)
        hilos, _ = repo.execute_custom_query(
            "SELECT id_cable, COUNT(DISTINCT id_hilo) as hilos FROM eventos_otdr GROUP BY id_cable")
        render_bar_chart(hilos)

    # Tabla de últimos eventos
    st.markdown(f"<div class='card-title' style='margin-top:8px;'>🕐 Últimos Eventos</div>", unsafe_allow_html=True)
    try:
        eventos, _ = repo.execute_custom_query(
            "SELECT distancia_km, tipo_evento, atenuacion_db, id_cable, id_hilo "
            "FROM eventos_otdr ORDER BY distancia_km LIMIT 10")
        if eventos:
            df = pd.DataFrame(eventos)
            # Color rows by criticidad
            def color_row(row):
                if row.get('atenuacion_db', 0) > 0.5:
                    return [f'color: {C["red"]}; font-weight:600'] * len(row)
                return ['' for _ in row.index]
            styled = df.style.apply(color_row, axis=1).format({
                'distancia_km': '{:.2f} km',
                'atenuacion_db': '{:.2f} dB',
            })
            st.dataframe(styled, use_container_width=True, hide_index=True)
    except Exception as e:
        st.caption(f"Sin datos: {e}")

    # Trazas rápidas
    st.markdown(f"<div class='card-title' style='margin-top:16px;'>📡 Visualización de Trazas</div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1,1,2])
    with col_a:
        cable_id = st.number_input("Cable", min_value=1, value=8, key="panel_cable")
    with col_b:
        hilo_id = st.number_input("Hilo", min_value=1, value=285, key="panel_hilo")
    with col_c:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔎 Ver Traza", use_container_width=True):
            img = generate_plot(cable_id, hilo_id, "/tmp/fibermind_panel.png", repo)
            if img:
                st.image(img, caption=f"Traza OTDR — Cable {cable_id}, Hilo {hilo_id}", use_column_width=True)
            else:
                st.warning("Sin datos para esa combinación")

def page_query(repo, ns, isp):
    st.markdown(f"<div class='card-title'>🔍 Consulta de Hilos</div>", unsafe_allow_html=True)
    st.markdown("Consulta eventos OTDR por cable e hilo. Los datos críticos (>0.5dB) se marcan en **rojo**.")

    col1, col2 = st.columns(2)
    with col1:
        id_cable = st.number_input("ID Cable", min_value=1, value=8, key="q_cable")
    with col2:
        id_hilo = st.number_input("ID Hilo", min_value=1, value=285, key="q_hilo")

    if st.button("🔎 Consultar", type="primary", use_container_width=True):
        try:
            eventos = repo.get_hilo_events(id_cable, id_hilo)
            if not eventos:
                st.warning(f"No hay datos para Cable {id_cable}, Hilo {id_hilo}")
            else:
                data = [{"Distancia (km)": e.distancia_km, "Tipo Evento": e.tipo_evento,
                         "Atenuación (dB)": e.atenuacion_db}
                        for e in eventos]
                df = pd.DataFrame(data)
                # Resaltar criticos
                def highlight_crit(row):
                    if row['Atenuación (dB)'] > 0.5:
                        return [f'color: {C["red"]}'] * len(row)
                    return ['']
                st.success(f"✅ {len(eventos)} eventos")
                st.dataframe(df.style.apply(highlight_crit, axis=1).format({
                    'Distancia (km)': '{:.2f} km',
                    'Atenuación (dB)': '{:.2f} dB',
                }), use_container_width=True, hide_index=True)

                img = generate_plot(id_cable, id_hilo, "/tmp/fibermind_query.png", repo)
                if img:
                    st.image(img, caption=f"Traza OTDR — Cable {id_cable}, Hilo {id_hilo}", use_column_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

def page_audit(repo, ns, isp):
    st.markdown(f"<div class='card-title'>⚠️ Auditoría de Red</div>", unsafe_allow_html=True)
    st.markdown("Detecta empalmes y curvaturas que exceden el umbral de pérdida permitido.")

    col1, col2 = st.columns(2)
    with col1:
        limite = st.slider("Umbral crítico (dB)", 0.1, 3.0, 0.5, 0.1, key="aud_lim")
    with col2:
        cable = st.number_input("Filtrar por Cable", min_value=0, value=8, key="aud_cable")

    if st.button("🔎 Ejecutar Auditoría", type="primary", use_container_width=True):
        cable_param = cable if cable > 0 else None
        res = ns.audit_critical_splices(limite, cable_param)
        if "limpia" in res.lower():
            st.success(res)
        else:
            st.warning(res)

    # Quick health summary
    try:
        r, _ = repo.execute_custom_query("SELECT COUNT(*) as t FROM eventos_otdr WHERE atenuacion_db > 0.5")
        criticos = r[0]['t']
        r, _ = repo.execute_custom_query("SELECT COUNT(*) as t FROM eventos_otdr")
        total = r[0]['t']
        pct = round(criticos / total * 100, 1) if total > 0 else 0
        health = "✅ Saludable" if pct < 20 else "⚠️ Atención" if pct < 50 else "🔴 Crítico"
        health_color = C['accent'] if pct < 20 else C['amber'] if pct < 50 else C['red']

        st.markdown(f"""
        <div style="background:{C['card']}; border:1px solid {C['card_border']}; border-radius:12px; padding:20px; margin-top:16px;">
            <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; color:{C['text_dim']}; margin-bottom:8px;">
                Salud de la Red
            </div>
            <div style="display:flex; align-items:center; gap:16px;">
                <span style="font-size:1.5rem; font-weight:700; color:{health_color};">{health}</span>
                <span style="font-size:0.85rem; color:{C['text_dim']};">{criticos} de {total} eventos críticos ({pct}%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except:
        pass

def page_infra(repo, ns, isp):
    st.markdown(f"<div class='card-title'>📍 Infraestructura Geográfica</div>", unsafe_allow_html=True)

    try:
        r, _ = repo.execute_custom_query(
            "SELECT nombre_elemento, plano, x, y FROM inventario_geografico ORDER BY nombre_elemento")
        if r:
            df = pd.DataFrame(r)
            st.dataframe(df, use_container_width=True, hide_index=True)

            search = st.text_input("🔍 Buscar elemento en planos", placeholder="Ej: EMPALME 3")
            if search:
                res = ns.locate_element(search)
                st.info(res)
        else:
            st.info("No hay elementos registrados en inventario.")
    except Exception as e:
        st.error(f"Error: {e}")

def page_about(isp):
    st.markdown(f"<div class='card-title'>ℹ️ Acerca de FiberMind</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown(f"""
        **FiberMind Analytics** v0.3.0

        Plataforma de inteligencia artificial para inspección y mantenimiento
        de infraestructura FTTH. Decodifica trazas OTDR, detecta fallas críticas
        y proporciona visibilidad en tiempo real de la red de fibra óptica.

        **Capacidades:**
        - 📡 Decodificación y visualización de trazas OTDR
        - ⚠️ Detección automática de fallas (empalmes, curvaturas, conectores)
        - 🔍 Consultas en lenguaje natural vía IA local (Ollama)
        - 🗺️ Localización geográfica de infraestructura en planos
        - 🔌 API REST multi-ISP para integración con NOCs
        - 🤖 Bot de Telegram para técnicos en campo
        """)
    with col2:
        st.markdown(f"""
        <div style="background:{C['card']}; border:1px solid {C['card_border']}; border-radius:12px; padding:16px;">
            <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; color:{C['text_dim']}; margin-bottom:8px;">
                ISP Activo
            </div>
            <div style="font-size:1.1rem; font-weight:600;">{isp.name}</div>
            <div style="font-size:0.85rem; color:{C['text_dim']};">{'🏙️ ' + isp.city if isp.city else ''}</div>
            <div style="font-size:0.8rem; color:{C['text_dim']};">🤖 {isp.ollama_model}</div>
            <div style="font-size:0.7rem; color:{C['text_dim']}; margin-top:8px;">📁 {isp.db_path}</div>
        </div>
        """, unsafe_allow_html=True)

        isps = config.list_isps()
        if isps:
            st.markdown(f"<div class='card-title' style='margin-top:16px;'>🌐 ISPs Activos</div>", unsafe_allow_html=True)
            for i in isps:
                icon = "✅" if i["db_exists"] else "❌"
                ci = config.get_isp(i["id"]).city
                st.markdown(f"{icon} **{i['name']}** — {ci or '—'}")

# ─── Main ──────────────────────────────────
def main():
    inject_css()
    selected_isp, nav = render_sidebar()
    repo, ns = get_isp_services(selected_isp)
    isp = config.get_isp(selected_isp)

    # Check online status
    is_online = False
    try:
        r, _ = repo.execute_custom_query("SELECT 1")
        is_online = True
    except:
        pass

    render_header(isp.name, is_online)

    if not is_online:
        st.warning(f"⚠️ Base de datos no disponible para **{isp.name}**. Verifica la ruta: `{isp.db_path}`")
        return

    pages = {
        "📊 Panel Principal": page_panel,
        "🔍 Consulta de Hilos": page_query,
        "⚠️ Auditoría": page_audit,
        "📍 Infraestructura": page_infra,
        "ℹ️ Acerca de": page_about,
    }

    page_fn = pages.get(nav, page_panel)
    page_fn(repo, ns, isp)

if __name__ == "__main__":
    main()
