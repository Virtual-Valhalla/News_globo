# NEWS_GLOBO | Terminal V.1 Geo-Scanner

An interactive 3D globe that lets users click any country to view real-time news headlines and summaries, styled as a cyberpunk terminal UI.

## Run & Operate

- **Run**: `python app.py` (dev) or `gunicorn --bind=0.0.0.0:5000 --reuse-port app:app` (prod)
- **Required env vars**: `NEWS_API_KEY` — one or more NewsAPI.org keys, comma-separated for rotation

## Stack

- **Backend**: Python 3.12, Flask 3.1.1
- **Frontend**: Vanilla JS, HTML5, CSS3, Globe.gl (Three.js), GSAP 3
- **Web scraping**: BeautifulSoup4
- **HTTP**: requests 2.32.4
- **Server**: gunicorn (production)

## Where things live

- `app.py` — Flask backend, API proxy, caching, key rotation
- `templates/index.html` — main UI (Jinja2)
- `static/js/app.js` — globe interaction and news logic
- `static/js/intro.js` — GSAP intro animation
- `static/js/globe.gl.min.js`, `static/js/three.min.js` — 3D libraries
- `static/style.css` — neon/cyberpunk theme
- `static/countries.geojson`, `static/ne_50m_admin_0_countries.json` — country geometries
- `requirements.txt` — Python dependencies

## Architecture decisions

- In-memory cache (dict) with per-entry TTL: 6h for countries, 4h for global feed — avoids hitting NewsAPI rate limits on repeated requests
- API key rotation: supports comma-separated `NEWS_API_KEY` values; automatically skips rate-limited keys and resets them after all are exhausted
- Two-tier country lookup: uses `top-headlines?country=` for the 55 natively supported countries, falls back to `everything?q=` for others
- Article scraping is done server-side to avoid CORS issues and expose a clean `/article?url=` endpoint

## Product

- Interactive 3D globe — click any country to fetch its top news
- Category filtering (business, entertainment, health, science, sports, technology)
- Article detail panel with scraped full text and embedded video if available
- Cache and API status endpoints (`/cache-status`, `/api-status`) for monitoring

## User preferences

_Populate as you build_

## Gotchas

- The 3D globe requires WebGL; it renders as a black screen in headless/screenshot environments — this is expected
- `NEWS_API_KEY` must be set as a Replit Secret before news fetching will work
- Multiple keys (comma-separated) are recommended to avoid rate limits

## Pointers

- NewsAPI docs: https://newsapi.org/docs
- Globe.gl docs: https://globe.gl
