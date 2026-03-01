# GoGolf – Simulación de Datos y Dashboard BSC

Repositorio del proyecto de análisis estratégico para **GoGolf** ([gogolf.mx](https://gogolf.mx)), plataforma de reservas de golf en México. Dado que la empresa no podía compartir datos reales, se construyó un **datamart sintético** con datos creíbles basados en fuentes verificables.

---

## Estructura del Repositorio

```
golf_simulation_data/
│
├── data/
│   ├── raw/                  # Tablas del datamart (dimensiones y hechos)
│   │   ├── dim_club.csv          # 14 clubes reales de gogolf.mx
│   │   ├── dim_campo.csv         # Tipos de campo (18h, 9h, pitch, driving)
│   │   ├── dim_fecha.csv         # Calendario 2023-2024 con temporada y festivos
│   │   ├── dim_jugador.csv       # 2,000 perfiles con NSE, handicap, canal
│   │   ├── fact_reservas.csv     # Tabla de hechos principal (~27K reservas)
│   │   ├── fact_cancelaciones.csv
│   │   ├── fact_noshow.csv       # Con pérdida estimada y causa
│   │   ├── fact_fricciones.csv   # Eventos de fricción social por requisito
│   │   ├── fact_ratings.csv      # Ratings por aspecto + categoría NPS
│   │   ├── inventario_clubes.csv # Snapshot mensual de ocupación
│   │   └── gogolf_campos_reales.csv  # Datos scrapeados de gogolf.mx
│   │
│   └── processed/
│       └── kpi_bsc_mensual.csv   # KPIs BSC precalculados por mes
│
├── src/
│   ├── 00_scraper_gogolf.py      # Scraper Playwright para gogolf.mx
│   ├── 01_generar_datos.py       # Generador de datos sintéticos
│   ├── 02_analisis_descriptivo.py# Análisis descriptivo + gráficas estáticas
│   └── 03_generar_word.py        # Generador del documento Word del reporte
│
├── dashboard/
│   └── app.py                    # Dashboard Streamlit BSC (6 tabs)
│
├── docs/
│   └── GoGolf_Secciones_3_4_5.docx  # Reporte Word (secciones 3, 4 y 5)
│
├── requirements.txt
└── README.md
```

---

## Cómo Reproducir

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Generar el datamart

```bash
python src/01_generar_datos.py
```

Genera todos los CSVs en `data/raw/` y `data/processed/`.

### 3. Ejecutar el dashboard

```bash
streamlit run dashboard/app.py
```

### 4. (Opcional) Regenerar gráficas estáticas

```bash
python src/02_analisis_descriptivo.py
```

### 5. (Opcional) Regenerar el documento Word

```bash
python src/03_generar_word.py
```

---

## Diseño del Datamart

Esquema estrella con 5 dimensiones y 5 tablas de hechos:

```
dim_fecha ──┐
dim_club  ──┤
dim_campo ──┼──► fact_reservas ──► fact_cancelaciones
dim_jugador─┘         │
                       ├──► fact_noshow
                       ├──► fact_ratings
                       └──► fact_fricciones

dim_club ──► inventario_clubes
fact_reservas (agregado) ──► kpi_bsc_mensual
```

---

## Fuentes de Datos

| Fuente | Uso |
|--------|-----|
| [gogolf.mx](https://gogolf.mx) (Playwright scraping) | 14 clubes reales con green fees y requisitos |
| SMN / CONAGUA | Probabilidad de lluvia mensual por región |
| AMAI 2022 (Regla NSE) | Distribución socioeconómica de usuarios |
| Benchmarks sector marketplace | Tasas de cancelación, NPS de referencia |

---

## BSC — KPIs Implementados

| Perspectiva | KPI |
|-------------|-----|
| Financiera | Ingreso prom/reserva · Margen por transacción · Tasa de cancelación |
| Cliente | NPS proxy · Tasa de recompra · Rating promedio |
| Procesos | % Cumplimiento horario · % Discrepancia inventario · Tasa no-show |
| Aprendizaje | % Fricción social por NSE · Tiempo de implementación |

---

## Insight Central

El **58% de las reservas presentan fricción social**: jugadores NSE C/D+ que acceden a clubes con requisitos de dress code estricto, handicap máximo o equipo propio obligatorio. Esto explica el **NPS negativo (-7.4)** y la **tasa de no-show de 16.3%** — ambos indicadores son consecuencia de la brecha entre la promesa de democratización del golf de GoGolf y los requisitos actuales de los clubes afiliados.

---

## Equipo

Proyecto MNA – Análisis de Datos Sintéticos
Datos: Syntéticos | Clubes: Reales (gogolf.mx)
