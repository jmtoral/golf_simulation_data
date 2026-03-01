"""
Plataforma de Reservas de Golf - Analisis Descriptivo + KPIs BSC v4
=====================================================================
Graficas: series de tiempo, histogramas, boxplots, barras, treemaps, heatmap.
Sin graficas de pastel.

KPIs BSC cubiertos:
  Financiera:  ingreso prom/reserva, margen por transaccion, tasa cancelacion
  Cliente:     NPS proxy, tasa recompra, rating promedio
  Procesos:    cumplimiento horario, discrepancia inventario, tasa no-show
  Aprendizaje: friccion social (indicador de brecha NSE)
"""

import os, csv, math, statistics
from collections import defaultdict

try:
    import pandas as pd
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    import matplotlib.patches as mpatches
    import numpy as np
    import squarify
    HAS_SQUARIFY = True
except ImportError:
    try:
        import pandas as pd
        import matplotlib; matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
        import matplotlib.patches as mpatches
        import numpy as np
        HAS_SQUARIFY = False
        print("AVISO: squarify no disponible, treemaps se reemplazaran con barras horizontales.")
        print("Instala con: pip install squarify\n")
    except ImportError:
        print("ERROR: pandas y matplotlib son necesarios.")
        print("pip install pandas matplotlib numpy squarify")
        exit(1)

BASE = os.path.dirname(os.path.dirname(__file__))   # raiz del repo
CSV  = os.path.join(BASE, "data", "raw")
PROC = os.path.join(BASE, "data", "processed")
FIGS = os.path.join(BASE, "output", "graficas")
os.makedirs(FIGS, exist_ok=True)

def load(fname):
    with open(os.path.join(CSV, fname), encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save_fig(name):
    path = os.path.join(FIGS, name)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  -> {name}")

# ── Paleta corporativa GoGolf ──────────────────────────────────────────────
# Verde primario, verdes secundarios, alertas naranja/rojo, neutros
C = [
    "#1a8a3c",   # 0 verde primario GoGolf
    "#0f5c28",   # 1 verde oscuro
    "#5cb85c",   # 2 verde medio
    "#f5820d",   # 3 naranja (advertencia)
    "#f9c923",   # 4 amarillo (neutral)
    "#2e75b6",   # 5 azul acento
    "#d93025",   # 6 rojo (alerta)
    "#7030a0",   # 7 morado
    "#00b0f0",   # 8 celeste
    "#4a5568",   # 9 gris oscuro
]

# Estilo global limpio y legible
plt.rcParams.update({
    "figure.facecolor":  "white",
    "axes.facecolor":    "white",
    "axes.edgecolor":    "#cccccc",
    "axes.grid":         True,
    "grid.color":        "#e8e8e8",
    "grid.linewidth":    0.7,
    "text.color":        "#2d2d2d",
    "axes.labelcolor":   "#2d2d2d",
    "xtick.color":       "#2d2d2d",
    "ytick.color":       "#2d2d2d",
    "font.family":       "DejaVu Sans",
    "font.size":         9,
    "axes.titlesize":    12,
    "axes.titleweight":  "bold",
    "axes.titlecolor":   "#0f5c28",
    "legend.framealpha": 0.9,
    "legend.fontsize":   8,
})

MESES_ABR = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
             7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

# ── Cargar ────────────────────────────────────────────────────────────────────
print("Cargando datos...")
reservas   = load("fact_reservas.csv")
cancelac   = load("fact_cancelaciones.csv")
noshow     = load("fact_noshow.csv")
fricciones = load("fact_fricciones.csv")
ratings    = load("fact_ratings.csv")
dim_club   = load("dim_club.csv")
dim_jug    = load("dim_jugador.csv")

# kpi_bsc_mensual está en processed
def load_proc(fname):
    with open(os.path.join(PROC, fname), encoding="utf-8") as f:
        return list(csv.DictReader(f))

bsc = load_proc("kpi_bsc_mensual.csv")
print(f"  {len(reservas):,} reservas | {len(fricciones):,} fricciones | {len(ratings):,} ratings")

club_nombre = {c["id_club"]: c["nombre_club"] for c in dim_club}

# ── Series de tiempo desde kpi_bsc ───────────────────────────────────────────
bsc_sorted = sorted(bsc, key=lambda r:(int(r["anio"]),int(r["mes"])))
periodos   = [(int(r["anio"]),int(r["mes"])) for r in bsc_sorted]
etiq       = [f"{MESES_ABR[m]}\n{y}" for y,m in periodos]
x          = np.arange(len(periodos))

def bsc_col(col): return [float(r[col]) for r in bsc_sorted]

tot_res    = bsc_col("total_reservas")
tasa_can   = bsc_col("tasa_cancelacion_pct")
tasa_ns    = bsc_col("tasa_noshow_pct")
ing_prom   = bsc_col("ingreso_promedio_por_reserva")
margen_prom= bsc_col("margen_promedio_por_transaccion")
nps        = bsc_col("nps_proxy")
recompra   = bsc_col("tasa_recompra_pct")
rating_mes = bsc_col("rating_promedio_mes")
cumpl_hor  = bsc_col("pct_cumplimiento_horario")
pct_disc   = bsc_col("pct_discrepancia_inventario")
pct_fric   = bsc_col("pct_friccion_social")
utilidad   = bsc_col("utilidad_neta_estimada_mxn")
usuarios   = bsc_col("total_usuarios_activos_mes")

def fmt_mxn(v, _=None):
    return f"${v:,.0f}"

def add_anio_divider(ax):
    """Linea punteada entre 2023 y 2024"""
    ax.axvline(11.5, color="#aaaaaa", linestyle=":", linewidth=1, alpha=0.7)
    ax.text(5.5,  ax.get_ylim()[1]*0.97, "2023", ha="center", fontsize=8, color="#888888")
    ax.text(17.5, ax.get_ylim()[1]*0.97, "2024", ha="center", fontsize=8, color="#888888")

# =============================================================================
# SECCION 1 — PERSPECTIVA FINANCIERA
# =============================================================================
print("\n[1/7] Perspectiva Financiera...")

# 1a. Comision, Costo Variable y Margen
fig, ax1 = plt.subplots(figsize=(15,5))
com_tot  = bsc_col("comision_total_gogolf_mxn")
cvar_tot = bsc_col("costo_variable_total_mxn")
com_arr  = np.array(com_tot)
cvar_arr = np.array(cvar_tot)
ax1.bar(x,  com_arr/1e6,  color=C[0], label="Comisión GoGolf (MXN M)", alpha=0.85)
ax1.bar(x, -cvar_arr/1e6, color=C[6], label="Costo variable (MXN M)",  alpha=0.75)
ax2 = ax1.twinx()
ax2.plot(x, [m*100 for m in margen_prom], color=C[3], marker="o",
         linewidth=2, markersize=4, label="Margen % (eje der.)")
ax1.axhline(0, color="#444444", linewidth=0.6)
ax1.set_xticks(x); ax1.set_xticklabels(etiq, fontsize=7)
ax1.set_ylabel("Millones MXN")
ax2.set_ylabel("Margen por transacción (%)")
ax1.set_title("Perspectiva Financiera: Comisión, Costo Variable y Margen")
l1,lb1 = ax1.get_legend_handles_labels()
l2,lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1+l2, lb1+lb2, loc="upper left")
ax2.tick_params(colors="#2d2d2d")
ax2.yaxis.label.set_color("#2d2d2d")
add_anio_divider(ax1)
save_fig("01a_financiero_comision_margen.png")

# 1b. Ingreso promedio por reserva + tasa cancelacion
fig, ax1 = plt.subplots(figsize=(15,5))
ax1.bar(x, ing_prom, color=C[1], alpha=0.82, label="Ingreso prom. por reserva (MXN)")
ax2 = ax1.twinx()
ax2.plot(x, tasa_can, color=C[3], marker="s", linewidth=2, markersize=4,
         label="Tasa de cancelación (%)")
ax2.axhline(statistics.mean(tasa_can), color=C[3], linestyle="--", alpha=0.45,
            label=f"Media: {statistics.mean(tasa_can):.1f}%")
ax1.set_xticks(x); ax1.set_xticklabels(etiq, fontsize=7)
ax1.set_ylabel("Ingreso promedio por reserva (MXN)")
ax2.set_ylabel("Tasa de cancelación (%)")
ax1.set_title("KPI Financiero: Ingreso Promedio por Reserva y Tasa de Cancelación")
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_mxn))
l1,lb1 = ax1.get_legend_handles_labels()
l2,lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1+l2, lb1+lb2, loc="upper left")
ax2.tick_params(colors="#2d2d2d")
ax2.yaxis.label.set_color("#2d2d2d")
add_anio_divider(ax1)
save_fig("01b_ingreso_prom_cancelacion.png")

# 1c. Distribucion de green fees por club (boxplot horizontal)
fig, ax = plt.subplots(figsize=(13,7))
club_gf = defaultdict(list)
for r in reservas:
    nombre = club_nombre.get(r["id_club"], r["id_club"])
    club_gf[nombre].append(float(r["green_fee_unitario_mxn"]))
nombres_ord = sorted(club_gf.keys(), key=lambda n: statistics.median(club_gf[n]))
data_bp = [club_gf[n] for n in nombres_ord]
bp = ax.boxplot(data_bp, vert=False, patch_artist=True, notch=False,
                flierprops=dict(marker=".", markersize=2, alpha=0.3),
                medianprops=dict(color="white", linewidth=2))
for i, patch in enumerate(bp["boxes"]):
    shade = C[i % 3]   # rota entre verde primario, verde oscuro, verde medio
    patch.set_facecolor(shade); patch.set_alpha(0.80)
ax.set_yticklabels([n.replace("Club de Golf ","").replace("Club ","")
                    for n in nombres_ord], fontsize=8)
ax.set_xlabel("Green Fee (MXN)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_mxn))
ax.set_title("Distribución de Green Fees por Club")
save_fig("01c_boxplot_greenfee_por_club.png")

# =============================================================================
# SECCION 2 — PERSPECTIVA CLIENTE
# =============================================================================
print("[2/7] Perspectiva Cliente...")

# 2a. NPS proxy + rating promedio mensual
fig, ax1 = plt.subplots(figsize=(15,5))
ax1.bar(x, nps, color=[C[0] if v>=0 else C[6] for v in nps],
        alpha=0.80, label="NPS proxy (eje izq.)")
ax1.axhline(0, color="#444444", linewidth=0.8)
ax2 = ax1.twinx()
ax2.plot(x, rating_mes, color=C[3], marker="D", linewidth=2,
         markersize=5, label="Rating promedio (eje der.)")
ax2.set_ylim(0, 5)
ax2.axhline(4.0, color=C[3], linestyle="--", alpha=0.4, label="Meta: 4.0")
ax1.set_xticks(x); ax1.set_xticklabels(etiq, fontsize=7)
ax1.set_ylabel("NPS (% promotores − % detractores)")
ax2.set_ylabel("Rating promedio (1–5)")
ax1.set_title("KPI Cliente: NPS Proxy y Rating Promedio Mensual")
l1,lb1 = ax1.get_legend_handles_labels()
l2,lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1+l2, lb1+lb2, loc="upper left")
ax2.tick_params(colors="#2d2d2d")
ax2.yaxis.label.set_color("#2d2d2d")
add_anio_divider(ax1)
save_fig("02a_nps_rating.png")

# 2b. Tasa de recompra + usuarios activos
fig, ax1 = plt.subplots(figsize=(15,5))
ax1.fill_between(x, usuarios, alpha=0.18, color=C[0])
ax1.plot(x, usuarios, color=C[0], linewidth=2, marker="o", markersize=3,
         label="Usuarios activos (eje izq.)")
ax2 = ax1.twinx()
ax2.plot(x, recompra, color=C[3], linewidth=2, marker="^", markersize=5,
         label="Tasa de recompra % (eje der.)")
ax2.axhline(statistics.mean(recompra), color=C[3], linestyle="--", alpha=0.4,
            label=f"Media: {statistics.mean(recompra):.1f}%")
ax1.set_xticks(x); ax1.set_xticklabels(etiq, fontsize=7)
ax1.set_ylabel("Usuarios activos en el mes")
ax2.set_ylabel("Tasa de recompra (%)")
ax1.set_title("KPI Cliente: Usuarios Activos y Tasa de Recompra")
l1,lb1 = ax1.get_legend_handles_labels()
l2,lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1+l2, lb1+lb2, loc="upper left")
ax2.tick_params(colors="#2d2d2d")
ax2.yaxis.label.set_color("#2d2d2d")
add_anio_divider(ax1)
save_fig("02b_recompra_usuarios.png")

# 2c. Rating por NSE
fig, axes = plt.subplots(1, 2, figsize=(14,6))

# Izq: histograma rating por NSE
nse_ratings = defaultdict(list)
res_dict = {r["id_reserva"]: r["nse_jugador"] for r in reservas}
for rt in ratings:
    nse = res_dict.get(rt["id_reserva"])
    if nse:
        nse_ratings[nse].append(float(rt["rating_promedio"]))
nse_orden  = ["AB","Cmas","C","Dmas"]
nse_labels = ["A/B","C+","C","D+"]
for i,(nse,lbl) in enumerate(zip(nse_orden,nse_labels)):
    if nse_ratings[nse]:
        axes[0].hist(nse_ratings[nse], bins=20, alpha=0.65, label=lbl, color=C[i])
axes[0].set_title("Distribución de Ratings por NSE")
axes[0].set_xlabel("Rating promedio")
axes[0].set_ylabel("Frecuencia")
axes[0].legend()

# Der: rating medio por NSE (barras)
medias_nse = [(lbl, statistics.mean(nse_ratings[nse]))
              for nse,lbl in zip(nse_orden,nse_labels) if nse_ratings[nse]]
bars = axes[1].barh([m[0] for m in medias_nse], [m[1] for m in medias_nse],
                    color=C[:len(medias_nse)], alpha=0.85)
axes[1].set_xlim(0,5)
axes[1].axvline(4.0, color=C[6], linestyle="--", alpha=0.6, label="Meta: 4.0")
axes[1].set_title("Rating Promedio por NSE del Jugador")
axes[1].set_xlabel("Rating promedio (1–5)")
for i,(lbl,val) in enumerate(medias_nse):
    axes[1].text(val+0.05, i, f"{val:.2f}", va="center", fontsize=10, color="#2d2d2d")
axes[1].legend()
save_fig("02c_rating_por_nse.png")

# =============================================================================
# SECCION 3 — PERSPECTIVA PROCESOS INTERNOS
# =============================================================================
print("[3/7] Perspectiva Procesos Internos...")

# 3a. No-show y cumplimiento de horario
fig, ax1 = plt.subplots(figsize=(15,5))
ax1.bar(x, tasa_ns, color=C[6], alpha=0.80, label="Tasa de no-show (%)")
ax2 = ax1.twinx()
ax2.plot(x, cumpl_hor, color=C[0], marker="o", linewidth=2,
         markersize=4, label="Cumplimiento de horario (%)")
ax2.axhline(95, color=C[2], linestyle="--", alpha=0.5, label="Meta: 95%")
ax2.set_ylim(80,100)
ax1.set_xticks(x); ax1.set_xticklabels(etiq, fontsize=7)
ax1.set_ylabel("Tasa de no-show (%)")
ax2.set_ylabel("% Cumplimiento de horario")
ax1.set_title("KPI Procesos: Tasa de No-Show y Cumplimiento de Horario")
l1,lb1 = ax1.get_legend_handles_labels()
l2,lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1+l2, lb1+lb2, loc="upper right")
ax2.tick_params(colors="#2d2d2d")
ax2.yaxis.label.set_color("#2d2d2d")
add_anio_divider(ax1)
save_fig("03a_noshow_cumplimiento.png")

# 3b. Discrepancia de inventario + friccion social
fig, ax1 = plt.subplots(figsize=(15,5))
ax1.bar(x, pct_disc, color=C[3], alpha=0.85, label="% Discrepancia de inventario")
ax2 = ax1.twinx()
ax2.plot(x, pct_fric, color=C[7], marker="s", linewidth=2,
         markersize=4, label="% Reservas con fricción social")
ax1.set_xticks(x); ax1.set_xticklabels(etiq, fontsize=7)
ax1.set_ylabel("% Discrepancia de inventario")
ax2.set_ylabel("% Fricción social")
ax1.set_title("KPI Procesos: Discrepancia de Inventario y Fricción Social")
l1,lb1 = ax1.get_legend_handles_labels()
l2,lb2 = ax2.get_legend_handles_labels()
ax1.legend(l1+l2, lb1+lb2, loc="upper right")
ax2.tick_params(colors="#2d2d2d")
ax2.yaxis.label.set_color("#2d2d2d")
add_anio_divider(ax1)
save_fig("03b_discrepancia_friccion.png")

# 3c. Causas de no-show + tipos de friccion
causas_ns = defaultdict(int)
for ns in noshow:
    causas_ns[ns["causa_principal"]] += 1
tipos_fric_cnt = defaultdict(int)
for f in fricciones:
    tipos_fric_cnt[f["tipo_friccion"]] += 1

fig, axes = plt.subplots(1, 2, figsize=(14,5))
causes_ord = sorted(causas_ns.items(), key=lambda kv:kv[1])
bars_h = axes[0].barh([k for k,_ in causes_ord], [v for _,v in causes_ord],
                      color=C[:len(causes_ord)], alpha=0.85)
axes[0].set_title("No-Shows por Causa Principal")
axes[0].set_xlabel("Número de eventos")
for i,(k,v) in enumerate(causes_ord):
    axes[0].text(v+10, i, f"{v:,}", va="center", fontsize=9, color="#2d2d2d")

fric_ord = sorted(tipos_fric_cnt.items(), key=lambda kv:kv[1], reverse=True)
if HAS_SQUARIFY:
    vals = [v for _,v in fric_ord]
    lbls = [f"{k}\n{v:,}" for k,v in fric_ord]
    # Paleta de verdes claros para que el texto negro sea legible
    tm_cols = ["#c7e8c7","#95d595","#5cb85c","#2e8b2e","#1a5c1a",
               "#a8d4a8","#6bbf6b","#3a9a3a","#e8f5e8","#b8e0b8"]
    squarify.plot(sizes=vals, label=lbls, color=tm_cols[:len(vals)],
                  alpha=0.92, ax=axes[1],
                  text_kwargs={"fontsize": 8, "color": "#1a1a1a", "wrap": True})
    axes[1].set_axis_off()
    axes[1].set_title("Tipos de Fricción Social (treemap)", pad=12)
else:
    axes[1].barh([k for k,_ in fric_ord], [v for _,v in fric_ord],
                 color=[C[i%len(C)] for i in range(len(fric_ord))], alpha=0.85)
    axes[1].set_title("Tipos de Fricción Social")
    axes[1].set_xlabel("Número de eventos")
save_fig("03c_noshow_causas_fricciones.png")

# =============================================================================
# SECCION 4 — FRICCION SOCIAL (perspectiva transversal)
# =============================================================================
print("[4/7] Friccion Social (BSC transversal)...")

# 4a. Tasa de no-show y cancelacion por NSE del jugador
nse_stat = defaultdict(lambda:{"res":0,"ns":0,"can":0,"fric":0})
for r in reservas:
    nse = r["nse_jugador"]; nse_stat[nse]["res"] += 1
    if r["estatus_reserva"]=="no_show":    nse_stat[nse]["ns"]  += 1
    if r["estatus_reserva"]=="cancelada":  nse_stat[nse]["can"] += 1
    if r["hay_friccion_social"]=="SI":     nse_stat[nse]["fric"]+= 1

nse_ord  = ["AB","Cmas","C","Dmas"]
nse_lbls = ["A/B","C+","C","D+"]
ns_pct   = [nse_stat[n]["ns"] /max(1,nse_stat[n]["res"])*100 for n in nse_ord]
can_pct  = [nse_stat[n]["can"]/max(1,nse_stat[n]["res"])*100 for n in nse_ord]
fric_pct = [nse_stat[n]["fric"]/max(1,nse_stat[n]["res"])*100 for n in nse_ord]

fig, ax = plt.subplots(figsize=(11,6))
w = 0.25; xi = np.arange(len(nse_ord))
b1 = ax.bar(xi-w, can_pct,  w, label="Tasa de cancelación (%)",   color=C[3], alpha=0.85)
b2 = ax.bar(xi,   ns_pct,   w, label="Tasa de no-show (%)",        color=C[6], alpha=0.85)
b3 = ax.bar(xi+w, fric_pct, w, label="% con fricción social",      color=C[0], alpha=0.85)
ax.set_xticks(xi); ax.set_xticklabels(nse_lbls, fontsize=11)
ax.set_xlabel("Nivel Socioeconómico del Jugador (NSE)")
ax.set_ylabel("Porcentaje (%)")
ax.set_title("Impacto del NSE: Cancelación, No-Show y Fricción Social")
ax.legend()
for bars in [b1,b2,b3]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, h+0.2, f"{h:.1f}%",
                ha="center", va="bottom", fontsize=8, color="#2d2d2d")
save_fig("04a_friccion_por_nse.png")

# 4b. Treemap de perdida por friccion por club
perdida_club = defaultdict(float)
for ns in noshow:
    if ns.get("friccion_social_como_factor","") == "SI":
        perdida_club[club_nombre.get(ns["id_club"],ns["id_club"])] += float(ns["perdida_total_estimada_mxn"])

if perdida_club:
    items = sorted(perdida_club.items(), key=lambda kv:kv[1], reverse=True)
    if HAS_SQUARIFY:
        fig, ax = plt.subplots(figsize=(13,7))
        vals = [v for _,v in items]
        lbls = [f"{k.replace('Club de Golf ','').replace('Club ','')}\n${v/1e3:.0f}K"
                for k,v in items]
        tm_cols = ["#c7e8c7","#95d595","#5cb85c","#2e8b2e","#1a5c1a",
                   "#a8d4a8","#6bbf6b","#3a9a3a","#e8f5e8","#b8e0b8",
                   "#d4eed4","#7acc7a","#4aac4a","#88cc88","#22aa22"]
        squarify.plot(sizes=vals, label=lbls, color=tm_cols[:len(vals)],
                      alpha=0.92, ax=ax,
                      text_kwargs={"fontsize": 8, "color": "#1a1a1a"})
        ax.set_axis_off()
        ax.set_title("Pérdida Estimada por No-Show (Fricción Social) por Club")
        save_fig("04b_treemap_perdida_friccion_club.png")
    else:
        fig, ax = plt.subplots(figsize=(13,7))
        ax.barh([k.replace("Club de Golf ","").replace("Club ","") for k,_ in items],
                [v/1e3 for _,v in items],
                color=[C[i%3] for i in range(len(items))], alpha=0.85)
        ax.set_xlabel("Pérdida estimada (miles MXN)")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:,.0f}K"))
        ax.set_title("Pérdida por No-Show de Fricción Social por Club")
        for i,(_,v) in enumerate(items):
            ax.text(v/1e3+0.5, i, f"${v/1e3:.0f}K", va="center", fontsize=8, color="#2d2d2d")
        save_fig("04b_perdida_friccion_club.png")

# =============================================================================
# SECCION 5 — SERIES DE TIEMPO PRINCIPALES
# =============================================================================
print("[5/7] Series de tiempo...")

# 5a. Reservas totales con banda de tendencia
fig, ax = plt.subplots(figsize=(15,5))
ax.plot(x, tot_res, color=C[0], linewidth=2.5, marker="o", markersize=4,
        label="Reservas mensuales")
z = np.polyfit(x, tot_res, 1); p = np.poly1d(z)
ax.plot(x, p(x), "--", color="#aaaaaa", linewidth=1.5, label="Tendencia lineal")
ax.fill_between(x, tot_res, alpha=0.12, color=C[0])
ax.set_xticks(x); ax.set_xticklabels(etiq, fontsize=7)
ax.axvline(11.5, color="#aaaaaa", linestyle=":", linewidth=1)
ax.text(5.5,  max(tot_res)*0.97, "2023", ha="center", fontsize=9, color="#888888")
ax.text(17.5, max(tot_res)*0.97, "2024", ha="center", fontsize=9, color="#888888")
ax.set_ylabel("Reservas por mes")
ax.set_title("Evolución Mensual de Reservas 2023-2024")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v:,.0f}"))
ax.legend()
save_fig("05a_series_reservas.png")

# 5b. Heatmap reservas: dia semana x mes (solo 2024)
DIAS = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
matrix = np.zeros((7,12))
for r in reservas:
    fid = r["id_fecha"]
    if fid[:4]=="2024":
        mes_i = int(fid[4:6])-1
        d = int(fid[6:8])
        import datetime
        dow = datetime.date(int(fid[:4]),int(fid[4:6]),d).weekday()
        matrix[dow, mes_i] += 1
fig, ax = plt.subplots(figsize=(14,5))
im = ax.imshow(matrix, aspect="auto", cmap="Greens")
ax.set_xticks(range(12)); ax.set_xticklabels(list(MESES_ABR.values()), fontsize=9)
ax.set_yticks(range(7));  ax.set_yticklabels(DIAS, fontsize=9)
cbar = plt.colorbar(im, ax=ax, label="Reservas")
cbar.ax.tick_params(colors="#2d2d2d")
cbar.ax.yaxis.label.set_color("#2d2d2d")
ax.set_title("Mapa de Calor: Reservas por Día de la Semana y Mes (2024)")
vmax = matrix.max()
for i in range(7):
    for j in range(12):
        val = matrix[i,j]
        txt_color = "white" if val > vmax * 0.55 else "#2d2d2d"
        ax.text(j, i, f"{int(val):,}", ha="center", va="center",
                fontsize=6, color=txt_color)
save_fig("05b_heatmap_dia_mes.png")

# =============================================================================
# SECCION 6 — ESTADISTICAS DESCRIPTIVAS
# =============================================================================
print("[6/7] Estadisticas descriptivas...")

def describe(data, label):
    s = sorted([v for v in data if v is not None])
    if not s: return None
    n = len(s)
    return {
        "variable": label, "n": n,
        "media":    round(statistics.mean(s),2),
        "mediana":  round(statistics.median(s),2),
        "desv_std": round(statistics.stdev(s),2) if n>1 else 0,
        "min":      round(s[0],2),
        "p25":      round(s[int(n*0.25)],2),
        "p75":      round(s[int(n*0.75)],2),
        "max":      round(s[-1],2),
    }

all_gf     = [float(r["green_fee_unitario_mxn"]) for r in reservas]
all_rat    = [float(r["rating_promedio"]) for r in ratings]
all_margin = [float(r["margen_por_transaccion"]) for r in reservas]
all_ns_perd= [float(r["perdida_total_estimada_mxn"]) for r in noshow]

stats_rows = [
    describe(all_gf,    "green_fee_unitario_mxn"),
    describe(tot_res,   "reservas_por_mes"),
    describe(tasa_can,  "tasa_cancelacion_pct"),
    describe(tasa_ns,   "tasa_noshow_pct"),
    describe(all_rat,   "rating_promedio"),
    describe(nps,       "nps_proxy"),
    describe(recompra,  "tasa_recompra_pct"),
    describe(cumpl_hor, "pct_cumplimiento_horario"),
    describe(pct_disc,  "pct_discrepancia_inventario"),
    describe(pct_fric,  "pct_friccion_social"),
    describe(all_margin,"margen_por_transaccion"),
    describe(all_ns_perd,"perdida_por_noshow_mxn"),
]
stats_rows = [r for r in stats_rows if r]

stats_path = os.path.join(FIGS,"estadisticas_descriptivas.csv")
with open(stats_path,"w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(stats_rows[0].keys()))
    w.writeheader(); w.writerows(stats_rows)

print("\n" + "="*88)
print("ESTADISTICAS DESCRIPTIVAS - Plataforma de Reservas de Golf 2023-2024")
print("="*88)
print(f"{'Variable':<38} {'N':>7} {'Media':>9} {'Mediana':>9} {'DE':>9} {'Min':>9} {'Max':>9}")
print("-"*88)
for row in stats_rows:
    print(f"{row['variable']:<38} {row['n']:>7,} {row['media']:>9,.2f} "
          f"{row['mediana']:>9,.2f} {row['desv_std']:>9,.2f} "
          f"{row['min']:>9,.2f} {row['max']:>9,.2f}")
print("="*88)

tot_res_glob  = len(reservas)
tasa_can_glob = sum(1 for r in reservas if r["estatus_reserva"]=="cancelada")/tot_res_glob*100
tasa_ns_glob  = sum(1 for r in reservas if r["estatus_reserva"]=="no_show")/tot_res_glob*100
ing_total     = sum(float(r["ingreso_total_mxn"]) for r in reservas)
com_total     = sum(float(r["comision_gogolf_mxn"]) for r in reservas)
rating_glob   = statistics.mean(all_rat)
fric_pct_glob = sum(1 for r in reservas if r["hay_friccion_social"]=="SI")/tot_res_glob*100
perdida_total = sum(float(r["perdida_total_estimada_mxn"]) for r in noshow)
nps_prom      = statistics.mean(nps)

print(f"\nKPIs GLOBALES 2023-2024")
print(f"  Total reservas:               {tot_res_glob:>10,}")
print(f"  Tasa de cancelacion:          {tasa_can_glob:>9.1f}%")
print(f"  Tasa de no-show:              {tasa_ns_glob:>9.1f}%")
print(f"  Ingreso total plataforma:     ${ing_total:>13,.0f} MXN")
print(f"  Comision total:               ${com_total:>13,.0f} MXN")
print(f"  Rating promedio:              {rating_glob:>9.2f} / 5.0")
print(f"  NPS proxy promedio:           {nps_prom:>9.1f}")
print(f"  % Reservas con friccion:      {fric_pct_glob:>9.1f}%")
print(f"  Perdida total no-show:        ${perdida_total:>13,.0f} MXN")

# =============================================================================
# SECCION 7 — DASHBOARD RESUMEN BSC (4 paneles)
# =============================================================================
print("[7/7] Dashboard BSC resumen...")

fig, axes = plt.subplots(2, 2, figsize=(16,10))
fig.patch.set_facecolor("white")
fig.suptitle("Dashboard BSC — Plataforma de Reservas de Golf 2023-2024",
             fontsize=15, fontweight="bold", color="#0f5c28", y=1.01)

# Panel 1: Financiero — utilidad mensual
ax = axes[0,0]
util_arr2 = np.array(utilidad)
ax.bar(x, util_arr2/1e6, color=[C[0] if v>=0 else C[6] for v in util_arr2], alpha=0.85)
ax.axhline(0, color="#444444", linewidth=0.7)
ax.set_xticks(x[::2]); ax.set_xticklabels([etiq[i] for i in range(0,len(etiq),2)], fontsize=6)
ax.set_title("Utilidad Neta Mensual (Comisión − Costo Var.)", fontsize=10)
ax.set_ylabel("Millones MXN")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v:.1f}M"))

# Panel 2: Cliente — NPS
ax = axes[0,1]
ax.bar(x, nps, color=[C[0] if v>=0 else C[6] for v in nps], alpha=0.80)
ax.axhline(0, color="#444444", linewidth=0.7)
ax.set_xticks(x[::2]); ax.set_xticklabels([etiq[i] for i in range(0,len(etiq),2)], fontsize=6)
ax.set_title("NPS Proxy Mensual", fontsize=10)
ax.set_ylabel("NPS (%)")
ax.plot(x, recompra, color=C[3], linewidth=1.5, linestyle="--", label="Recompra %")
ax.legend(fontsize=7)

# Panel 3: Procesos — no-show y cumplimiento
ax = axes[1,0]
ax.bar(x, tasa_ns, color=C[6], alpha=0.75, label="No-show %")
ax.plot(x, [100-v for v in cumpl_hor], color=C[0], linewidth=1.5,
        linestyle="--", label="Incumplimiento horario %")
ax.set_xticks(x[::2]); ax.set_xticklabels([etiq[i] for i in range(0,len(etiq),2)], fontsize=6)
ax.set_title("Procesos: No-Show e Incumplimiento de Horario", fontsize=10)
ax.set_ylabel("(%)")
ax.legend(fontsize=7)

# Panel 4: Aprendizaje — friccion social por NSE
ax = axes[1,1]
xi2 = np.arange(len(nse_ord))
bars_p = ax.bar(xi2, fric_pct, color=[C[0],C[2],C[3],C[6]], alpha=0.85)
ax.set_xticks(xi2); ax.set_xticklabels(nse_lbls, fontsize=10)
ax.set_title("Aprendizaje: % Fricción Social por NSE", fontsize=10)
ax.set_ylabel("% reservas con fricción")
for i,v in enumerate(fric_pct):
    ax.text(i, v+0.3, f"{v:.1f}%", ha="center", fontsize=9, color="#2d2d2d")

plt.tight_layout()
save_fig("00_dashboard_bsc.png")

print(f"\nTodas las graficas en ./graficas/")
print("Archivos:")
for f in sorted(os.listdir(FIGS)):
    size = os.path.getsize(os.path.join(FIGS,f))
    print(f"  {f:<55} {size/1024:>6.1f} KB")
