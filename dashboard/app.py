"""
GoGolf – Dashboard Empresarial BSC
===================================
Ejecutar con:  streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Configuracion de pagina ────────────────────────────────────────────────
st.set_page_config(
    page_title="GoGolf – Dashboard BSC",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Ruta de datos ──────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "raw")
PROC = os.path.join(BASE, "data", "processed")

# ── Paleta corporativa GoGolf ──────────────────────────────────────────────
# Verde primario GoGolf (extraído del logo/sitio)
VERDE_P    = "#1a8a3c"   # verde botón gogolf
VERDE_OSC  = "#0f5c28"   # hover / sidebar
VERDE_LITE = "#e8f5ed"   # fondo suave verde
BLANCO     = "#ffffff"
GRIS_BG    = "#f5f7f5"   # fondo general
GRIS_TEXT  = "#3d4a3d"   # texto oscuro neutro
GRIS_MED   = "#7a8c7a"   # texto secundario
ROJO       = "#d93025"   # alerta / negativo
NARANJA    = "#f5820d"   # advertencia / medio
AMARILLO   = "#f9c923"   # neutral cálido
GRIS_DARK  = "#4a5568"   # gráficas neutras

# ── CSS ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ---- Fondo general ---- */
.stApp {{ background-color: {GRIS_BG}; }}

/* ---- Sidebar verde gogolf ---- */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {VERDE_OSC} 0%, {VERDE_P} 100%);
}}
[data-testid="stSidebar"] * {{ color: white !important; }}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {{
    background-color: rgba(255,255,255,0.25) !important;
}}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="select"] > div {{
    background-color: rgba(255,255,255,0.15) !important;
    border-color: rgba(255,255,255,0.4) !important;
}}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.3); }}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background-color: {VERDE_LITE};
    border-radius: 10px;
    padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 8px;
    color: {VERDE_OSC};
    font-weight: 600;
    padding: 6px 16px;
}}
.stTabs [aria-selected="true"] {{
    background-color: {VERDE_P} !important;
    color: white !important;
}}

/* ---- Metric cards ---- */
.kcard {{
    background: {BLANCO};
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    border-left: 5px solid {VERDE_P};
    margin-bottom: 10px;
}}
.kcard.alerta   {{ border-left-color: {ROJO}; }}
.kcard.aviso    {{ border-left-color: {NARANJA}; }}
.kcard.info     {{ border-left-color: {GRIS_DARK}; }}
.kval  {{ font-size: 2rem; font-weight: 800; color: {GRIS_TEXT}; line-height:1.1; }}
.klbl  {{ font-size: 0.80rem; color: {GRIS_MED}; margin-top: 3px; text-transform: uppercase; letter-spacing:.4px; }}
.kdelta {{ font-size: 0.78rem; margin-top: 5px; font-weight: 600; }}

/* ---- Section titles ---- */
.sec-title {{
    font-size: 1rem; font-weight: 700;
    color: {VERDE_OSC};
    border-left: 4px solid {VERDE_P};
    padding-left: 10px;
    margin: 22px 0 12px 0;
}}

/* ---- Header strip ---- */
.header-strip {{
    background: linear-gradient(90deg, {VERDE_OSC} 0%, {VERDE_P} 100%);
    border-radius: 12px;
    padding: 18px 28px;
    margin-bottom: 18px;
    color: white;
}}
.header-strip h1 {{ color: white; margin:0; font-size:1.6rem; }}
.header-strip p  {{ color: rgba(255,255,255,0.80); margin:4px 0 0 0; font-size:.88rem; }}
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ─────────────────────────────────────────────────────────
@st.cache_data
def load_all():
    bsc     = pd.read_csv(os.path.join(PROC, "kpi_bsc_mensual.csv"))
    res     = pd.read_csv(os.path.join(DATA, "fact_reservas.csv"))
    cancel  = pd.read_csv(os.path.join(DATA, "fact_cancelaciones.csv"))
    noshow  = pd.read_csv(os.path.join(DATA, "fact_noshow.csv"))
    ratings = pd.read_csv(os.path.join(DATA, "fact_ratings.csv"))
    fricc   = pd.read_csv(os.path.join(DATA, "fact_fricciones.csv"))
    clubs   = pd.read_csv(os.path.join(DATA, "dim_club.csv"))
    jugs    = pd.read_csv(os.path.join(DATA, "dim_jugador.csv"))
    inv     = pd.read_csv(os.path.join(DATA, "inventario_clubes.csv"))

    MESES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
             7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}
    bsc["periodo"] = pd.to_datetime(
        bsc["anio"].astype(str) + "-" + bsc["mes"].astype(str).str.zfill(2)
    )
    # Etiqueta en español para eje X categórico (evita locale inglés de Plotly)
    bsc["periodo_lbl"] = bsc.apply(
        lambda r: f"{MESES[int(r['mes'])]} {int(r['anio'])}", axis=1
    )
    res["fecha_dt"]  = pd.to_datetime(res["id_fecha"], format="%Y%m%d")
    res["anio"]      = res["fecha_dt"].dt.year
    res["mes"]       = res["fecha_dt"].dt.month
    res["periodo"]   = res["fecha_dt"].dt.to_period("M").dt.to_timestamp()
    res["periodo_lbl"] = res.apply(
        lambda r: f"{MESES[int(r['mes'])]} {int(r['anio'])}", axis=1
    )

    fricc = fricc.merge(clubs[["id_club","nombre_club"]], on="id_club", how="left")
    noshow= noshow.merge(clubs[["id_club","nombre_club"]], on="id_club", how="left")
    res   = res.merge(clubs[["id_club","nombre_club"]], on="id_club", how="left")

    return bsc, res, cancel, noshow, ratings, fricc, clubs, jugs, inv

bsc, res, cancel, noshow, ratings, fricc, clubs, jugs, inv = load_all()

MESES_ES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
            7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

# ── layout helpers ────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    plot_bgcolor=BLANCO, paper_bgcolor=BLANCO,
    font=dict(family="Inter, sans-serif", color=GRIS_TEXT),
    legend=dict(font=dict(color=GRIS_TEXT), bgcolor="rgba(255,255,255,0.85)",
                bordercolor="#e0e0e0", borderwidth=1),
    margin=dict(t=20, b=30, l=10, r=10),
)

_FONT_AXIS = dict(color=GRIS_TEXT, size=11)
_XAXIS_DEF = dict(showgrid=False, zeroline=False,
                  tickfont=_FONT_AXIS, title_font=_FONT_AXIS)
_YAXIS_DEF = dict(showgrid=True, gridcolor="#e8ede8", zeroline=False,
                  tickfont=_FONT_AXIS, title_font=_FONT_AXIS)

def apply_layout(fig, height=300, **kw):
    # Merge xaxis / yaxis defaults con lo que pase el caller
    xaxis = {**_XAXIS_DEF, **(kw.pop("xaxis", {}) or {})}
    yaxis = {**_YAXIS_DEF, **(kw.pop("yaxis", {}) or {})}
    fig.update_layout(height=height, xaxis=xaxis, yaxis=yaxis, **PLOT_LAYOUT, **kw)

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR – Filtros
# ═══════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.image("https://gogolf.mx/build/images/logo-light.svg", width=200)
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("#### Filtros")

    anios = sorted(bsc["anio"].unique())
    anio_sel = st.multiselect("Año", anios, default=anios)

    meses_disp = sorted(bsc["mes"].unique())
    mes_sel = st.multiselect(
        "Mes", meses_disp,
        default=meses_disp,
        format_func=lambda m: MESES_ES[m]
    )

    nse_opts = sorted(res["nse_jugador"].dropna().unique())
    nse_sel  = st.multiselect("NSE del Jugador", nse_opts, default=nse_opts)

    club_opts = sorted(clubs["nombre_club"].tolist())
    club_sel  = st.multiselect("Club", club_opts, default=club_opts)

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.caption("GoGolf · Dashboard BSC v3\nDatos sintéticos 2023-2024")

# ── Aplicar filtros ────────────────────────────────────────────────────────
bsc_f = bsc[bsc["anio"].isin(anio_sel) & bsc["mes"].isin(mes_sel)]
res_f = res[
    res["anio"].isin(anio_sel) &
    res["mes"].isin(mes_sel) &
    res["nse_jugador"].isin(nse_sel) &
    res["nombre_club"].isin(club_sel)
]
noshow_f = noshow[noshow["nombre_club"].isin(club_sel)]

# ═══════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════
st.markdown(
    "<div class='header-strip'>"
    "<h1>⛳ GoGolf — Dashboard Estratégico BSC</h1>"
    "<p>Período 2023-2024 &nbsp;·&nbsp; Datos sintéticos de alta fidelidad &nbsp;·&nbsp; 14 clubes reales</p>"
    "</div>",
    unsafe_allow_html=True
)

# ── helpers de KPI card ────────────────────────────────────────────────────
def kpi_card(col, label, value, color="verde"):
    css_mod = "alerta" if color=="rojo" else "aviso" if color=="naranja" else "info" if color=="info" else ""
    col.markdown(
        f"<div class='kcard {css_mod}'>"
        f"<div class='kval'>{value}</div>"
        f"<div class='klbl'>{label}</div>"
        f"</div>",
        unsafe_allow_html=True
    )

def sec(title):
    st.markdown(f"<div class='sec-title'>{title}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════
tab_resumen, tab_fin, tab_cliente, tab_procesos, tab_friccion, tab_clubes = st.tabs([
    "📊 Resumen Ejecutivo",
    "💰 Financiera",
    "👤 Cliente",
    "⚙️ Procesos",
    "⚠️ Fricción Social",
    "🏌️ Clubes",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 – RESUMEN EJECUTIVO
# ═══════════════════════════════════════════════════════════════════════════
with tab_resumen:

    sec("KPIs Globales del Período")
    c1,c2,c3,c4,c5,c6 = st.columns(6)

    total_res      = len(res_f)
    tasa_can_glob  = res_f[res_f.estatus_reserva=="cancelada"].shape[0] / max(total_res,1) * 100
    tasa_ns_glob   = res_f[res_f.estatus_reserva=="no_show"].shape[0]   / max(total_res,1) * 100
    ing_total      = res_f["ingreso_total_mxn"].sum()
    com_total      = res_f["comision_gogolf_mxn"].sum()
    nps_val        = bsc_f["nps_proxy"].mean()

    kpi_card(c1, "Total Reservas",    f"{total_res:,}")
    kpi_card(c2, "Ingreso Total",     f"${ing_total/1e6:.1f}M")
    kpi_card(c3, "Comisión GoGolf",   f"${com_total/1e6:.1f}M")
    kpi_card(c4, "Tasa Cancelación",  f"{tasa_can_glob:.1f}%",  color="naranja")
    kpi_card(c5, "Tasa No-Show",      f"{tasa_ns_glob:.1f}%",   color="rojo")
    kpi_card(c6, "NPS Proxy",         f"{nps_val:.1f}",
             color="rojo" if nps_val < 0 else "verde")

    st.markdown("<br/>", unsafe_allow_html=True)
    col_left, col_right = st.columns([2,1])

    with col_left:
        sec("Reservas Mensuales y Tendencia")
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=bsc_f["periodo_lbl"], y=bsc_f["total_reservas"],
            marker_color=VERDE_P, opacity=0.85, name="Reservas",
        ))
        x_num = np.arange(len(bsc_f))
        if len(x_num) > 1:
            z = np.polyfit(x_num, bsc_f["total_reservas"], 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=bsc_f["periodo_lbl"], y=p(x_num),
                line=dict(color=NARANJA, dash="dash", width=2.5),
                name="Tendencia"
            ))
        apply_layout(fig, height=300,
                     legend=dict(orientation="h", y=1.1),
                     yaxis_title="Reservas")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        sec("Estatus de Reservas")
        est_cnt = res_f.groupby("estatus_reserva").size().reset_index(name="n")
        color_map = {
            "confirmada": VERDE_P,
            "completada": VERDE_OSC,
            "cancelada":  NARANJA,
            "no_show":    ROJO,
        }
        fig2 = px.bar(
            est_cnt.sort_values("n"), x="n", y="estatus_reserva",
            orientation="h",
            color="estatus_reserva",
            color_discrete_map=color_map,
            text="n",
        )
        fig2.update_layout(
            height=300, showlegend=False,
            **{k:v for k,v in PLOT_LAYOUT.items()},
            xaxis_title="Reservas", yaxis_title="",
        )
        fig2.update_traces(texttemplate="%{text:,}", textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    sec("Tablero BSC — Las 4 Perspectivas")
    fig4 = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "💰 Financiera: Comisión vs Costo Variable (MXN)",
            "👤 Cliente: NPS Proxy",
            "⚙️ Procesos: No-Show e Incumplimiento",
            "🌱 Aprendizaje: Fricción Social por NSE",
        ],
        vertical_spacing=0.18, horizontal_spacing=0.10,
    )
    fig4.add_trace(go.Bar(x=bsc_f["periodo_lbl"],y=bsc_f["comision_total_gogolf_mxn"]/1e6,
                          name="Comisión",marker_color=VERDE_P,opacity=0.85), row=1,col=1)
    fig4.add_trace(go.Bar(x=bsc_f["periodo_lbl"],y=-bsc_f["costo_variable_total_mxn"]/1e6,
                          name="Costo Var.",marker_color=ROJO,opacity=0.75), row=1,col=1)

    nps_colors = [VERDE_P if v>=0 else ROJO for v in bsc_f["nps_proxy"]]
    fig4.add_trace(go.Bar(x=bsc_f["periodo_lbl"],y=bsc_f["nps_proxy"],
                          name="NPS",marker_color=nps_colors,showlegend=False), row=1,col=2)
    fig4.add_hline(y=0, line_dash="dot", line_color=GRIS_DARK, row=1, col=2)

    fig4.add_trace(go.Scatter(x=bsc_f["periodo_lbl"],y=bsc_f["tasa_noshow_pct"],
                              name="No-show %",line=dict(color=ROJO,width=2),
                              mode="lines+markers"), row=2,col=1)
    fig4.add_trace(go.Scatter(x=bsc_f["periodo_lbl"],
                              y=100-bsc_f["pct_cumplimiento_horario"],
                              name="Incumplimiento %",line=dict(color=NARANJA,width=2),
                              mode="lines+markers"), row=2,col=1)

    nse_data = res_f.groupby("nse_jugador").apply(
        lambda d: d["hay_friccion_social"].eq("SI").mean()*100
    ).reset_index(name="pct_friccion")
    nse_order = {"AB":0,"Cmas":1,"C":2,"Dmas":3}
    nse_data["orden"] = nse_data["nse_jugador"].map(nse_order)
    nse_data = nse_data.sort_values("orden")
    nse_labels = {"AB":"A/B","Cmas":"C+","C":"C","Dmas":"D+"}
    nse_data["label"] = nse_data["nse_jugador"].map(nse_labels)
    fig4.add_trace(go.Bar(
        x=nse_data["label"], y=nse_data["pct_friccion"],
        marker_color=[VERDE_P, "#5cb85c", NARANJA, ROJO],
        showlegend=False, name="Friccion %",
        text=nse_data["pct_friccion"].round(1).astype(str)+"%",
        textposition="outside",
    ), row=2,col=2)
    fig4.update_layout(
        height=560, showlegend=True,
        legend=dict(orientation="h", y=-0.05, font=dict(color=GRIS_TEXT)),
        plot_bgcolor=BLANCO, paper_bgcolor=BLANCO,
        font=dict(family="Inter, sans-serif", color=GRIS_TEXT),
        margin=dict(t=50,b=30,l=10,r=10),
        barmode="relative",
    )
    fig4.update_xaxes(tickfont=_FONT_AXIS, title_font=_FONT_AXIS)
    fig4.update_yaxes(tickfont=_FONT_AXIS, title_font=_FONT_AXIS)
    st.plotly_chart(fig4, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 – FINANCIERA
# ═══════════════════════════════════════════════════════════════════════════
with tab_fin:
    sec("Perspectiva Financiera")

    c1,c2,c3,c4 = st.columns(4)
    ing_prom = res_f["ingreso_total_mxn"].mean()
    margen   = res_f["margen_por_transaccion"].mean()*100
    util     = bsc_f["utilidad_neta_estimada_mxn"].sum()
    tasa_c   = res_f[res_f.estatus_reserva=="cancelada"].shape[0]/max(len(res_f),1)*100

    kpi_card(c1,"Ingreso prom / reserva", f"${ing_prom:,.0f}")
    kpi_card(c2,"Margen promedio",        f"{margen:.1f}%",    color="verde")
    kpi_card(c3,"Utilidad neta (período)",f"${util/1e6:.2f}M")
    kpi_card(c4,"Tasa cancelación",       f"{tasa_c:.1f}%",    color="naranja")

    c_left, c_right = st.columns(2)
    with c_left:
        sec("Ingreso Promedio por Reserva (Mensual)")
        fig = px.line(bsc_f, x="periodo_lbl", y="ingreso_promedio_por_reserva",
                      markers=True, color_discrete_sequence=[VERDE_P])
        fig.add_hline(y=bsc_f["ingreso_promedio_por_reserva"].mean(),
                      line_dash="dash", line_color=NARANJA,
                      annotation_text="Promedio", annotation_position="top left")
        apply_layout(fig, height=300,
                     yaxis=dict(tickprefix="$", tickformat=",", showgrid=True,
                                gridcolor="#e8ede8", zeroline=False,
                                title="Ingreso promedio por reserva (MXN)"))
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        sec("Margen por Transacción (Mensual)")
        fig = px.bar(bsc_f, x="periodo_lbl",
                     y=bsc_f["margen_promedio_por_transaccion"]*100,
                     color_discrete_sequence=[VERDE_P])
        fig.add_hline(y=bsc_f["margen_promedio_por_transaccion"].mean()*100,
                      line_dash="dash", line_color=ROJO,
                      annotation_text="Promedio")
        apply_layout(fig, height=300, yaxis_title="Margen (%)")
        st.plotly_chart(fig, use_container_width=True)

    sec("Green Fee por Club (Distribución)")
    club_gf = res_f.groupby("nombre_club")["green_fee_unitario_mxn"].median().reset_index()
    club_gf = club_gf.sort_values("green_fee_unitario_mxn")
    club_gf["nombre_corto"] = (club_gf["nombre_club"]
                               .str.replace("Club de Golf ","", regex=False)
                               .str.replace("Club ","", regex=False))
    fig = px.box(
        res_f.merge(club_gf[["nombre_club","nombre_corto"]], on="nombre_club")
             .sort_values("green_fee_unitario_mxn"),
        x="green_fee_unitario_mxn", y="nombre_corto",
        orientation="h",
        color_discrete_sequence=[VERDE_P],
    )
    apply_layout(fig, height=420,
                 xaxis=dict(tickprefix="$", tickformat=",", showgrid=False, zeroline=False),
                 yaxis_title="", xaxis_title="Green Fee (MXN)")
    st.plotly_chart(fig, use_container_width=True)

    sec("Cancelaciones: Motivo e Impacto")
    c_l, c_r = st.columns(2)
    with c_l:
        mc = cancel.groupby("motivo_cancelacion").size().reset_index(name="n").sort_values("n")
        fig = px.bar(mc, x="n", y="motivo_cancelacion", orientation="h",
                     color_discrete_sequence=[NARANJA], text="n")
        apply_layout(fig, height=300,
                     xaxis_title="Cancelaciones", yaxis_title="")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    with c_r:
        tc = cancel.groupby("tipo_cancelacion")["ingreso_cancelado_mxn"].sum().reset_index()
        fig = px.bar(tc, x="tipo_cancelacion", y="ingreso_cancelado_mxn",
                     color_discrete_sequence=[ROJO])
        apply_layout(fig, height=300,
                     yaxis=dict(tickprefix="$", tickformat=",", showgrid=True,
                                gridcolor="#e8ede8", zeroline=False,
                                title="Ingreso cancelado (MXN)"))
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 – CLIENTE
# ═══════════════════════════════════════════════════════════════════════════
with tab_cliente:
    sec("Perspectiva de Cliente")

    c1,c2,c3 = st.columns(3)
    nps_m    = bsc_f["nps_proxy"].mean()
    recompra = bsc_f["tasa_recompra_pct"].mean()
    rating   = bsc_f["rating_promedio_mes"].mean()

    kpi_card(c1,"NPS Proxy promedio", f"{nps_m:.1f}",
             color="rojo" if nps_m<0 else "verde")
    kpi_card(c2,"Tasa de recompra",   f"{recompra:.1f}%")
    kpi_card(c3,"Rating promedio",    f"{rating:.2f} / 5.0")

    c_left, c_right = st.columns(2)
    with c_left:
        sec("NPS Proxy Mensual")
        nps_colors = [VERDE_P if v>=0 else ROJO for v in bsc_f["nps_proxy"]]
        fig = go.Figure(go.Bar(x=bsc_f["periodo_lbl"], y=bsc_f["nps_proxy"],
                               marker_color=nps_colors))
        fig.add_hline(y=0,  line_dash="dot",  line_color=GRIS_DARK)
        fig.add_hline(y=10, line_dash="dash", line_color=VERDE_P,
                      annotation_text="Meta 12m: +10", annotation_position="top right")
        apply_layout(fig, height=300, yaxis_title="NPS")
        st.plotly_chart(fig, use_container_width=True)

    with c_right:
        sec("Tasa de Recompra Mensual")
        fig = px.line(bsc_f, x="periodo_lbl", y="tasa_recompra_pct",
                      markers=True, color_discrete_sequence=[VERDE_P])
        fig.add_hline(y=recompra+10, line_dash="dash", line_color=NARANJA,
                      annotation_text="Meta 12m")
        apply_layout(fig, height=300, yaxis_title="Recompra (%)")
        st.plotly_chart(fig, use_container_width=True)

    sec("Ratings por NSE y Aspecto")
    c_l, c_r = st.columns(2)
    with c_l:
        # fact_ratings ya contiene nse_jugador — no necesita merge con res
        nse_mean = ratings.groupby("nse_jugador")["rating_promedio"].mean().reset_index()
        nse_order = {"AB":0,"Cmas":1,"C":2,"Dmas":3}
        nse_mean["orden"] = nse_mean["nse_jugador"].map(nse_order)
        nse_mean = nse_mean.sort_values("orden")
        nse_mean["label"] = nse_mean["nse_jugador"].map(
            {"AB":"A/B","Cmas":"C+","C":"C","Dmas":"D+"})
        fig = px.bar(nse_mean, x="label", y="rating_promedio",
                     color="label",
                     color_discrete_sequence=[VERDE_OSC, VERDE_P, NARANJA, ROJO],
                     text=nse_mean["rating_promedio"].round(2))
        fig.add_hline(y=4.0, line_dash="dash", line_color=GRIS_DARK,
                      annotation_text="Meta: 4.0")
        apply_layout(fig, height=320,
                     yaxis=dict(range=[0,5], title="Rating promedio",
                                showgrid=True, gridcolor="#e8ede8", zeroline=False),
                     showlegend=False,)
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with c_r:
        aspectos = ["experiencia_general","condicion_campo","servicio_club",
                    "facilidad_reserva","relacion_precio_valor"]
        asp_mean = ratings[aspectos].mean().reset_index()
        asp_mean.columns = ["aspecto","media"]
        asp_mean = asp_mean.sort_values("media")
        fig = px.bar(asp_mean, x="media", y="aspecto", orientation="h",
                     color_discrete_sequence=[VERDE_P],
                     text=asp_mean["media"].round(2))
        fig.add_vline(x=4.0, line_dash="dash", line_color=ROJO)
        apply_layout(fig, height=320,
                     xaxis=dict(range=[0,5], title="Rating promedio",
                                showgrid=False, zeroline=False),
                     yaxis_title="")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    sec("Usuarios Activos y Recompra")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=bsc_f["periodo_lbl"], y=bsc_f["total_usuarios_activos_mes"],
                   fill="tozeroy",
                   fillcolor=f"rgba(26,138,60,0.12)",
                   line=dict(color=VERDE_P,width=2.5), name="Usuarios activos"),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=bsc_f["periodo_lbl"], y=bsc_f["tasa_recompra_pct"],
                   line=dict(color=NARANJA,width=2,dash="dot"),
                   name="Recompra %", mode="lines+markers"),
        secondary_y=True
    )
    fig.update_layout(height=300, plot_bgcolor=BLANCO, paper_bgcolor=BLANCO,
                      font=dict(family="Inter, sans-serif", color=GRIS_TEXT),
                      margin=dict(t=10,b=10),
                      legend=dict(orientation="h", y=1.1,
                                  font=dict(color=GRIS_TEXT)))
    fig.update_yaxes(title_text="Usuarios activos", secondary_y=False,
                     showgrid=True, gridcolor="#e8ede8",
                     tickfont=_FONT_AXIS, title_font=_FONT_AXIS)
    fig.update_yaxes(title_text="Tasa de recompra (%)", secondary_y=True,
                     showgrid=False,
                     tickfont=_FONT_AXIS, title_font=_FONT_AXIS)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 – PROCESOS
# ═══════════════════════════════════════════════════════════════════════════
with tab_procesos:
    sec("Perspectiva de Procesos Internos")

    c1,c2,c3 = st.columns(3)
    cumpl  = bsc_f["pct_cumplimiento_horario"].mean()
    disc   = bsc_f["pct_discrepancia_inventario"].mean()
    ns_p   = bsc_f["tasa_noshow_pct"].mean()
    perdida= noshow_f["perdida_total_estimada_mxn"].sum()

    kpi_card(c1,"% Cumplimiento horario",   f"{cumpl:.1f}%",   color="verde")
    kpi_card(c2,"% Discrepancia inventario",f"{disc:.2f}%",    color="naranja")
    kpi_card(c3,"Tasa no-show",             f"{ns_p:.1f}%",    color="rojo")

    st.metric("Pérdida total estimada por no-shows",
              f"${perdida/1e6:.2f}M MXN",
              help="Green fee × jugadores × 0.90 + comisión GoGolf")

    c_l, c_r = st.columns(2)
    with c_l:
        sec("Tasa de No-Show Mensual")
        fig = px.line(bsc_f, x="periodo_lbl", y="tasa_noshow_pct",
                      markers=True, color_discrete_sequence=[ROJO])
        fig.add_hline(y=ns_p-3, line_dash="dash", line_color=VERDE_P,
                      annotation_text="Meta 6m")
        apply_layout(fig, height=300, yaxis_title="No-show (%)")
        st.plotly_chart(fig, use_container_width=True)

    with c_r:
        sec("% Discrepancia de Inventario")
        fig = px.bar(bsc_f, x="periodo_lbl", y="pct_discrepancia_inventario",
                     color_discrete_sequence=[NARANJA])
        fig.add_hline(y=disc*0.5, line_dash="dash", line_color=VERDE_P,
                      annotation_text="Meta 12m")
        apply_layout(fig, height=300, yaxis_title="Discrepancia (%)")
        st.plotly_chart(fig, use_container_width=True)

    sec("Causas de No-Show")
    c_l, c_r = st.columns(2)
    with c_l:
        causa_cnt = (noshow_f.groupby("causa_principal").size()
                     .reset_index(name="n").sort_values("n"))
        fig = px.bar(causa_cnt, x="n", y="causa_principal", orientation="h",
                     color_discrete_sequence=[ROJO], text="n")
        apply_layout(fig, height=280, xaxis_title="No-shows", yaxis_title="")
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    with c_r:
        ns_club = (noshow_f.groupby("nombre_club")["perdida_total_estimada_mxn"].sum()
                   .reset_index()
                   .sort_values("perdida_total_estimada_mxn", ascending=False)
                   .head(10))
        ns_club["nombre_corto"] = (ns_club["nombre_club"]
                                   .str.replace("Club de Golf ","", regex=False)
                                   .str.replace("Club ","", regex=False))
        fig = px.bar(ns_club, x="perdida_total_estimada_mxn", y="nombre_corto",
                     orientation="h", color_discrete_sequence=[ROJO],
                     text=ns_club["perdida_total_estimada_mxn"]
                          .apply(lambda v: f"${v/1e3:.0f}K"))
        apply_layout(fig, height=320,
                     xaxis_title="Pérdida estimada (MXN)", yaxis_title="")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 – FRICCION SOCIAL
# ═══════════════════════════════════════════════════════════════════════════
with tab_friccion:
    sec("Fricción Social: Brecha NSE vs Requisitos de Clubes")
    st.info(
        "**¿Qué es la fricción social en GoGolf?**  "
        "Ocurre cuando el perfil del jugador (NSE, handicap, equipo propio, "
        "conocimiento de dress code) no cumple los requisitos de acceso del club. "
        "GoGolf democratiza el acceso al golf, pero los clubes fueron diseñados "
        "para el segmento A/B. Esta brecha genera no-shows, cancelaciones y NPS negativo."
    )

    c1,c2,c3 = st.columns(3)
    pct_fric  = res_f["hay_friccion_social"].eq("SI").mean()*100
    fric_ns   = res_f[(res_f.hay_friccion_social=="SI") &
                      (res_f.estatus_reserva=="no_show")].shape[0]
    nse_bajo  = res_f[res_f.nse_jugador.isin(["C","Dmas"])].shape[0]/max(len(res_f),1)*100

    kpi_card(c1,"% Reservas con fricción", f"{pct_fric:.1f}%",  color="rojo")
    kpi_card(c2,"No-shows por fricción",   f"{fric_ns:,}",       color="rojo")
    kpi_card(c3,"% Reservas NSE C/D+",    f"{nse_bajo:.0f}%",   color="naranja")

    c_l, c_r = st.columns(2)
    with c_l:
        sec("Impacto del NSE: Cancelación, No-Show y Fricción")
        nse_agg = res_f.groupby("nse_jugador").agg(
            total=("id_reserva","count"),
            cancelada=("estatus_reserva", lambda x: (x=="cancelada").sum()),
            noshow=("estatus_reserva",    lambda x: (x=="no_show").sum()),
            friccion=("hay_friccion_social",lambda x: (x=="SI").sum()),
        ).reset_index()
        nse_agg["pct_can"]  = nse_agg["cancelada"]/nse_agg["total"]*100
        nse_agg["pct_ns"]   = nse_agg["noshow"]   /nse_agg["total"]*100
        nse_agg["pct_fric"] = nse_agg["friccion"]  /nse_agg["total"]*100
        nse_agg["label"]    = nse_agg["nse_jugador"].map(
            {"AB":"A/B","Cmas":"C+","C":"C","Dmas":"D+"})
        nse_agg["orden"]    = nse_agg["nse_jugador"].map({"AB":0,"Cmas":1,"C":2,"Dmas":3})
        nse_agg = nse_agg.sort_values("orden")

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Cancelación %", x=nse_agg["label"],
                             y=nse_agg["pct_can"],
                             marker_color=NARANJA,
                             text=nse_agg["pct_can"].round(1)))
        fig.add_trace(go.Bar(name="No-show %", x=nse_agg["label"],
                             y=nse_agg["pct_ns"],
                             marker_color=ROJO,
                             text=nse_agg["pct_ns"].round(1)))
        fig.add_trace(go.Bar(name="Fricción %", x=nse_agg["label"],
                             y=nse_agg["pct_fric"],
                             marker_color=VERDE_P,
                             text=nse_agg["pct_fric"].round(1)))
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        apply_layout(fig, height=350,
                     barmode="group", yaxis_title="%",
                     legend=dict(orientation="h",y=1.1))
        st.plotly_chart(fig, use_container_width=True)

    with c_r:
        sec("Tipos de Fricción Detectados")
        tipo_cnt = (fricc.groupby("tipo_friccion").size()
                    .reset_index(name="n")
                    .sort_values("n",ascending=False))
        fig = px.treemap(
            tipo_cnt, path=["tipo_friccion"], values="n",
            color="n",
            color_continuous_scale=[[0, VERDE_LITE], [0.5, VERDE_P], [1, VERDE_OSC]],
        )
        fig.update_traces(texttemplate="<b>%{label}</b><br>%{value:,}",
                          textfont_size=13)
        fig.update_layout(height=350, margin=dict(t=10,b=10,l=0,r=0),
                          coloraxis_showscale=False,
                          paper_bgcolor=BLANCO)
        st.plotly_chart(fig, use_container_width=True)

    sec("Fricción por Club y Tipo de Requisito")
    fric_club = (fricc.groupby(["nombre_club","tipo_friccion"])
                 .size().reset_index(name="n"))
    fric_club["nombre_corto"] = (fric_club["nombre_club"]
                                 .str.replace("Club de Golf ","", regex=False)
                                 .str.replace("Club ","", regex=False))
    # paleta de verdes y alertas — sin piezas de pizza
    palette = [VERDE_OSC, VERDE_P, "#5cb85c", NARANJA, ROJO, AMARILLO, GRIS_DARK]
    fig = px.bar(
        fric_club.sort_values("n", ascending=False).head(60),
        x="nombre_corto", y="n", color="tipo_friccion",
        barmode="stack",
        color_discrete_sequence=palette,
    )
    apply_layout(fig, height=380,
                 xaxis=dict(tickangle=-35, showgrid=False, zeroline=False),
                 yaxis_title="Eventos de fricción",
                 xaxis_title="",
                 legend=dict(orientation="h", y=1.05))
    st.plotly_chart(fig, use_container_width=True)

    sec("Fricción Social Mensual")
    fig = px.line(bsc_f, x="periodo_lbl", y="pct_friccion_social",
                  markers=True, color_discrete_sequence=[ROJO])
    fig.add_hline(y=bsc_f["pct_friccion_social"].mean()*0.85,
                  line_dash="dash", line_color=VERDE_P,
                  annotation_text="Meta 6m")
    fig.add_hline(y=bsc_f["pct_friccion_social"].mean()*0.50,
                  line_dash="dash", line_color=VERDE_OSC,
                  annotation_text="Meta 24m")
    apply_layout(fig, height=300, yaxis_title="% Reservas con fricción")
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 6 – CLUBES
# ═══════════════════════════════════════════════════════════════════════════
with tab_clubes:
    sec("Análisis por Club")

    club_agg = res_f.groupby("nombre_club").agg(
        reservas=("id_reserva","count"),
        ingreso=("ingreso_total_mxn","sum"),
        comision=("comision_gogolf_mxn","sum"),
        gf_med=("green_fee_unitario_mxn","median"),
        noshow_n=("estatus_reserva",lambda x:(x=="no_show").sum()),
        cancel_n=("estatus_reserva",lambda x:(x=="cancelada").sum()),
        fric_n=("hay_friccion_social",lambda x:(x=="SI").sum()),
    ).reset_index()
    club_agg["tasa_ns"]  = club_agg["noshow_n"]/club_agg["reservas"]*100
    club_agg["tasa_can"] = club_agg["cancel_n"]/club_agg["reservas"]*100
    club_agg["pct_fric"] = club_agg["fric_n"]  /club_agg["reservas"]*100
    club_agg = club_agg.merge(
        clubs[["nombre_club","tipo_club","num_hoyos","estado",
               "requisito_dress_code","nse_minimo_acceso"]],
        on="nombre_club", how="left"
    )

    tipo_colors = {
        "resort":       VERDE_OSC,
        "privado":      VERDE_P,
        "semi-privado": NARANJA,
        "publico":      AMARILLO,
        "historico":    GRIS_DARK,
    }

    c_l, c_r = st.columns(2)
    with c_l:
        sec("Reservas por Club")
        df_ord = club_agg.sort_values("reservas")
        fig = px.bar(df_ord, x="reservas", y="nombre_club", orientation="h",
                     color="tipo_club",
                     color_discrete_map=tipo_colors,
                     text="reservas")
        apply_layout(fig, height=420,
                     xaxis_title="Reservas", yaxis_title="",
                     legend=dict(title="Tipo"))
        fig.update_traces(texttemplate="%{text:,}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with c_r:
        sec("Ingresos vs Tasa No-Show por Club")
        fig = px.scatter(
            club_agg,
            x="ingreso", y="tasa_ns",
            size="reservas", color="tipo_club",
            hover_name="nombre_club",
            color_discrete_map=tipo_colors,
            size_max=50,
            text="nombre_club",
        )
        fig.update_traces(textposition="top center", textfont_size=7)
        apply_layout(fig, height=420,
                     xaxis=dict(tickprefix="$", tickformat=",",
                                showgrid=False, zeroline=False),
                     yaxis_title="Tasa no-show (%)",
                     xaxis_title="Ingreso total (MXN)")
        st.plotly_chart(fig, use_container_width=True)

    sec("Tabla de Resumen por Club")
    disp_cols = {
        "nombre_club":"Club","tipo_club":"Tipo","estado":"Estado",
        "num_hoyos":"Hoyos","gf_med":"GF Mediana (MXN)",
        "reservas":"Reservas","ingreso":"Ingreso (MXN)",
        "tasa_ns":"No-Show %","tasa_can":"Cancel. %","pct_fric":"Fricción %",
        "requisito_dress_code":"Dress Code","nse_minimo_acceso":"NSE Mín",
    }
    tbl = club_agg[list(disp_cols.keys())].rename(columns=disp_cols)
    tbl["Ingreso (MXN)"]    = tbl["Ingreso (MXN)"].apply(lambda v: f"${v:,.0f}")
    tbl["GF Mediana (MXN)"] = tbl["GF Mediana (MXN)"].apply(lambda v: f"${v:,.0f}")
    tbl["No-Show %"]        = tbl["No-Show %"].apply(lambda v: f"{v:.1f}%")
    tbl["Cancel. %"]        = tbl["Cancel. %"].apply(lambda v: f"{v:.1f}%")
    tbl["Fricción %"]       = tbl["Fricción %"].apply(lambda v: f"{v:.1f}%")
    st.dataframe(tbl.sort_values("Reservas", ascending=False),
                 use_container_width=True, height=380)

    sec("Mapa de Clubes GoGolf")
    map_df = clubs.merge(
        club_agg[["nombre_club","reservas","tasa_ns","pct_fric"]],
        on="nombre_club", how="left"
    )
    fig_map = px.scatter_mapbox(
        map_df, lat="latitud", lon="longitud",
        size="reservas", color="tasa_ns",
        hover_name="nombre_club",
        hover_data={"latitud":False,"longitud":False,
                    "tasa_ns":":.1f","reservas":":.0f"},
        color_continuous_scale=[[0, VERDE_P], [0.5, AMARILLO], [1, ROJO]],
        size_max=30,
        zoom=4.5, center={"lat":20.0,"lon":-99.0},
        mapbox_style="carto-positron",
        labels={"tasa_ns":"No-Show %","reservas":"Reservas"},
    )
    fig_map.update_layout(height=480, margin=dict(t=10,b=10,l=0,r=0),
                          paper_bgcolor=BLANCO)
    st.plotly_chart(fig_map, use_container_width=True)
