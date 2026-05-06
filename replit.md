# NEWS_GLOBO

A cyberpunk-themed 3D interactive globe for monitoring global news in real time, powered by NewsAPI.org and rendered with Globe.gl + Three.js.

## Run & Operate

- **Start**: `python app.py` (port 5000)
- **Required env secrets**: `NEWS_API_KEY` — one or more NewsAPI.org keys, comma-separated (e.g. `key1,key2`)

## Stack

- **Backend**: Python 3.12, Flask 3.1.1
- **Frontend**: HTML5, CSS3, vanilla JavaScript
- **3D Globe**: Globe.gl + Three.js (via CDN)
- **Animations**: GSAP 3 (via CDN)
- **Data**: NewsAPI.org REST API + GeoJSON country borders

## Where things live

- `app.py` — Flask server: routes, in-memory cache, API key rotation
- `templates/index.html` — Main UI (cyberpunk terminal theme)
- `static/style.css` — Neon/cyberpunk styles
- `static/js/app.js` — Globe logic and news loading
- `static/js/intro.js` — GSAP zoom intro animation
- `static/countries.geojson` — Country border data

## Architecture decisions

- In-memory cache with TTL (6h countries, 4h global) to avoid rate-limit exhaustion
- Multiple NewsAPI keys supported with automatic rotation on 429 responses
- Fallback from `top-headlines` to `everything` endpoint for unsupported countries
- Flask serves both the frontend (SSR via Jinja2) and acts as a proxy/backend for NewsAPI

## Product

- Interactive 3D globe — click any country to load its top news
- Cyberpunk terminal UI with NEWS_TERMINAL panel, CONSOLE log, and DATA_DECRYPTOR article reader
- Category filter (business, entertainment, general, health, science, sports, technology)
- Intro zoom animation on first load

## User preferences

_Populate as you build_

## Gotchas

- `NEWS_API_KEY` must be set or the app runs in placeholder mode (no real news)
- Free NewsAPI keys only work on localhost in dev mode; production requires a paid plan

## Pointers

- [NewsAPI docs](https://newsapi.org/docs)
- [Globe.gl docs](https://globe.gl/)
