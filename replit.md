# NEWS_GLOBO | Terminal V.1 Geo-Scanner

Globo 3D interactivo con estética cyberpunk para monitoreo de noticias globales en tiempo real.
Haz clic en cualquier país para ver sus últimas noticias con filtrado por categoría y lector de artículos completo.

---

## Ejecutar en Replit

### Comando de inicio

```
python app.py
```

El servidor arranca en el puerto `5000`. El preview del navegador se abre automáticamente.

### Para producción (Deploy)

```
gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 app:app
```

---

## Importar este proyecto en Replit

1. Ve a [replit.com](https://replit.com) → **Create Repl** → **Import from GitHub**
2. Pega la URL: `https://github.com/Virtual-Valhalla/News_globo`
3. Selecciona **Python** como lenguaje
4. Replit detectará automáticamente el `requirements.txt` e instalará las dependencias
5. Configura el Secret `NEWS_API_KEY` (ver sección siguiente)
6. Haz clic en **Run** — el workflow `Start application` ejecuta `python app.py`

---

## Secrets (variables de entorno)

En Replit, **nunca uses `.env`**. Usa siempre la sección **Secrets** del panel lateral (icono de candado).

| Secret | Descripción | Obligatorio |
|--------|-------------|-------------|
| `NEWS_API_KEY` | API key(s) de [NewsAPI.org](https://newsapi.org/register), separadas por `,` | No — sin ella funciona con la BD local |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Token PAT para hacer push a GitHub | Solo si usas git push |

**Cómo añadir un Secret:**
1. Panel lateral → icono de candado (Secrets)
2. Key: `NEWS_API_KEY`
3. Value: `key1,key2,key3`
4. Guardar → la variable estará disponible al reiniciar el servidor

> Con múltiples keys separadas por coma, el sistema rota automáticamente entre ellas al alcanzar el rate limit.

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12, Flask 3.1.1, Blueprints |
| Base de datos | SQLite (WAL mode, migraciones automáticas al arrancar) |
| Scraping | BeautifulSoup4, lxml, requests 2.32.4 |
| Frontend | Vanilla JS (modular), HTML5, CSS3 |
| Globo 3D | Globe.gl + Three.js (servidos localmente desde `static/vendor/`) |
| Animaciones | GSAP 3 (CDN: `cdnjs.cloudflare.com`) |
| Servidor prod | Gunicorn |

---

## Estructura de archivos

```
app.py                         — Punto de entrada: Blueprints + scheduler
config.py                      — Constantes: TTLs, COUNTRY_NAMES, API key builder
requirements.txt               — Dependencias Python
seed_sources.py                — Utilidad: poblar la BD con fuentes RSS/HTML

routes/
  main_routes.py               — GET / (sirve el frontend)
  api_routes.py                — /country-news, /article, /cache-*, /api-status
  news_api_routes.py           — /v1/* (REST CRUD API completo)
  docs_routes.py               — /docs (documentación interactiva)

services/
  news_service.py              — Caché, rotación de keys, fetch_url, filter_articles
  content_extractor.py         — Scraper completo (título, texto, og:image, multimedia)
  media_parser.py              — Detector multimedia (YouTube, Vimeo, Twitter, HTML5)
  fetch_service.py             — Orquestador de ingesta con ThreadPoolExecutor
  scheduler.py                 — Daemon thread para auto-ingesta cada 60 min

scrapers/
  rss_scraper.py               — Parser RSS/Atom (hasta 30 artículos por feed)
  html_scraper.py              — Scraper HTML (hasta 10 artículos por fuente)

models/
  database.py                  — SQLite: init, migraciones seguras, CRUD

templates/
  index.html                   — UI principal (Jinja2)

static/
  css/main.css                 — Estilos base, globo, tipografía, responsive
  css/terminal.css             — Consola, terminal, lector, noticias, botones
  js/components/console.js     — logToConsole, clearConsole, toggleConsole
  js/components/terminal.js    — Selector de categorías, dropdown, swipe, toggleTerminal
  js/components/reader.js      — openReader, closeReader (panel DATA_DECRYPTOR)
  js/core/globe_engine.js      — Init Globe.gl, GeoJSON desde CDN, click/hover
  js/app.js                    — selectNode, loadNews, resetToGlobal, window.onload
  js/intro.js                  — Animación GSAP: zoom de entrada + punto pulsante
  vendor/three.min.js          — Three.js (copia local)
  vendor/globe.gl.min.js       — Globe.gl (copia local)
```

---

## Arquitectura

- **Blueprints**: `main_bp` (UI) · `api_bp` (mapa) · `news_api_bp` (REST v1) · `docs_bp` (docs)
- **Caché**: dict en memoria con TTL por entrada — 6 h países, 4 h global; lazy expiry
- **Estrategia de fetch** (por orden de prioridad):
  1. Caché en memoria
  2. BD local (artículos del scheduler)
  3. NewsAPI `top-headlines` (55 países nativos)
  4. NewsAPI `everything` tier 1 — búsqueda en título 7 días (Deep-Scan)
  5. NewsAPI `everything` tier 2 — búsqueda amplia 30 días (Deep-Scan fallback)
- **JS load order**: `console → terminal → reader → intro → globe_engine → app` (globals en cascada — orden crítico)
- **GeoJSON**: cargado en runtime desde GitHub CDN (177 países, Natural Earth 110m) — requiere internet
- **SQLite**: WAL mode, migraciones automáticas con `column-existence check` antes de `ALTER TABLE`

---

## Endpoints principales

| Ruta | Descripción |
|------|-------------|
| `/` | Aplicación principal |
| `/docs` | Documentación interactiva de la REST API |
| `/country-news?country=XX` | Noticias por código ISO (`es`, `us`, `mx`…) |
| `/v1/health` | Healthcheck |
| `/v1/scheduler` | Estado del scheduler |
| `/cache-status` | Estado del caché en memoria |
| `/api-status` | Uso y estado de las API keys |

---

## Preferencias del proyecto

- Código, logs y comentarios en **español**
- Estructura modular — un archivo, una responsabilidad
- Docstrings a nivel de módulo + comentarios inline en todos los archivos fuente

---

## Gotchas

- El globo 3D requiere **WebGL** — aparece negro en entornos headless (esperado)
- `NEWS_API_KEY` debe configurarse como Secret de Replit (nunca en `.env` ni en el código)
- El GeoJSON se carga desde GitHub CDN — requiere conexión a internet en el primer render
- La animación de intro necesita `cdnjs.cloudflare.com` (GSAP desde CDN)
- El orden de carga de los JS en `index.html` es significativo — no reordenar
- `loadArticle()` en `reader.js` es código legacy inactivo — el visor activo es `openReader()`
- Para push a GitHub: usar `GITHUB_PERSONAL_ACCESS_TOKEN` en la URL (git config restringido en Replit)

---

## Recursos

- [NewsAPI docs](https://newsapi.org/docs)
- [Globe.gl docs](https://globe.gl)
- [GitHub repo](https://github.com/Virtual-Valhalla/News_globo)
- [Flask docs](https://flask.palletsprojects.com)
