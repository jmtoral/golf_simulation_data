# Datamart Sintético y Dashboard Estratégico BSC
## Plataforma de Reservas de Golf · México

> Plataforma digital que democratiza el acceso a campos de golf en México, conectando jugadores externos con clubes que aceptan reservas mediante green fee, sin necesidad de membresía ni anualidad.

---

## Nota sobre confidencialidad

> Debido a que la empresa se encuentra actualmente en **fases críticas de levantamiento de capital y auditoría de procesos**, se ha optado por utilizar un **Entorno de Datos Sintéticos de Alta Fidelidad** para este análisis. Este modelo replica las distribuciones probabilísticas, estacionalidades y reglas de negocio reales de la plataforma, permitiendo proyectar metas estratégicas sin comprometer la confidencialidad transaccional durante sus rondas de inversión.

Los precios de green fee y los 14 clubes son **reales**, extraídos directamente del sitio de la empresa. Las distribuciones de lluvia provienen del **SMN/CONAGUA** y la segmentación socioeconómica sigue la **Regla NSE AMAI 2022**.

---

## Dashboard BSC Interactivo

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

![Dashboard BSC](assets/00_dashboard_bsc.png)

---

## SIPOC del Proceso de Reserva

| **S — Suppliers** | **I — Inputs** | **P — Process** | **O — Outputs** | **C — Customers** |
|---|---|---|---|---|
| Clubes de golf (14) | Disponibilidad de tee times | 1. Jugador busca campo | Reserva confirmada | Jugador externo |
| Jugadores registrados | Perfil del jugador (NSE, handicap) | 2. Plataforma filtra por fecha/estado | Notificación al club | Club de golf |
| Pasarela de pago | Green fee publicado | 3. Jugador selecciona horario | Ingreso (green fee) | Plataforma (comisión) |
| Sistema de inventario | Requisitos de acceso del club | 4. Validación de requisitos de entrada | Comisión 8–12% | — |
| SMN/CONAGUA (lluvia) | Probabilidad de lluvia regional | 5. Pago y confirmación | Rating post-juego | — |
| — | Historial de reservas | 6. Juego completado o cancelado/no-show | KPIs BSC mensuales | — |

**Restricciones de calidad identificadas en el proceso:**
- Paso 4 (validación de requisitos): el 58.1% de las reservas presentan al menos un evento de fricción social no detectado antes de la confirmación.
- Paso 6 (resultado): tasa de no-show del 16.3%, más del doble del benchmark sectorial (6–8%).

---

## Cambios Implementados (Feedback del Cliente)

- **Crecimiento de Clubes:** Se simula la integración paulatina de 19 clubes (rango de green fee de $500 a $10,000 MXN, promedio ~$2,000 MXN). Capacidad de reservas acotada a la realidad del mercado (~100 green fees al mes por club como límite superior teórico).
- **Modelo de Ingresos:** GoGolf cobra una comisión del 22% sobre el green fee + una tarifa de $25 MXN por reserva.
- **Cancelaciones y No-Shows:** Las cancelaciones con menos de 24 horas ahora son "no-show" (pérdida del 100% para el jugador). Para cancelaciones válidas, GoGolf retiene un **8.9%** sobre el monto cancelado.
- **Fricción Social Realista:** Se redujo el impacto de rechazos directos por código de vestimenta. La fricción crítica causante de no-shows ahora es la **"llegada tarde"**. Exceder el hándicap máximo del club resulta en una **restricción de horario** (tee times asignados después de las 11:00 AM) en lugar de un rechazo.
- **Dashboard Actualizado:** Nuevo KPI superior de "Total Green Fees" y gráfica dinámica "Ritmo de Integración de Clubes" mostrando el despunte de oferta.

---

## Hallazgos Estratégicos

Los hallazgos se presentan alineados con la lógica causa–efecto del Balanced Scorecard:
**Aprendizaje y Crecimiento → Procesos Internos → Cliente → Financiera**.

---

### 🌱 Perspectiva de Aprendizaje y Crecimiento

#### Hallazgo 1: La base de clientes es mayoritariamente NSE medio-bajo — la misión democratizadora funciona, pero genera fricción

El **53% de los jugadores registrados** pertenecen a los segmentos NSE C y D+, con ingresos familiares por debajo de $35,000 MXN/mes. La plataforma está atrayendo al perfil de usuario que declara querer servir: el jugador que desea acceder al golf sin ser socio de un club privado.

Sin embargo, el **58.1% de todas las reservas presentan al menos un evento de fricción social**: dress code no conocido, equipo propio requerido pero no disponible, handicap excedido, o insuficiente anticipación de reserva. Esta fricción es la causa raíz de los problemas en todas las perspectivas superiores del BSC.

![Fricción Social por NSE](assets/04a_friccion_por_nse.png)

| Tipo de fricción | Frecuencia |
|---|---|
| Dress code incumplido | Alta (clubes con requisito estricto: 4 de 14) |
| Equipo propio requerido | Media (5 clubes lo exigen) |
| Handicap excedido | Media (varía por club: 28–54 máx) |
| Discrepancia de inventario | 3.7% de reservas confirmadas |
| Anticipación insuficiente | Baja (2–3 días mínimo en 6 clubes) |

**Implicación estratégica:** La solución no es filtrar usuarios de NSE bajo, sino rediseñar el flujo de reserva para que el sistema haga el matching club-jugador antes de confirmar, mostrando solo clubes compatibles con el perfil del usuario.

---

### ⚙️ Perspectiva de Procesos Internos

#### Hallazgo 2: La tasa de no-show (16.3%) es el principal siniestro operativo — más del doble del benchmark sectorial

La tasa de no-show promedio mensual es **16.3%**, significativamente superior al 6–8% típico de plataformas de reserva turística consolidadas. El análisis de causas muestra que la **fricción social es el driver principal**, por encima incluso del clima adverso.

![No-Show y Cumplimiento de Horario](assets/03a_noshow_cumplimiento.png)

La **pérdida total estimada** por no-shows en el período 2023–2024 asciende a **$25.3 millones MXN** — cada slot vacío representa ingreso irrecuperable para el club y pérdida de comisión para la plataforma.

#### Hallazgo 3: El cumplimiento de horario (85.7%) y las discrepancias de inventario (3.7%) son fricciones del modelo marketplace

El cumplimiento de horario se ubica **14 puntos por debajo de la meta de 96%** definida en el BSC para el largo plazo. Las discrepancias entre el inventario digital y la disponibilidad real del club generan confirmaciones que el club no puede honrar — fricción crítica que destruye confianza en ambos lados del marketplace.

![Discrepancia de Inventario y Fricción Social](assets/03b_discrepancia_friccion.png)

**Implicación estratégica:** Implementar una API en tiempo real con el sistema de reservas de cada club (en lugar de sincronización manual) reduciría las discrepancias de 3.7% a <1% en 12 meses.

---

### 👤 Perspectiva de Cliente

#### Hallazgo 4: El NPS negativo (-7.4) no es un problema de calidad de los campos — es un problema de expectativas no gestionadas

El **NPS proxy promedio es -7.4**, con más detractores que promotores en la base actual. Sin embargo, el rating promedio de los campos es **3.92/5.0** — los jugadores que logran completar una experiencia sin fricciones califican bien los clubes.

![NPS Proxy y Rating Mensual](assets/02a_nps_rating.png)

La divergencia entre NPS negativo y rating aceptable indica que el problema no es la calidad del golf, sino la **experiencia de reserva**: el jugador llega al club y encuentra requisitos que no conocía, o el horario no está disponible a pesar de la confirmación.

#### Hallazgo 5: La tasa de recompra del 56.8% es una señal positiva, pero está concentrada en NSE alto

La tasa de recompra promedio es **56.8%** — más de la mitad de usuarios activos reservan más de una vez al mes. Este es el activo más valioso del negocio: quienes superan la barrera inicial y tienen una buena experiencia regresan.

![Recompra y Usuarios Activos](assets/02b_recompra_usuarios.png)

El problema es que esta recurrencia está concentrada en NSE A/B y C+. Los usuarios NSE C y D+ presentan tasas de recompra significativamente menores — no porque el golf no les guste, sino porque la probabilidad de fricción en cada reserva desincentiva el intento.

---

### 💰 Perspectiva Financiera

#### Hallazgo 6: El ingreso promedio por reserva ($2,302 MXN) oculta una segmentación de tres velocidades

La mediana de green fee es $2,050 MXN, pero la distribución tiene cola larga hacia los resorts de Quintana Roo y Nayarit ($3,800–$5,330), lo que eleva el promedio artificialmente. El **65% de las reservas son de campos de 18 hoyos** a precio estándar; el **25% son de 9 hoyos** (campos más accesibles, con green fee ~45% menor).

![Boxplot Green Fee por Club](assets/01c_boxplot_greenfee_por_club.png)

#### Hallazgo 7: El margen por transacción (75.7%) es sólido, pero los no-shows lo erosionan sistemáticamente

Con una comisión de 8–12% y costos variables de ~$45–$65 MXN por reserva, el margen operativo es atractivo. Sin embargo, cada no-show elimina la comisión del evento y genera costos de atención al cliente — reducir la tasa de no-show de 16.3% a <10% (meta a 12 meses) equivale a recuperar aproximadamente **$8–10M MXN en comisiones anuales**.

![Comisión, Costo Variable y Margen](assets/01a_financiero_comision_margen.png)

#### Hallazgo 8: La estacionalidad concentra el 40% del ingreso en 5 meses — riesgo de flujo de caja en temporada baja

Los meses de mayo–agosto y diciembre concentran la demanda. Febrero y noviembre registran las tasas de ocupación más bajas (<50%). La estrategia de pricing dinámico y alianzas corporativas en temporada baja es crítica para la estabilidad financiera del modelo.

![Ingreso Promedio y Tasa de Cancelación](assets/01b_ingreso_prom_cancelacion.png)

---

## Metas SMART por Perspectiva (Resumen)

| Perspectiva | KPI | Baseline | Meta 6m | Meta 12m | Meta 24m |
|---|---|---|---|---|---|
| 💰 Financiera | Ingreso prom/reserva | $2,302 | $2,417 | $2,578 | $2,878 |
| 💰 Financiera | Margen por transacción | 75.7% | 78.7% | 81.7% | 85.7% |
| 💰 Financiera | Tasa de cancelación | 21.2% | <18% | <16% | <14% |
| 👤 Cliente | NPS proxy | -7.4 | >0 | >+10 | >+20 |
| 👤 Cliente | Tasa de recompra | 56.8% | >62% | >67% | >72% |
| 👤 Cliente | Rating promedio | 3.92 | >4.0 | >4.2 | >4.5 |
| ⚙️ Procesos | % Cumplimiento horario | 85.7% | >90% | >93% | >96% |
| ⚙️ Procesos | % Discrepancia inventario | 3.7% | <2.8% | <1.9% | <0.9% |
| ⚙️ Procesos | Tasa de no-show | 16.3% | <13% | <11% | <9% |
| 🌱 Aprendizaje | % Fricción social | 58.1% | <49% | <41% | <29% |
| 🌱 Aprendizaje | % Decisiones con análisis | ~30% | >50% | >70% | >85% |
| 🌱 Aprendizaje | Tiempo impl. mejoras (días) | ~45 | <35 | <25 | <15 |

---

## Diseño del Datamart — Esquema Entidad-Relación

```mermaid
erDiagram
    dim_fecha {
        string id_fecha PK
        int anio
        int mes
        int dia
        string dia_semana
        string temporada
        bool es_festivo
        float prob_lluvia
    }
    dim_club {
        string id_club PK
        string nombre_club
        string tipo_club
        string estado
        string ciudad
        int num_hoyos
        int par_total
        float green_fee_min
        float green_fee_max
        bool requisito_dress_code
        bool requiere_equipo_propio
        int handicap_maximo
        int dias_anticipacion_min
        string nse_minimo_acceso
        float latitud
        float longitud
    }
    dim_campo {
        string id_campo PK
        string tipo_campo
        int num_hoyos
        float multiplicador_precio
    }
    dim_jugador {
        string id_jugador PK
        string nse_jugador
        int handicap
        string canal_adquisicion
        bool tiene_equipo_propio
        bool conoce_dress_code
        string estado_residencia
    }
    fact_reservas {
        string id_reserva PK
        string id_fecha FK
        string id_club FK
        string id_campo FK
        string id_jugador FK
        string estatus_reserva
        float green_fee_unitario_mxn
        int num_jugadores
        float ingreso_total_mxn
        float comision_gogolf_mxn
        float costo_variable_mxn
        float margen_por_transaccion
        string hay_friccion_social
        string nse_jugador
        float prob_lluvia_dia
    }
    fact_cancelaciones {
        string id_cancelacion PK
        string id_reserva FK
        string motivo_cancelacion
        string tipo_cancelacion
        float penalizacion_pct
        float ingreso_cancelado_mxn
    }
    fact_noshow {
        string id_noshow PK
        string id_reserva FK
        string id_club FK
        string causa_principal
        int num_jugadores_noshow
        float perdida_estimada_club_mxn
        float comision_perdida_gogolf_mxn
        float perdida_total_estimada_mxn
    }
    fact_ratings {
        string id_rating PK
        string id_reserva FK
        float experiencia_general
        float condicion_campo
        float servicio_club
        float facilidad_reserva
        float relacion_precio_valor
        float rating_promedio
        string nps_categoria
    }
    fact_fricciones {
        string id_friccion PK
        string id_reserva FK
        string id_club FK
        string tipo_friccion
        string descripcion
    }
    inventario_clubes {
        string id_inv PK
        string id_club FK
        int anio
        int mes
        int slots_totales
        int slots_ocupados
        int slots_disponibles
        float tasa_ocupacion_pct
        float pct_discrepancia_inventario
    }
    kpi_bsc_mensual {
        string id_periodo PK
        int anio
        int mes
        int total_reservas
        float ingreso_promedio_por_reserva
        float comision_total_gogolf_mxn
        float costo_variable_total_mxn
        float utilidad_neta_estimada_mxn
        float margen_promedio_por_transaccion
        float tasa_cancelacion_pct
        float nps_proxy
        float rating_promedio_mes
        float tasa_recompra_pct
        int total_usuarios_activos_mes
        float pct_cumplimiento_horario
        float pct_discrepancia_inventario
        float tasa_noshow_pct
        float pct_friccion_social
    }

    dim_fecha     ||--o{ fact_reservas : "id_fecha"
    dim_club      ||--o{ fact_reservas : "id_club"
    dim_campo     ||--o{ fact_reservas : "id_campo"
    dim_jugador   ||--o{ fact_reservas : "id_jugador"
    fact_reservas ||--o| fact_cancelaciones : "id_reserva"
    fact_reservas ||--o| fact_noshow        : "id_reserva"
    fact_reservas ||--o| fact_ratings       : "id_reserva"
    fact_reservas ||--o{ fact_fricciones    : "id_reserva"
    dim_club      ||--o{ inventario_clubes  : "id_club"
```

---

## Estructura del Repositorio

```
golf_simulation_data/
│
├── data/
│   ├── raw/                       # Tablas del datamart (dims + facts)
│   │   ├── dim_club.csv               # 14 clubes reales
│   │   ├── dim_campo.csv              # Tipos de campo con multiplicador de precio
│   │   ├── dim_fecha.csv              # Calendario 2023-2024 (temporada, festivos)
│   │   ├── dim_jugador.csv            # 2,000 perfiles con NSE, handicap, canal
│   │   ├── fact_reservas.csv          # ~27K reservas con fricción y lluvia
│   │   ├── fact_cancelaciones.csv     # Motivo, tipo y penalización
│   │   ├── fact_noshow.csv            # Pérdida estimada y causa principal
│   │   ├── fact_fricciones.csv        # Eventos granulares de fricción social
│   │   ├── fact_ratings.csv           # 5 aspectos + categoría NPS
│   │   ├── inventario_clubes.csv      # Snapshot mensual de ocupación
│   │   └── campos_reales.csv          # Datos scrapeados del sitio oficial
│   │
│   └── processed/
│       └── kpi_bsc_mensual.csv        # KPIs BSC precalculados (24 periodos)
│
├── src/
│   ├── 00_scraper.py                  # Scraper Playwright (Chromium headless)
│   ├── 01_generar_datos.py            # Generador del datamart sintético
│   └── 02_analisis_descriptivo.py     # Análisis + gráficas estáticas
│
├── dashboard/
│   └── app.py                         # Dashboard Streamlit BSC (6 tabs)
│
├── assets/                            # Gráficas embebidas en este README
├── requirements.txt
└── README.md
```

---

## Reproducción

```bash
# 1. Instalar dependencias
pip install -r requirements.txt
playwright install chromium

# 2. Regenerar el datamart (semilla fija, 100% reproducible)
python src/01_generar_datos.py

# 3. Correr el dashboard
streamlit run dashboard/app.py

# 4. Regenerar gráficas estáticas
python src/02_analisis_descriptivo.py
```

---

## Fuentes de Datos

| Fuente | Uso |
|---|---|
| Sitio oficial de la plataforma (Playwright scraping) | 14 clubes con green fees reales y requisitos de entrada |
| SMN / CONAGUA | Probabilidad de lluvia mensual por región (9 regiones) |
| AMAI 2022 (Regla NSE) | Distribución socioeconómica: AB 12%, C+ 35%, C 38%, D+ 15% |
| Benchmarks sector marketplace | Tasas de cancelación, NPS y recompra de referencia |

---

*Proyecto MNA — Análisis Estratégico de Plataforma de Reservas de Golf · México · 2023–2024*
