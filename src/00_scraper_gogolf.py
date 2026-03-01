"""
GoGolf - Scraper de campos disponibles
Usa Playwright (Chromium) para renderizar el JS y extraer todos los campos.
Tambien intercepta llamadas de red para capturar la API interna si existe.
"""

import json, csv, os, time
from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(__file__), "csv")
os.makedirs(OUT, exist_ok=True)

api_responses = []   # guarda cualquier respuesta JSON que interceptemos

def handle_response(response):
    url = response.url
    # Capturar llamadas JSON que parezcan listas de campos
    if any(k in url for k in ["field", "course", "club", "search", "api"]):
        ct = response.headers.get("content-type", "")
        if "json" in ct:
            try:
                body = response.json()
                api_responses.append({"url": url, "body": body})
                print(f"  [API] {url}")
            except Exception:
                pass

def scrape_page(page, url):
    print(f"\nAbriendo: {url}")
    page.goto(url, wait_until="networkidle", timeout=30000)
    # Esperar a que carguen tarjetas de campos
    try:
        page.wait_for_selector("a[href*='/fields/'], .field-card, .course-card, [class*='field'], [class*='course'], [class*='club']",
                               timeout=10000)
    except Exception:
        pass
    time.sleep(2)   # margen extra para JS lento
    return page.content()

def extract_fields_from_html(html):
    """Extraccion simple sin BeautifulSoup usando busqueda de texto."""
    import re
    # Buscar nombres de clubes en titulos h2/h3/h4 o dentro de tarjetas
    names = re.findall(r'<h[2-4][^>]*>([^<]{5,80})</h[2-4]>', html)
    prices = re.findall(r'\$[\s]*([\d,]+)', html)
    return names, prices

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        viewport={"width": 1280, "height": 900},
        locale="es-MX",
    )
    page = ctx.new_page()
    page.on("response", handle_response)

    all_html = {}
    for pg_num in range(1, 6):   # intenta hasta 5 paginas
        url = f"https://gogolf.mx/fields/search?page={pg_num}"
        try:
            html = scrape_page(page, url)
            all_html[pg_num] = html
            # Si la pagina es identica a la anterior, detener paginacion
            if pg_num > 1 and html == all_html[pg_num - 1]:
                print(f"  Pagina {pg_num} identica a la anterior -> fin de resultados")
                break
        except Exception as e:
            print(f"  Error en pagina {pg_num}: {e}")
            break

    # Guardar HTML para inspeccion
    html_path = os.path.join(OUT, "gogolf_raw.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(list(all_html.values())[-1] if all_html else "")
    print(f"\nHTML guardado en: {html_path}")

    # Guardar respuestas API interceptadas
    if api_responses:
        api_path = os.path.join(OUT, "gogolf_api_responses.json")
        with open(api_path, "w", encoding="utf-8") as f:
            json.dump(api_responses, f, ensure_ascii=False, indent=2)
        print(f"Respuestas API guardadas en: {api_path}")
        print(f"Total llamadas API capturadas: {len(api_responses)}")
    else:
        print("No se interceptaron llamadas API JSON.")

    # Screenshot para diagnostico
    shot_path = os.path.join(OUT, "gogolf_screenshot.png")
    page.screenshot(path=shot_path, full_page=True)
    print(f"Screenshot guardado en: {shot_path}")

    browser.close()

# ── Parsear HTML final con regex ──────────────────────────────────────────────
import re

final_html = list(all_html.values())[-1] if all_html else ""

# Buscar bloques de campos: texto entre etiquetas de tarjeta
# Estrategia: extraer todos los textos con precio MXN cercanos a un nombre
fields_found = []

# Patron: cualquier bloque que tenga nombre y precio juntos
blocks = re.findall(
    r'(?:field|course|club|card|item)[^>]*>(.*?)</(?:div|article|section|li)',
    final_html, re.IGNORECASE | re.DOTALL
)

print(f"\nBloques de tarjeta encontrados en HTML: {len(blocks)}")
for b in blocks[:20]:
    text = re.sub(r'<[^>]+>', ' ', b).strip()
    text = re.sub(r'\s+', ' ', text)
    if len(text) > 10:
        print(f"  >> {text[:120]}")

# Extraer h tags (nombres probables)
h_tags = re.findall(r'<h[2-5][^>]*>(.*?)</h[2-5]>', final_html, re.DOTALL)
h_clean = [re.sub(r'<[^>]+>', '', h).strip() for h in h_tags]
h_clean = [h for h in h_clean if 5 < len(h) < 100]
print(f"\nTitulos (h2-h5) encontrados: {h_clean[:30]}")

# Extraer precios
precios = re.findall(r'\$\s*([\d,\.]+)', final_html)
print(f"Precios encontrados: {precios[:20]}")
