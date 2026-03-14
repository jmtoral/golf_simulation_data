"""
GoGolf - Generador de Datos Sinteticos para Datamart v3
=======================================================
Novedades v3:
  - Requisitos de entrada por club (dress code, handicap, equipo propio)
  - Perfil socioeconomico del jugador (NSE A/B/C+/C/D) con ingreso estimado
  - Friccion social modelada: jugadores NSE bajo -> mayor tasa rechazo/noshow
    por requisitos no cumplidos
  - fact_fricciones: tabla de eventos de friccion (rechazo en puerta,
    discrepancia inventario, incumplimiento dress code)
  - KPIs BSC precalculados: NPS proxy, tasa recompra, cumplimiento horario,
    discrepancia inventario, insights trimestrales
  - Costos variables por reserva (para margen por transaccion)

Periodo: Enero 2023 - Diciembre 2024
"""

import random
import math
from datetime import date, timedelta
import csv
import os

random.seed(42)

OUT = os.path.join(os.path.dirname(__file__), "csv")
os.makedirs(OUT, exist_ok=True)

def csv_write(filename, fieldnames, rows):
    path = os.path.join(OUT, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  OK {filename:45s} ({len(rows):>6,} filas)")

# =============================================================================
# 1. DIM_CLUB con requisitos de entrada
# =============================================================================
# Requisitos reales tipicos en campos de golf mexicanos:
#   handicap_max    : indice de handicap maximo permitido (None = sin restriccion)
#   dress_code      : nivel de exigencia (ninguno / moderado / estricto)
#   equipo_propio   : exigen que el jugador lleve sus propios palos (SI/NO)
#   reserva_minima  : dias de anticipacion minima requerida
#   nse_min_acceso  : NSE minimo sugerido para poder costear sin friccion
#                     (A=1, B=2, C+=3, C=4, D=5)

clubes_raw = [
    # cid, nombre, ciudad, estado, tipo, hoyos, par, yardas, gf_lv, gf_fs, cierre, lat, lon,
    # handicap_max, dress_code, equipo_propio, reserva_min_dias, nse_min, fecha_integracion
    ("CLB001","Campestre Cocoyoc",               "Yautepec",             "Morelos",          "semi-privado",18,72,6744, 2000, 2500,{"martes"}, 18.9154,-98.9389,  36,"moderado","NO",1, 3, "2023-01-15"),
    ("CLB002","Club Campestre Coatzacoalcos",    "Coatzacoalcos",        "Veracruz",         "semi-privado", 9,71,6376, 1200, 1600,{"lunes"},  18.1500,-94.4300,  54,"moderado","NO",1, 4, "2023-01-20"),
    ("CLB003","Club de Golf Hacienda Soltepec",  "Huamantla",            "Tlaxcala",         "publico",       9,72,5772,  500,  800,{"lunes"},  19.3167,-97.9167,None,"ninguno", "NO",0, 4, "2023-01-25"),
    ("CLB004","Club de Golf La Purisima",        "Texcoco",              "Estado de Mexico", "semi-privado",18,55,   0, 1000, 1800,set(),       19.5167,-98.8833,  54,"moderado","NO",1, 4, "2023-02-15"),
    ("CLB005","Club de Golf Malanquin",          "San Miguel de Allende","Guanajuato",       "privado",      18,72,7289, 2800, 3500,{"lunes"},  20.9000,-100.7333, 28,"estricto","SI",2, 2, "2023-02-28"),
    ("CLB006","Club de Golf Santa Fe",           "Ciudad de Mexico",     "CDMX",             "privado",      18,72,7000, 3500, 5000,{"lunes"},  19.3600,-99.2700,  36,"estricto","SI",2, 2, "2023-03-10"),
    ("CLB007","Club de Golf Santa Gertrudis",    "Orizaba",              "Veracruz",         "historico",     9,70,   0, 1200, 1600,{"lunes"},  18.8500,-97.1000,  54,"moderado","NO",1, 3, "2023-04-10"),
    ("CLB008","Club de Golf Tequisquiapan",      "Tequisquiapan",        "Queretaro",        "privado",      18,72,   0, 2500, 3500,{"martes"}, 20.5333,-99.8833,  28,"estricto","SI",3, 2, "2023-05-15"),
    ("CLB009","Club de Golf Villa Rica",         "Veracruz",             "Veracruz",         "privado",      18,72,   0, 1800, 2800,{"lunes"},  19.2000,-96.1333,  36,"moderado","SI",2, 3, "2023-06-20"),
    ("CLB010","Club de Golf Xalapa",             "Xalapa",               "Veracruz",         "semi-privado", 18,72,   0, 1500, 2200,{"lunes"},  19.5333,-96.9500,  54,"moderado","NO",1, 3, "2023-07-25"),
    ("CLB011","El Tigre Golf Club",              "Nuevo Vallarta",       "Nayarit",          "resort",       18,72,7200, 6000, 6000,set(),       20.7000,-105.2833,None,"moderado","NO",0, 2, "2023-08-30"),
    ("CLB012","El Tinto Golf Course",            "Cancun",               "Quintana Roo",     "resort",       18,72,7435, 3000, 4500,set(),       21.1000,-86.8700, None,"moderado","NO",0, 3, "2023-09-05"),
    ("CLB013","Hard Rock Golf Club Riviera Maya","Playa del Carmen",     "Quintana Roo",     "resort",       18,71,6775, 4500, 5500,set(),       20.6296,-87.0739, None,"moderado","NO",0, 2, "2023-10-15"),
    ("CLB014","Riviera Cancun Golf Club",        "Cancun",               "Quintana Roo",     "resort",       18,72,   0, 8000,10000,set(),       21.0500,-86.8700, None,"estricto","SI",1, 2, "2023-11-20"),
    ("CLB015","Amanali Country Club",            "Tepeji del Rio",       "Hidalgo",          "privado",      18,72,7300, 2500, 3500,set(),       19.9213,-99.3496, 36,"moderado","NO",1, 2, "2023-12-10"),
    ("CLB016","Club de Golf Chapultepec",        "Naucalpan",            "Estado de Mexico", "privado",      18,72,7330, 6000, 8000,{"lunes"},   19.4261,-99.2325, 28,"estricto","SI",2, 1, "2024-01-15"),
    ("CLB017","Bosque Real Country Club",        "Huixquilucan",         "Estado de Mexico", "privado",      18,72,7100, 4000, 5000,{"lunes"},   19.3900,-99.2900, 36,"estricto","SI",2, 1, "2024-02-20"),
    ("CLB018","Club Campestre Monterrey",        "Monterrey",            "Nuevo Leon",       "privado",      18,72,7250, 5000, 7000,{"lunes"},   25.6315,-100.3204,28,"estricto","SI",3, 1, "2024-03-05"),
    ("CLB019","Punta Mita Golf Club",            "Punta de Mita",        "Nayarit",          "resort",       18,72,7014, 8500,10000,set(),       20.7633,-105.5265,None,"moderado","NO",0,1, "2024-04-10"),
]

REGION_LLUVIA = {
    "CLB001":"morelos","CLB002":"veracruz_costa","CLB003":"tlaxcala",
    "CLB004":"cdmx_edomex","CLB005":"bajio","CLB006":"cdmx_edomex",
    "CLB007":"veracruz_sierra","CLB008":"queretaro","CLB009":"veracruz_costa",
    "CLB010":"veracruz_sierra","CLB011":"pacifico_norte",
    "CLB012":"caribe","CLB013":"caribe","CLB014":"caribe",
    "CLB015":"cdmx_edomex","CLB016":"cdmx_edomex","CLB017":"cdmx_edomex",
    "CLB018":"bajio","CLB019":"pacifico_norte",
}

dim_club = []
for row in clubes_raw:
    (cid,nombre,ciudad,estado,tipo,hoyos,par,yardas,gf_lv,gf_fs,cierre,
     lat,lon,hdcp,dress,equipo,res_min,nse_min,fecha_int) = row
    dim_club.append({
        "id_club":                cid,
        "nombre_club":            nombre,
        "ciudad":                 ciudad,
        "estado":                 estado,
        "tipo_club":              tipo,
        "num_hoyos":              hoyos,
        "par":                    par,
        "yardas_blues":           yardas,
        "green_fee_lv_mxn":       gf_lv,
        "green_fee_fs_mxn":       gf_fs,
        "dia_cierre":             ",".join(sorted(cierre)) if cierre else "ninguno",
        "requisito_handicap_max": hdcp if hdcp else "sin_limite",
        "requisito_dress_code":   dress,
        "requisito_equipo_propio":equipo,
        "anticipacion_min_dias":  res_min,
        "nse_minimo_acceso":      nse_min,
        "latitud":                lat,
        "longitud":               lon,
        "fecha_integracion":      fecha_int,
        "fuente":                 "gogolf.mx",
        "activo":                 "SI",
    })
csv_write("dim_club.csv", list(dim_club[0].keys()), dim_club)

CIERRE_MAP      = {r[0]: r[10] for r in clubes_raw}
NSE_MIN_MAP     = {r[0]: r[17] for r in clubes_raw}
DRESS_MAP       = {r[0]: r[14] for r in clubes_raw}
HDCP_MAP        = {r[0]: r[13] for r in clubes_raw}
EQUIPO_MAP      = {r[0]: r[15] for r in clubes_raw}
RESMIN_MAP      = {r[0]: r[16] for r in clubes_raw}
INTEGRACION_MAP = {r[0]: date.fromisoformat(r[18]) for r in clubes_raw}

# =============================================================================
# 2. DIM_CAMPO
# =============================================================================
dim_campo = [
    {"id_tipo_campo":"CAMPO_18","descripcion":"18 hoyos","categoria":"estandar","multiplicador_precio":1.00},
    {"id_tipo_campo":"CAMPO_9", "descripcion":"9 hoyos", "categoria":"corto",   "multiplicador_precio":0.55},
    {"id_tipo_campo":"PITCH",   "descripcion":"Pitch & Putt","categoria":"practica","multiplicador_precio":0.30},
    {"id_tipo_campo":"DRIVING", "descripcion":"Driving Range","categoria":"practica","multiplicador_precio":0.20},
]
csv_write("dim_campo.csv", list(dim_campo[0].keys()), dim_campo)

# =============================================================================
# 3. LLUVIA POR REGION/MES  (SMN/CONAGUA)
# =============================================================================
PROB_LLUVIA = {
    "cdmx_edomex":    [0.05,0.04,0.07,0.14,0.28,0.55,0.60,0.58,0.52,0.28,0.08,0.04],
    "morelos":        [0.05,0.04,0.06,0.12,0.30,0.58,0.62,0.60,0.55,0.30,0.08,0.04],
    "veracruz_costa": [0.20,0.15,0.12,0.16,0.30,0.45,0.50,0.52,0.58,0.50,0.35,0.22],
    "veracruz_sierra":[0.12,0.10,0.10,0.18,0.35,0.55,0.58,0.56,0.60,0.45,0.22,0.12],
    "tlaxcala":       [0.04,0.04,0.07,0.12,0.25,0.50,0.55,0.52,0.48,0.25,0.07,0.04],
    "bajio":          [0.03,0.03,0.04,0.08,0.18,0.40,0.48,0.46,0.38,0.18,0.05,0.03],
    "queretaro":      [0.03,0.03,0.05,0.10,0.20,0.42,0.50,0.48,0.40,0.20,0.06,0.03],
    "pacifico_norte": [0.05,0.03,0.02,0.02,0.04,0.08,0.15,0.20,0.18,0.10,0.06,0.05],
    "caribe":         [0.10,0.08,0.07,0.10,0.18,0.35,0.38,0.40,0.50,0.45,0.25,0.12],
}
def prob_lluvia(id_club, mes):
    return PROB_LLUVIA[REGION_LLUVIA.get(id_club,"cdmx_edomex")][mes-1]

# =============================================================================
# 4. DIM_FECHA
# =============================================================================
DIAS_ES  = ["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"]
MESES_ES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
FESTIVOS = {
    date(2023,1,1),date(2023,2,6),date(2023,3,20),date(2023,4,6),date(2023,4,7),
    date(2023,5,1),date(2023,9,16),date(2023,11,2),date(2023,11,20),date(2023,12,25),
    date(2024,1,1),date(2024,2,5),date(2024,3,18),date(2024,3,28),date(2024,3,29),
    date(2024,5,1),date(2024,9,16),date(2024,11,2),date(2024,11,18),date(2024,12,25),
}
dim_fecha = []
d = date(2023,1,1)
while d <= date(2024,12,31):
    dow = d.weekday(); mes = d.month
    temporada = "alta" if mes in (5,6,7,8,12) else ("baja" if mes in (2,11) else "media")
    dim_fecha.append({
        "id_fecha":          d.strftime("%Y%m%d"),
        "fecha":             d.isoformat(),
        "anio":              d.year,
        "trimestre":         math.ceil(mes/3),
        "mes_num":           mes,
        "mes_nombre":        MESES_ES[mes-1],
        "semana_anio":       d.isocalendar()[1],
        "dia_semana_num":    dow+1,
        "dia_semana_nombre": DIAS_ES[dow],
        "es_fin_semana":     "SI" if dow>=5 else "NO",
        "es_festivo":        "SI" if d in FESTIVOS else "NO",
        "temporada":         temporada,
    })
    d += timedelta(days=1)
csv_write("dim_fecha.csv", list(dim_fecha[0].keys()), dim_fecha)

# =============================================================================
# 5. DIM_JUGADOR con NSE y perfil de friccion
# =============================================================================
# NSE Mexico (AMAI 2022):
#   A/B  ~7%  ingreso familiar >$85,000/mes  — golfistas de toda la vida
#   C+   ~14% ingreso ~$35,000-$85,000/mes  — pueden costear pero con esfuerzo
#   C    ~17% ingreso ~$11,600-$35,000/mes  — acceden a campos baratos
#   D+   ~33% ingreso ~$6,800-$11,600/mes   — muy ocasional, precio es barrera
#   D/E  ~29% — fuera del alcance del producto GoGolf
#
# GoGolf atrae principalmente C+ y C (democratizacion), con algo de A/B y D+
NSE_DIST = [
    # (nse, label, pct_gogolf, ingreso_familiar_min, ingreso_familiar_max,
    #   handicap_tipico_max, tiene_equipo_pct, conoce_dress_code_pct)
    ("AB",  "A/B",  0.12, 85000, 250000, 18, 0.90, 0.95),
    ("Cmas","C+",   0.35, 35000,  85000, 36, 0.60, 0.70),
    ("C",   "C",    0.38, 11600,  35000, 54, 0.30, 0.45),
    ("Dmas","D+",   0.15,  6800,  11600, 72, 0.10, 0.20),
]

NOMBRES   = ["Carlos","Luis","Ana","Maria","Jorge","Roberto","Patricia","Fernando",
             "Alejandro","Claudia","Ricardo","Sofia","Miguel","Laura","Hector",
             "Gabriela","Eduardo","Valeria","Andres","Diana","Pablo","Carmen",
             "Sergio","Monica","Arturo","Veronica","Javier","Lorena","Ernesto","Rebeca"]
APELLIDOS = ["Garcia","Martinez","Lopez","Gonzalez","Rodriguez","Hernandez",
             "Perez","Sanchez","Ramirez","Torres","Flores","Rivera","Gomez",
             "Diaz","Cruz","Morales","Ortiz","Reyes","Navarro","Jimenez",
             "Castillo","Moreno","Romero","Alvarez","Ruiz","Vargas","Delgado",
             "Castro","Mendoza","Guerrero"]
CIUDADES_J = ["Ciudad de Mexico","Monterrey","Guadalajara","Puebla","Queretaro",
              "Xalapa","Veracruz","Cuernavaca","Tlaxcala","Cancun",
              "Playa del Carmen","San Miguel de Allende","Coatzacoalcos","Toluca","Leon"]
NIVELES   = [("principiante",0.30),("intermedio",0.40),("avanzado",0.22),("profesional",0.08)]
CANALES   = [("app_movil",0.55),("web",0.35),("telefono",0.10)]

N_JUGADORES = 2000
dim_jugador = []
nse_pesos = [r[2] for r in NSE_DIST]

for i in range(1, N_JUGADORES+1):
    anio_reg = 2023 if i <= 600 else 2024
    mes_reg  = random.randint(1,12)
    dia_reg  = random.randint(1,28)

    nse_row  = random.choices(NSE_DIST, weights=nse_pesos)[0]
    nse_cod, nse_lbl, _, ing_min, ing_max, hdcp_tip, equipo_pct, dress_pct = nse_row

    ingreso_familiar = round(random.uniform(ing_min, ing_max), -2)
    handicap_jugador = random.randint(0, hdcp_tip) if hdcp_tip < 100 else random.randint(36, 72)
    nivel = random.choices([n for n,_ in NIVELES],[w for _,w in NIVELES])[0]
    canal = random.choices([c for c,_ in CANALES],[w for _,w in CANALES])[0]

    dim_jugador.append({
        "id_jugador":            f"JUG{i:05d}",
        "nombre":                random.choice(NOMBRES),
        "apellido_paterno":      random.choice(APELLIDOS),
        "apellido_materno":      random.choice(APELLIDOS),
        "anio_nacimiento":       random.randint(1960,2002),
        "ciudad_origen":         random.choice(CIUDADES_J),
        "nse":                   nse_cod,
        "nse_label":             nse_lbl,
        "ingreso_familiar_mensual_mxn": ingreso_familiar,
        "nivel_juego":           nivel,
        "handicap_declarado":    handicap_jugador,
        "tiene_equipo_propio":   "SI" if random.random() < equipo_pct else "NO",
        "conoce_dress_code":     "SI" if random.random() < dress_pct else "NO",
        "canal_preferido":       canal,
        "fecha_registro":        date(anio_reg,mes_reg,dia_reg).isoformat(),
        "activo":                random.choices(["SI","NO"],[0.88,0.12])[0],
    })
csv_write("dim_jugador.csv", list(dim_jugador[0].keys()), dim_jugador)

# Mapas rapidos
jug_map    = {j["id_jugador"]: j for j in dim_jugador}
campo_map  = {c["id_tipo_campo"]: c for c in dim_campo}
club_map   = {c["id_club"]: c for c in dim_club}
fecha_map  = {f["id_fecha"]: f for f in dim_fecha}
fechas_ids = [f["id_fecha"] for f in dim_fecha]
jugadores_ids = [j["id_jugador"] for j in dim_jugador]
DOW_NOMBRE = {0:"lunes",1:"martes",2:"miercoles",3:"jueves",
              4:"viernes",5:"sabado",6:"domingo"}
CAMPO_IDS  = [c["id_tipo_campo"] for c in dim_campo]
CAMPO_PESOS = [0.65,0.25,0.06,0.04]

# =============================================================================
# 6. LOGICA DE FRICCION SOCIAL
#    Dado un jugador y un club, determina si hay friccion y de que tipo.
#    La friccion puede derivar en: rechazo, no-show voluntario, o reserva
#    con incidencia (cumplimiento parcial de requisitos).
# =============================================================================
TIPOS_FRICCION = [
    "llegada_tarde",
    "handicap_horario_restringido",
    "anticipacion_insuficiente",
    "discrepancia_inventario",
]

def evaluar_friccion(jugador, club, dias_anticipacion):
    """
    Retorna lista de fricciones activas y probabilidad de que la reserva
    termine en rechazo/noshow por causa social.
    """
    fricciones = []
    prob_rechazo_extra = 0.0

    # 1. Llegada tarde
    if random.random() < 0.04: # 4% base de llegadas tarde
        fricciones.append("llegada_tarde")
        prob_rechazo_extra += 0.70 # Alta prob de que termine sin jugar si llega tarde

    # 2. Handicap (Causa restriccion de horario, a veces quejas, pero no rechazo directo)
    hdcp_max = HDCP_MAP[club["id_club"]]
    if hdcp_max and isinstance(hdcp_max, int):
        if jugador["handicap_declarado"] > hdcp_max:
            fricciones.append("handicap_horario_restringido")
            prob_rechazo_extra += 0.02 # Friccion muy leve (les molesta la restriccion)

    # 3. Anticipacion minima
    res_min = RESMIN_MAP[club["id_club"]]
    if dias_anticipacion < res_min:
        fricciones.append("anticipacion_insuficiente")
        prob_rechazo_extra += 0.05

    # 4. Discrepancia inventario (independiente del jugador, falla del sistema)
    if random.random() < 0.02:   # 2% base de discrepancias
        fricciones.append("discrepancia_inventario")
        prob_rechazo_extra += 0.30

    return fricciones, min(prob_rechazo_extra, 0.95)

# =============================================================================
# 7. FACT_RESERVAS
# =============================================================================
ESTATUS_BASE = [("confirmada",0.65),("cancelada",0.18),("no_show",0.10),("completada",0.07)]
CANALES_R    = [("app_movil",0.55),("web",0.35),("telefono",0.10)]
HORARIOS     = ["06:00","06:30","07:00","07:30","08:00","08:30","09:00","09:30",
                "10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30",
                "14:00","14:30","15:00","15:30","16:00","16:30","17:00"]

# Costo variable por reserva (operacion GoGolf): procesamiento pago, soporte
COSTO_VAR_BASE_MXN = 45.0

def reservas_dia(fecha_obj, jug_activos, clubes_disp_count):
    # Meta maxima: ~100 green fees al mes por campo = ~30 reservas = ~1 reserva/dia por campo activo
    base = min(1.2, jug_activos * 0.08 / 30) * clubes_disp_count
    mes  = fecha_obj.month
    if mes in (5,6,7,8,12): base *= 1.30
    elif mes in (2,11):      base *= 0.80
    if fecha_obj.weekday() >= 5: base *= 1.50
    if fecha_obj in FESTIVOS:    base *= 1.20
    return max(1, int(base + random.gauss(0, base*0.15)))

CLUB_PESOS_BASE = [1.0,0.6,0.5,0.7,0.8,0.9,0.5,0.8,0.6,0.6,1.2,1.0,1.0,1.0,0.8,0.9,0.7,0.7,1.1]

fact_reservas       = []
reservas_canceladas = []
reservas_noshow     = []
reservas_con_rating = []
fact_fricciones     = []
reserva_id = 1
friccion_id = 1

for fid in fechas_ids:
    fecha_obj  = date.fromisoformat(fid[:4]+"-"+fid[4:6]+"-"+fid[6:])
    dow_nombre = DOW_NOMBRE[fecha_obj.weekday()]
    mes        = fecha_obj.month
    es_fin     = fecha_obj.weekday() >= 5

    jug_activos = max(50, sum(
        1 for j in dim_jugador
        if j["activo"]=="SI" and date.fromisoformat(j["fecha_registro"])<=fecha_obj
    ))
    pool_jug = [j["id_jugador"] for j in dim_jugador
                if date.fromisoformat(j["fecha_registro"]) <= fecha_obj]
    if not pool_jug: pool_jug = jugadores_ids[:10]

    clubes_abiertos = [c for c in dim_club if INTEGRACION_MAP[c["id_club"]] <= fecha_obj]
    n_res = reservas_dia(fecha_obj, jug_activos, len(clubes_abiertos))

    for _ in range(n_res):
        # Club disponible ese dia
        clubes_disp  = [c for c in clubes_abiertos if dow_nombre not in CIERRE_MAP[c["id_club"]]]
        if not clubes_disp: continue
        pesos_disp   = [CLUB_PESOS_BASE[dim_club.index(c)] for c in clubes_disp]
        if mes in (5,6,7,8,12):
            pesos_disp = [p*(1.5 if c["tipo_club"]=="resort" else 1.0)
                          for p,c in zip(pesos_disp, clubes_disp)]
        club = random.choices(clubes_disp, weights=pesos_disp)[0]

        # Jugador
        jug_id  = random.choice(pool_jug)
        jugador = jug_map[jug_id]

        # Tipo de campo
        hoyos  = club["num_hoyos"]
        tipo_c = random.choices(
            ["CAMPO_9","PITCH","DRIVING"],[0.80,0.12,0.08]
        )[0] if hoyos==9 else random.choices(CAMPO_IDS,weights=CAMPO_PESOS)[0]
        campo  = campo_map[tipo_c]

        # Precio
        gf_base  = club["green_fee_fs_mxn"] if es_fin else club["green_fee_lv_mxn"]
        precio   = round(int(gf_base) * campo["multiplicador_precio"] * random.uniform(0.97,1.03), 2)
        num_jug  = random.choices([1,2,3,4],[0.20,0.35,0.30,0.15])[0]
        ingreso  = round(precio * num_jug, 2)
        # GoGolf cobra 22% del green fee + $25 MXN por reserva
        tasa_com = 0.22 
        comision = round((ingreso * tasa_com) + 25.0, 2)

        # Costo variable (incluye procesamiento + soporte)
        nse_n    = {"AB":1,"Cmas":2,"C":3,"Dmas":4}[jugador["nse"]]
        costo_var = round(COSTO_VAR_BASE_MXN * (1 + (nse_n-1)*0.15), 2)
        margen    = round((comision - costo_var) / comision, 4) if comision > 0 else 0.0

        # Dias de anticipacion
        dias_ant = random.choices(
            [0,1,2,3,4,5,6,7,14,21,30],
            weights=[0.08,0.15,0.18,0.15,0.12,0.08,0.07,0.07,0.05,0.03,0.02]
        )[0]

        # --- FRICCION SOCIAL ---
        fricciones_act, prob_rechazo_extra = evaluar_friccion(jugador, club, dias_ant)
        hay_friccion = len(fricciones_act) > 0
        
        horario_escogido = random.choice(HORARIOS)
        if "handicap_horario_restringido" in fricciones_act:
            horarios_tarde = [h for h in HORARIOS if int(h.split(":")[0]) >= 11]
            horario_escogido = random.choice(horarios_tarde)

        # Registrar fricciones en tabla aparte
        for tipo_fric in fricciones_act:
            fact_fricciones.append({
                "id_friccion":      f"FRI{friccion_id:07d}",
                "id_reserva":       f"RES{reserva_id:07d}",
                "id_club":          club["id_club"],
                "id_jugador":       jug_id,
                "id_fecha":         fid,
                "tipo_friccion":    tipo_fric,
                "nse_jugador":      jugador["nse"],
                "nse_minimo_club":  club["nse_minimo_acceso"],
                "dress_code_club":  club["requisito_dress_code"],
                "handicap_jugador": jugador["handicap_declarado"],
                "handicap_max_club":club["requisito_handicap_max"],
                "prob_rechazo":     round(prob_rechazo_extra, 3),
                "derivó_en_rechazo":"",   # se llena abajo
            })
            friccion_id += 1

        # Lluvia
        p_lluvia  = prob_lluvia(club["id_club"], mes)
        hay_lluvia = random.random() < p_lluvia

        # Estatus: ajustado por friccion + lluvia
        # Las cancelaciones deben ser mas altas que los no-shows (regla de negocio)
        pesos_est = [("confirmada",0.75),("cancelada",0.16),("no_show",0.04),("completada",0.05)]
        if hay_lluvia:
            pesos_est = [("confirmada",0.50),("cancelada",0.30),("no_show",0.10),("completada",0.10)]
        if hay_friccion:
            # Friccion aumenta fuertemente el no-show si llegan tarde (rechazo velado)
            conf_w = max(0.10, pesos_est[0][1] - prob_rechazo_extra*0.5)
            ns_w   = min(0.60, pesos_est[2][1] + prob_rechazo_extra*0.6)
            can_w  = min(0.35, pesos_est[1][1] + prob_rechazo_extra*0.2)
            com_w  = pesos_est[3][1]
            tot    = conf_w + ns_w + can_w + com_w
            pesos_est = [("confirmada",conf_w/tot),("cancelada",can_w/tot),
                         ("no_show",ns_w/tot),("completada",com_w/tot)]

        estatus = random.choices([e for e,_ in pesos_est],[w for _,w in pesos_est])[0]

        # Marcar si la friccion derivó en rechazo (no_show por requisito)
        if hay_friccion and estatus == "no_show":
            for fric in fact_fricciones:
                if fric["id_reserva"] == f"RES{reserva_id:07d}":
                    fric["derivó_en_rechazo"] = "SI"
        elif hay_friccion:
            for fric in fact_fricciones:
                if fric["id_reserva"] == f"RES{reserva_id:07d}":
                    fric["derivó_en_rechazo"] = "NO"

        # Cumplimiento de horario (BSC: procesos internos)
        # Discrepancia si hay friccion tipo inventario o si reserva es misma hora
        hay_discrepancia = "discrepancia_inventario" in fricciones_act
        cumplimiento_horario = "NO" if (hay_discrepancia or
                                        (estatus=="no_show" and hay_friccion)) else "SI"

        rid = f"RES{reserva_id:07d}"

        # Pierden todo el dinero si es no_show
        perdida_noshow = round(ingreso, 2) if estatus=="no_show" else 0.0

        row = {
            "id_reserva":                  rid,
            "id_fecha":                    fid,
            "id_club":                     club["id_club"],
            "id_jugador":                  jug_id,
            "id_tipo_campo":               tipo_c,
            "nse_jugador":                 jugador["nse"],
            "horario_tee_time":            horario_escogido,
            "num_jugadores_grupo":         num_jug,
            "es_fin_semana":               "SI" if es_fin else "NO",
            "hubo_lluvia":                 "SI" if hay_lluvia else "NO",
            "prob_lluvia_region":          round(p_lluvia,3),
            "hay_friccion_social":         "SI" if hay_friccion else "NO",
            "num_fricciones":              len(fricciones_act),
            "green_fee_unitario_mxn":      precio,
            "ingreso_total_mxn":           ingreso,
            "costo_variable_mxn":          costo_var,
            "tasa_comision_gogolf":        tasa_com,
            "comision_gogolf_mxn":         comision,
            "margen_por_transaccion":      margen,
            "canal_reserva":               random.choices([c for c,_ in CANALES_R],[w for _,w in CANALES_R])[0],
            "estatus_reserva":             estatus,
            "cumplimiento_horario":        cumplimiento_horario,
            "discrepancia_inventario":     "SI" if hay_discrepancia else "NO",
            "perdida_estimada_noshow_mxn": perdida_noshow,
            "dias_anticipacion":           dias_ant,
        }
        fact_reservas.append(row)

        if estatus == "cancelada":
            reservas_canceladas.append((rid, precio, num_jug, hay_friccion))
        if estatus == "no_show":
            reservas_noshow.append((rid, precio, num_jug, club["id_club"],
                                    hay_lluvia, hay_friccion, fricciones_act))
        if estatus in ("completada","confirmada"):
            reservas_con_rating.append((rid, jug_id, club["id_club"], jugador["nse"]))
        reserva_id += 1

csv_write("fact_reservas.csv", list(fact_reservas[0].keys()), fact_reservas)
csv_write("fact_fricciones.csv", list(fact_fricciones[0].keys()), fact_fricciones)

# =============================================================================
# 8. FACT_CANCELACIONES
# =============================================================================
MOTIVOS_CANCEL = [
    ("clima_adverso",0.22),("cambio_de_planes",0.18),("lesion_enfermedad",0.12),
    ("trabajo_compromiso",0.15),("requisito_no_cumplido",0.12),
    ("precio_alto",0.12),("error_sistema",0.05),("otro",0.04),
]
TIPO_CANCEL = [("anticipada_>48h",0.60),("anticipada_24-48h",0.40)]

fact_cancelaciones = []
for rid, precio, num_jug, con_friccion in reservas_canceladas:
    # Si hay friccion, el motivo tiende a ser requisito o precio
    if con_friccion:
        motivos_adj = [("requisito_no_cumplido",0.30),("precio_alto",0.20),
                       ("cambio_de_planes",0.15),("clima_adverso",0.10),
                       ("lesion_enfermedad",0.10),("trabajo_compromiso",0.10),
                       ("error_sistema",0.03),("otro",0.02)]
    else:
        motivos_adj = MOTIVOS_CANCEL
    motivo = random.choices([m for m,_ in motivos_adj],[w for _,w in motivos_adj])[0]
    tipo   = random.choices([t for t,_ in TIPO_CANCEL],[w for _,w in TIPO_CANCEL])[0]
    reembolso = 1.0 - 0.089 # Penalizacion del 8.9%
    horas = {"anticipada_>48h":random.randint(49,240),"anticipada_24-48h":random.randint(24,48)}[tipo]
    ingreso_cancel = round(precio*num_jug,2)
    # GoGolf retiene el 8.9% de cancelacion
    comision_retenida = round(ingreso_cancel * 0.089, 2)
    
    fact_cancelaciones.append({
        "id_cancelacion":             f"CAN{len(fact_cancelaciones)+1:07d}",
        "id_reserva":                 rid,
        "motivo_cancelacion":         motivo,
        "tipo_cancelacion":           tipo,
        "horas_antes_tee_time":       horas,
        "pct_reembolso":              round(reembolso,4),
        "penalizacion_aplicada":      "SI",
        "ingreso_cancelado_mxn":      ingreso_cancel,
        "cancelacion_por_friccion":   "SI" if con_friccion else "NO",
        "comision_retenida_gogolf_mxn": comision_retenida,
    })
csv_write("fact_cancelaciones.csv", list(fact_cancelaciones[0].keys()), fact_cancelaciones)

# =============================================================================
# 9. FACT_NOSHOW
# =============================================================================
fact_noshow = []
for rid, precio, num_jug, id_club, lluvia, friccion, fricc_tipos in reservas_noshow:
    ingreso_perdido = round(precio*num_jug,2)
    causa_principal = "friccion_social" if friccion else ("lluvia" if lluvia else "otro")
    fact_noshow.append({
        "id_noshow":                     f"NSW{len(fact_noshow)+1:07d}",
        "id_reserva":                    rid,
        "id_club":                       id_club,
        "causa_principal":               causa_principal,
        "fricciones_detectadas":         "|".join(fricc_tipos) if fricc_tipos else "",
        "lluvia_como_factor":            "SI" if lluvia else "NO",
        "friccion_social_como_factor":   "SI" if friccion else "NO",
        "num_jugadores_noshow":          num_jug,
        "ingreso_perdido_club_mxn":      0.0, # El campo no pierde, pago ex-ante
        "comision_perdida_gogolf_mxn":   0.0, # GoGolf retiene su comision
        "perdida_total_estimada_mxn":    ingreso_perdido, # Pierde el jugador al 100%
    })
csv_write("fact_noshow.csv", list(fact_noshow[0].keys()), fact_noshow)

# =============================================================================
# 10. FACT_RATINGS con NPS proxy
#     Rating 9-10 (escala 1-5 -> 5) = promotor
#     Rating 7-8  (escala -> 4)     = neutro
#     Rating <=6  (escala -> <=3)   = detractor
# =============================================================================
rids_rating = random.sample(reservas_con_rating, k=int(len(reservas_con_rating)*0.38))
ASPECTOS = ["experiencia_general","condicion_campo","servicio_club",
            "facilidad_reserva","relacion_precio_valor"]

fact_ratings = []
# Variabilidad mensual del NPS: algunos meses buenos, algunos malos
# Semilla ya fija arriba, esto produce resultados reproducibles
_nps_mes_mod = {}
for _y in [2023, 2024]:
    for _m in range(1, 13):
        # Modificador mensual: ciclo con picos en temporada alta (may-ago, dic)
        if _m in (5, 6, 7, 8, 12):   _nps_mes_mod[(_y, _m)] = +0.30   # buen mes
        elif _m in (1, 3, 4, 10):    _nps_mes_mod[(_y, _m)] = +0.10   # mes normal
        else:                        _nps_mes_mod[(_y, _m)] = -0.05   # mes bajo

for rid, jug_id, id_club, nse in rids_rating:
    # Extraer mes de la reserva para aplicar modificador estacional
    fid = next((r["id_fecha"] for r in fact_reservas if r["id_reserva"] == rid), None)
    mes_mod = 0.0
    if fid:
        _k = (int(fid[:4]), int(fid[4:6]))
        mes_mod = _nps_mes_mod.get(_k, 0.0)

    # Pesos base por NSE — media global ~3.65 → NPS oscila entre -12 y +12
    # Escala [1, 2, 3, 4, 5]
    if nse == "AB":
        weights_r = [0.03, 0.06, 0.18, 0.42, 0.31]   # media ~3.92 → buen NPS en picos
    elif nse == "Cmas":
        weights_r = [0.05, 0.09, 0.22, 0.40, 0.24]   # media ~3.69
    elif nse == "C":
        weights_r = [0.08, 0.12, 0.24, 0.36, 0.20]   # media ~3.48, fricción visible
    else:  # Dmas
        weights_r = [0.11, 0.15, 0.25, 0.32, 0.17]   # media ~3.29, mayor frustración

    # Aplicar modificador mensual: desplazar pesos hacia 5 (buen mes) o 1 (mal mes)
    w = list(weights_r)
    if mes_mod > 0:
        shift = mes_mod * 0.10
        w = [max(0, w[i] - shift/4) for i in range(4)] + [w[4] + shift]
    elif mes_mod < 0:
        shift = abs(mes_mod) * 0.10
        w = [w[0] + shift] + [max(0, w[i] - shift/4) for i in range(1, 5)]
    total_w = sum(w)
    w = [v / total_w for v in w]

    ratings_asp = {a: random.choices([1,2,3,4,5], w)[0] for a in ASPECTOS}
    promedio = round(sum(ratings_asp.values()) / len(ratings_asp), 2)

    # NPS: umbrales calibrados para rango realista -15 a +15 con variabilidad mensual
    # Promotor (NPS 9-10): promedio >= 4.1  → ~35-45% de ratings
    # Neutro   (NPS 7-8):  4.1 > promedio >= 3.4
    # Detractor (NPS 0-6): promedio < 3.4   → ~15-25% de ratings
    if promedio >= 4.1:   nps_cat = "promotor"
    elif promedio >= 3.4: nps_cat = "neutro"
    else:                 nps_cat = "detractor"

    fact_ratings.append({
        "id_rating":              f"RAT{len(fact_ratings)+1:07d}",
        "id_reserva":             rid,
        "id_club":                id_club,
        "nse_jugador":            nse,
        **ratings_asp,
        "rating_promedio":        promedio,
        "nps_categoria":          nps_cat,
        "tiene_comentario":       random.choices(["SI","NO"],[0.35,0.65])[0],
    })
csv_write("fact_ratings.csv", list(fact_ratings[0].keys()), fact_ratings)

# =============================================================================
# 11. INVENTARIO_CLUBES
# =============================================================================
inventario = []
for anio in [2023,2024]:
    for mes in range(1,13):
        for club in dim_club:
            hoyos = club["num_hoyos"]
            cap_dia = 40 if hoyos==9 else 80
            dias_mes = 28+(4 if mes!=2 else 0)
            cierres = CIERRE_MAP[club["id_club"]]
            dias_cierre = int(len(cierres)*dias_mes/7)
            dias_abierto = dias_mes - dias_cierre
            cap_mensual = cap_dia * dias_abierto
            base_ocup = 0.72 if mes in (5,6,7,8,12) else (0.45 if mes in (2,11) else 0.58)
            if club["tipo_club"]=="resort": base_ocup += 0.10
            ocupacion = min(0.97, random.uniform(base_ocup-0.08, base_ocup+0.12))
            slots_usados = int(cap_mensual*ocupacion)
            gf_prom = (club["green_fee_lv_mxn"]*5+club["green_fee_fs_mxn"]*2)/7
            # Discrepancias de inventario del mes
            pct_discrepancia = round(random.uniform(0.01, 0.08), 4)  # 1-8%
            inventario.append({
                "id_inventario":                  f"INV{len(inventario)+1:06d}",
                "id_club":                        club["id_club"],
                "anio":                           anio,
                "mes":                            mes,
                "dias_abierto_mes":               dias_abierto,
                "slots_disponibles_mes":          cap_mensual,
                "slots_reservados_mes":           slots_usados,
                "slots_libres_mes":               cap_mensual-slots_usados,
                "pct_ocupacion":                  round(ocupacion,4),
                "green_fee_promedio_ponderado_mxn":round(gf_prom,2),
                "pct_discrepancia_inventario":    pct_discrepancia,
                "casos_discrepancia_mes":         int(slots_usados*pct_discrepancia),
            })
csv_write("inventario_clubes.csv", list(inventario[0].keys()), inventario)

# =============================================================================
# 12. KPI_BSC_MENSUAL — tabla precalculada de indicadores BSC
# =============================================================================
from collections import defaultdict

mensual = defaultdict(lambda:{
    "reservas":0,"canceladas":0,"noshows":0,"completadas_confirmadas":0,
    "ingresos":0.0,"comisiones":0.0,"costos_var":0.0,"margenes":[],
    "fricciones":0,"discrepancias":0,"sin_cumplimiento":0,
    "jugadores":set(),
})

for r in fact_reservas:
    fid = r["id_fecha"]; y,m = int(fid[:4]),int(fid[4:6]); k=(y,m)
    mensual[k]["reservas"]       += 1
    mensual[k]["ingresos"]       += r["ingreso_total_mxn"]
    mensual[k]["comisiones"]     += r["comision_gogolf_mxn"]
    mensual[k]["costos_var"]     += r["costo_variable_mxn"]
    mensual[k]["margenes"].append(r["margen_por_transaccion"])
    mensual[k]["jugadores"].add(r["id_jugador"])
    if r["estatus_reserva"]=="cancelada":    mensual[k]["canceladas"]+=1
    if r["estatus_reserva"]=="no_show":      mensual[k]["noshows"]+=1
    if r["estatus_reserva"] in ("completada","confirmada"):
        mensual[k]["completadas_confirmadas"]+=1
    if r["hay_friccion_social"]=="SI":       mensual[k]["fricciones"]+=1
    if r["discrepancia_inventario"]=="SI":   mensual[k]["discrepancias"]+=1
    if r["cumplimiento_horario"]=="NO":      mensual[k]["sin_cumplimiento"]+=1

# Tasa de recompra: jugadores con >=2 reservas en el mes
jug_reservas_mes = defaultdict(lambda:defaultdict(int))
for r in fact_reservas:
    fid=r["id_fecha"]; k=(int(fid[:4]),int(fid[4:6]))
    jug_reservas_mes[k][r["id_jugador"]] += 1

# NPS por mes
nps_mes = defaultdict(lambda:{"promotores":0,"neutros":0,"detractores":0,"total":0})
# Mapa rapido reserva->fecha
res_fecha_map = {r["id_reserva"]: r["id_fecha"] for r in fact_reservas}
# Mapa nps_categoria -> clave en dict
NPS_KEY = {"promotor":"promotores","neutro":"neutros","detractor":"detractores"}
for rt in fact_ratings:
    fid_r = res_fecha_map.get(rt["id_reserva"])
    if not fid_r: continue
    k=(int(fid_r[:4]),int(fid_r[4:6]))
    nps_mes[k][NPS_KEY[rt["nps_categoria"]]] += 1
    nps_mes[k]["total"] += 1

MESES_ES2 = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
             "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

# Pre-calcular rating promedio por mes usando res_fecha_map
rating_mes = defaultdict(list)
for rt in fact_ratings:
    fid_r = res_fecha_map.get(rt["id_reserva"])
    if fid_r:
        k2 = (int(fid_r[:4]), int(fid_r[4:6]))
        rating_mes[k2].append(rt["rating_promedio"])

kpi_bsc = []
periodos = sorted(mensual.keys())
for k in periodos:
    y,m = k
    d  = mensual[k]
    res = d["reservas"]; can = d["canceladas"]; ns = d["noshows"]
    ing = d["ingresos"]; com = d["comisiones"]; cvar = d["costos_var"]
    jugs = d["jugadores"]
    jrm  = jug_reservas_mes[k]
    con_recompra = sum(1 for v in jrm.values() if v>=2)
    # NPS
    np_d = nps_mes[k]
    tot_nps = np_d["total"] or 1
    nps_val = round((np_d["promotores"]/tot_nps - np_d["detractores"]/tot_nps)*100, 1)

    kpi_bsc.append({
        # Periodo
        "anio":                          y,
        "mes":                           m,
        "mes_nombre":                    MESES_ES2[m-1],
        # --- FINANCIERA ---
        "ingreso_total_mxn":             round(ing,2),
        "comision_total_gogolf_mxn":     round(com,2),
        "costo_variable_total_mxn":      round(cvar,2),
        "utilidad_neta_estimada_mxn":    round(com-cvar,2),
        "ingreso_promedio_por_reserva":  round(ing/res,2) if res else 0,
        "margen_promedio_por_transaccion":round(sum(d["margenes"])/len(d["margenes"]),4) if d["margenes"] else 0,
        "tasa_cancelacion_pct":          round(can/res*100,2) if res else 0,
        # --- CLIENTE ---
        "nps_proxy":                     nps_val,
        "total_usuarios_activos_mes":    len(jugs),
        "usuarios_con_recompra":         con_recompra,
        "tasa_recompra_pct":             round(con_recompra/len(jugs)*100,2) if jugs else 0,
        "rating_promedio_mes":           round(sum(rating_mes[k])/len(rating_mes[k]),4) if rating_mes[k] else 0,
        # --- PROCESOS ---
        "total_reservas":                res,
        "tasa_noshow_pct":               round(ns/res*100,2) if res else 0,
        "pct_cumplimiento_horario":      round((res-d["sin_cumplimiento"])/res*100,2) if res else 0,
        "pct_discrepancia_inventario":   round(d["discrepancias"]/res*100,2) if res else 0,
        "reservas_con_friccion_social":  d["fricciones"],
        "pct_friccion_social":           round(d["fricciones"]/res*100,2) if res else 0,
        # --- APRENDIZAJE (trimestral, se repite el valor del trimestre) ---
        "trimestre":                     math.ceil(m/3),
    })
csv_write("kpi_bsc_mensual.csv", list(kpi_bsc[0].keys()), kpi_bsc)

# =============================================================================
# Resumen final
# =============================================================================
perdida_noshow  = sum(r["perdida_total_estimada_mxn"] for r in fact_noshow)
friccion_social = sum(1 for r in fact_fricciones if r["derivó_en_rechazo"]=="SI")
pct_nse_bajo    = sum(1 for j in dim_jugador if j["nse"] in ("C","Dmas"))/len(dim_jugador)*100

print("\nListo! Todos los archivos CSV generados en ./csv/")
print(f"  Clubes reales GoGolf:   {len(dim_club)}")
print(f"  Jugadores (max 2,000):  {len(dim_jugador)}")
print(f"  NSE bajo (C+D) en base: {pct_nse_bajo:.0f}%")
print(f"  Total reservas:         {len(fact_reservas):,}")
print(f"  Cancelaciones:          {len(fact_cancelaciones):,}")
print(f"  No-shows:               {len(fact_noshow):,}")
print(f"  Eventos de friccion:    {len(fact_fricciones):,}")
print(f"  Fricciones->rechazo:    {friccion_social:,}")
print(f"  Ratings:                {len(fact_ratings):,}")
print(f"  Perdida total no-show:  ${perdida_noshow:,.0f} MXN")
print(f"  KPI BSC mensual:        {len(kpi_bsc)} periodos")
