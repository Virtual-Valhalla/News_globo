# NEWS_GLOBO | Terminal V.1 Geo-Scanner

Plataforma de visualización geoespacial con estética **cyberpunk** para el monitoreo de noticias globales en tiempo real. Un globo 3D interactivo donde puedes hacer clic en cualquier país para ver sus últimas noticias.

- **Demo / repo**: [github.com/Virtual-Valhalla/News_globo](https://github.com/Virtual-Valhalla/News_globo)
- **API docs** (local): `http://localhost:5000/docs`

---

## Índice

1. [Requisitos](#requisitos)
2. [Instalación local](#instalación-local)
3. [Configurar la API key](#configurar-la-api-key)
4. [Ejecutar la aplicación](#ejecutar-la-aplicación)
5. [Uso de la interfaz](#uso-de-la-interfaz)
6. [Variables de entorno](#variables-de-entorno)
7. [API REST](#api-rest)
8. [Estructura del proyecto](#estructura-del-proyecto)
9. [Arquitectura](#arquitectura)
10. [Base de datos](#base-de-datos)
11. [Producción](#producción)

---

## Requisitos

- **Python 3.8+** (probado en 3.12)
- **pip**
- API key gratuita de [NewsAPI.org](https://newsapi.org/register) _(opcional — sin ella funciona con la BD local)_
- Navegador con **WebGL** activado (Chrome, Firefox, Edge)

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/Virtual-Valhalla/News_globo.git
cd News_globo
```

### 2. Crear y activar un entorno virtual

**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD)**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Configurar la API key

La API key de [NewsAPI.org](https://newsapi.org/register) permite obtener titulares en tiempo real.
Sin ella, la app sigue funcionando mostrando las noticias de la base de datos local (scrapeadas por el scheduler).

### Opción A — Variable de entorno en la misma línea (recomendada para desarrollo)

**Windows (PowerShell)**
```powershell
$env:NEWS_API_KEY="API_KEY_1,API_KEY_2,API_KEY_3"; python app.py
```

**Windows (CMD)**
```cmd
set NEWS_API_KEY=API_KEY_1,API_KEY_2,API_KEY_3 && python app.py
```

**macOS / Linux**
```bash
NEWS_API_KEY="API_KEY_1,API_KEY_2,API_KEY_3" python app.py
```

### Opción B — Archivo `.env` (persistente entre sesiones)

Crea un archivo `.env` en la raíz del proyecto:

```env
NEWS_API_KEY=API_KEY_1,API_KEY_2,API_KEY_3
```

Luego simplemente ejecuta:

```bash
python app.py
```

> El separador `,` permite configurar múltiples keys. El sistema rota entre ellas automáticamente cuando una alcanza su límite de uso (rate limit), y las resetea cuando todas están agotadas.

---

## Ejecutar la aplicación

### Desarrollo

```bash
python app.py
```

Abre `http://localhost:5000` en el navegador.

### Flujo completo en un solo comando

**Windows (PowerShell)**
```powershell
python -m venv venv; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt; $env:NEWS_API_KEY="TU_API_KEY"; python app.py
```

**macOS / Linux**
```bash
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && NEWS_API_KEY="TU_API_KEY" python app.py
```

---

## Uso de la interfaz

| Acción | Descripción |
|--------|-------------|
| **Click en la pantalla** | Inicia el zoom de entrada desde la vista lejana |
| **Click en un país** | Carga las últimas noticias de ese país |
| **Flechas ◄ ►** | Cambia la categoría (General, Tecnología, Negocios…) |
| **Click en un titular** | Abre el panel DATA_DECRYPTOR con el artículo completo |
| **RESET_CAMERA** | Vuelve a la vista global y carga el feed mundial |
| **Botón −/+** | Colapsa o expande el panel NEWS_TERMINAL o la CONSOLE |

**Paneles de la UI:**
- **NEWS_TERMINAL** — lista de titulares del país seleccionado con selector de categoría
- **CONSOLE** — log en tiempo real con niveles INFO / SUCCESS / WARNING / ERROR / DEBUG
- **DATA_DECRYPTOR** — artículo completo con imagen, video embebido (YouTube/Vimeo) y enlace a la fuente

---

## Variables de entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `NEWS_API_KEY` | API key(s) de NewsAPI.org, separadas por coma | — |
| `PORT` | Puerto del servidor | `5000` |
| `DB_PATH` | Ruta al archivo SQLite | `news_globo.db` (raíz del proyecto) |
| `FETCH_INTERVAL_MINUTES` | Intervalo de ingesta automática (minutos) | `60` |
| `FETCH_INITIAL_DELAY_SECONDS` | Espera antes del primer scraping al arrancar | `30` |

---

## API REST

Todos los endpoints bajo `/v1/` devuelven JSON con el campo `status: "ok"` o `status: "error"`.
Documentación interactiva completa en `http://localhost:5000/docs`.

### Endpoints de mapa (usados por el frontend)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Página principal |
| `GET` | `/country-news?country=XX` | Noticias por código ISO-A2 (ej: `es`, `us`, `mx`) |
| `GET` | `/country-news?country=XX&category=YY` | Noticias filtradas por categoría |
| `GET` | `/article?url=...` | Extrae contenido completo de un artículo externo |
| `GET` | `/cache-status` | Estado del caché en memoria (artículos, TTL, scan_mode) |
| `POST` | `/cache-clear` | Limpia el caché — todo o `?country=XX` |
| `GET` | `/api-status` | Estado y uso de las API keys |
| `POST` | `/reset-api-limits` | Resetea contadores de rate-limit |

### Noticias (`/v1/news`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/v1/news` | Lista noticias — `?source=ID`, `?limit=50`, `?offset=0` |
| `GET` | `/v1/news/<id>` | Detalle — `?full=true` re-extrae contenido en vivo |

### Fuentes (`/v1/sources`)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/v1/sources` | Lista fuentes — `?active=true` solo activas |
| `POST` | `/v1/sources` | Crea fuente: `{"nombre","url","tipo","activa"}` |
| `PUT` | `/v1/sources/<id>` | Actualiza campos de una fuente |
| `DELETE` | `/v1/sources/<id>` | Elimina una fuente |

### Ingesta y scheduler

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/v1/fetch` | Scraping manual — todas las fuentes o `?source_id=X` |
| `GET` | `/v1/scheduler` | Estado del scheduler |
| `POST` | `/v1/scheduler/start` | Arranca ingesta automática |
| `POST` | `/v1/scheduler/stop` | Detiene ingesta automática |
| `POST` | `/v1/scheduler/run-now` | Ejecución inmediata en background |
| `PUT` | `/v1/scheduler/interval` | Cambia intervalo: `{"minutes": 30}` |
| `GET` | `/v1/health` | Healthcheck del servicio |

### Categorías disponibles

`general` · `technology` · `business` · `sports` · `entertainment` · `health` · `science`

---

## Estructura del proyecto

```
News_globo/
├── app.py                      # Punto de entrada: registra Blueprints, arranca scheduler
├── config.py                   # Constantes: TTLs, COUNTRY_NAMES, API key builder
├── requirements.txt            # Dependencias Python
├── seed_sources.py             # Script de utilidad: poblar la BD con fuentes de noticias
│
├── routes/
│   ├── main_routes.py          # Blueprint: GET / — sirve el frontend
│   ├── api_routes.py           # Blueprint: /country-news, /article, /cache-*, /api-status
│   ├── news_api_routes.py      # Blueprint: /v1/* — REST CRUD API
│   └── docs_routes.py          # Blueprint: /docs — documentación interactiva
│
├── services/
│   ├── news_service.py         # Caché, rotación de keys, fetch_url(), filter_articles()
│   ├── content_extractor.py    # Scraper de artículos (título, texto, og:image, media)
│   ├── media_parser.py         # Detector multimedia (YouTube, Vimeo, Twitter, HTML5)
│   ├── fetch_service.py        # Orquestador de ingesta con ThreadPoolExecutor
│   └── scheduler.py            # Daemon thread para auto-ingesta periódica
│
├── scrapers/
│   ├── rss_scraper.py          # Parser RSS/Atom (hasta 30 artículos por feed)
│   └── html_scraper.py         # Scraper HTML (hasta 10 artículos por fuente)
│
├── models/
│   └── database.py             # Capa SQLite: init, migraciones, CRUD
│
├── templates/
│   └── index.html              # Página principal (Jinja2)
│
└── static/
    ├── css/
    │   ├── main.css            # Estilos base, globo, tipografía, responsive
    │   └── terminal.css        # Consola, terminal, lector, noticias, botones
    ├── js/
    │   ├── components/
    │   │   ├── console.js      # logToConsole, clearConsole, toggleConsole
    │   │   ├── terminal.js     # Selector de categorías, dropdown, swipe, toggleTerminal
    │   │   └── reader.js       # openReader, closeReader (DATA_DECRYPTOR)
    │   ├── core/
    │   │   └── globe_engine.js # Init Globe.gl, GeoJSON, eventos click/hover
    │   ├── app.js              # selectNode, loadNews, resetToGlobal, window.onload
    │   └── intro.js            # Animación de intro con GSAP (zoom + punto pulsante)
    └── vendor/
        ├── three.min.js        # Three.js (copia local — sin dependencia de CDN)
        └── globe.gl.min.js     # Globe.gl (copia local — sin dependencia de CDN)
```

---

## Arquitectura

### Backend

- **Flask Blueprints**: `main_bp` (UI) · `api_bp` (mapa) · `news_api_bp` (REST v1) · `docs_bp` (docs)
- **Caché en memoria**: dict con TTL por entrada — 6 h para países, 4 h para feed global; lazy expiry
- **Rotación de API keys**: salta automáticamente las que alcanzan el rate limit; resetea cuando todas están agotadas
- **Estrategia de fetch**:
  1. Caché en memoria → si HIT, devuelve inmediatamente
  2. BD local → artículos scrapeados por el scheduler
  3. NewsAPI `top-headlines` → para 55 países con soporte nativo
  4. NewsAPI `everything` tier 1 → búsqueda en título (7 días) para países sin soporte
  5. NewsAPI `everything` tier 2 → búsqueda amplia (30 días) como último recurso (Deep-Scan)
- **Scraping**: BeautifulSoup4 + lxml; CORS resuelto server-side vía `/article?url=`
- **Scheduler**: daemon thread; primer fetch a los 30 s del arranque, luego cada 60 min

### Frontend

- **Carga modular**: `console.js → terminal.js → reader.js → intro.js → globe_engine.js → app.js`
  (orden crítico — cada archivo expone globals usados por el siguiente)
- **Globe.gl + Three.js**: servidos localmente en `static/vendor/` para evitar dependencias de CDN
- **GeoJSON**: cargado desde GitHub CDN en tiempo real (177 países, Natural Earth 110m)
- **GSAP 3**: animación de intro desde CDN (`cdnjs.cloudflare.com`)

### Base de datos

SQLite con modo **WAL** y migraciones automáticas al arrancar (seguras: comprueba existencia de columnas antes de `ALTER TABLE`).

Tablas principales:
- `fuentes` — fuentes de noticias (`nombre`, `url`, `tipo`, `activa`)
- `noticias` — artículos (`titulo`, `resumen`, `contenido`, `imagen`, `multimedia`, `categoria`, `fecha_publicacion`, `fuente_id`)

---

## Producción

```bash
gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 app:app
```

Con variable de entorno:

**Linux / macOS**
```bash
NEWS_API_KEY="key1,key2,key3" gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 app:app
```

**Windows (PowerShell)**
```powershell
$env:NEWS_API_KEY="key1,key2,key3"; gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 app:app
```

---

## Stack tecnológico

| Capa | Tecnología | Versión |
|------|-----------|---------|
| Backend | Python + Flask (Blueprints) | 3.12 / 3.1.1 |
| Base de datos | SQLite (WAL mode) | — |
| Scraping | BeautifulSoup4, lxml, requests | 4.14.3 / — / 2.32.4 |
| Frontend | Vanilla JS modular, HTML5, CSS3 | — |
| Globo 3D | Globe.gl + Three.js (local) | — |
| Animaciones | GSAP 3 (CDN) | — |
| Servidor prod | Gunicorn | — |

---

## Autor

**Virtual-Valhalla** — [github.com/Virtual-Valhalla](https://github.com/Virtual-Valhalla)

---

## Recursos

- [NewsAPI docs](https://newsapi.org/docs)
- [Globe.gl docs](https://globe.gl)
- [Three.js docs](https://threejs.org/docs)
- [GSAP docs](https://gsap.com/docs)
- [Flask docs](https://flask.palletsprojects.com)
