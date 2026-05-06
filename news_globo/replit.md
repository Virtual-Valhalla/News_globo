# NEWS_GLOBO | Terminal V.1 Geo-Scanner

An interactive 3D globe that lets users click any country to view real-time news headlines and summaries, styled as a cyberpunk terminal UI.

## Run & Operate

- **Run**: `python app.py` (dev) or `gunicorn --bind=0.0.0.0:5000 --reuse-port app:app` (prod)
- **Required env vars**: `NEWS_API_KEY` — one or more NewsAPI.org keys, comma-separated for rotation
- **GitHub push**: `git push "https://$GITHUB_PERSONAL_ACCESS_TOKEN@github.com/Virtual-Valhalla/News_globo.git" main`

## Stack

- **Backend**: Python 3.12, Flask 3.1.1, Blueprints
- **Frontend**: Vanilla JS (modular), HTML5, Globe.gl (Three.js), GSAP 3
- **Web scraping**: BeautifulSoup4
- **HTTP**: requests 2.32.4
- **Server**: gunicorn (production)

## Where things live

```
app.py                        — Entry point; registers Blueprints
config.py                     — Constants: TTLs, COUNTRY_NAMES, API key builder
services/news_service.py      — Cache, key rotation, fetch_url, scraping
routes/main_routes.py         — Blueprint: GET /
routes/api_routes.py          — Blueprint: /country-news, /article, /cache-*, /api-status
templates/index.html          — Main UI (Jinja2)
static/
  css/main.css                — Base styles, globe, typography, responsive
  css/terminal.css            — Console, terminal, reader, news items, buttons
  js/components/console.js   — logToConsole, clearConsole, toggleConsole
  js/components/terminal.js  — Category selector, toggleTerminal
  js/components/reader.js    — openReader, closeReader, loadArticle
  js/core/globe_engine.js    — Globe init, GeoJSON load, click/hover handlers
  js/app.js                  — selectNode, loadNews, resetToGlobal, onload
  js/intro.js                — GSAP intro animation
  js/shaders/waterDrop.js    — Three.js custom shader (unused/reserved)
  vendor/three.min.js        — Three.js library (local)
  vendor/globe.gl.min.js     — Globe.gl library (local)
  data/                      — GeoJSON country geometry files
requirements.txt             — Python dependencies
```

## Architecture decisions

- Flask Blueprints: `main_bp` for UI, `api_bp` for all data endpoints — clean separation of concerns
- In-memory cache (dict) with per-entry TTL: 6h for countries, 4h for global feed
- API key rotation: comma-separated `NEWS_API_KEY`; auto-skips rate-limited keys
- Two-tier country lookup: `top-headlines?country=` for 55 native countries, `everything?q=` fallback for others
- Article scraping done server-side via `/article?url=` to avoid CORS issues
- JS load order: console → terminal → reader → intro → globe_engine → app (globals cascade)
- Vendor libs served locally (`static/vendor/`) to avoid CDN downtime issues

## Product

- Interactive 3D globe — click any country to fetch its top news
- Category filtering (business, entertainment, health, science, sports, technology)
- Article detail panel with scraped full text and embedded video if available
- Cache and API status endpoints (`/cache-status`, `/api-status`) for monitoring

## User preferences

- Project uses Spanish for UI labels and log messages
- Prefers modular file structure (one responsibility per file)

## Gotchas

- The 3D globe requires WebGL; renders as black in headless/screenshot environments — expected
- `NEWS_API_KEY` must be set as a Replit Secret before news fetching works
- Multiple keys (comma-separated) are recommended to avoid rate limits
- JS files are vanilla globals — load order in `index.html` is significant
- To push to GitHub use `GITHUB_PERSONAL_ACCESS_TOKEN` secret in the push URL (git config is restricted in Replit main agent)

## Pointers

- NewsAPI docs: https://newsapi.org/docs
- Globe.gl docs: https://globe.gl
- GitHub repo: https://github.com/Virtual-Valhalla/News_globo
