# News Globo

A 3D interactive globe that displays real-time news from around the world, letting users click on countries to browse news filtered by category.

## Run & Operate

- **Flask app**: `cd news_globo && python app.py` — runs on port 5000
- **Seed sources**: `cd news_globo && python seed_sources.py` — populates all news sources with categories
- **pnpm API server**: `pnpm --filter @workspace/api-server run dev` — Node.js API (port 8080)
- Required env: `NEWS_API_KEY` — NewsAPI.org key (comma-separated for rotation). Without it, app runs DB-only mode.

## Stack

- Python 3.11, Flask 3.x, SQLite (WAL mode)
- BeautifulSoup4 + lxml for RSS scraping
- Globe.gl + Three.js for 3D globe frontend
- pnpm workspaces, Node.js 24, TypeScript 5.9 (separate Node API server)

## Where things live

```
news_globo/
  app.py                    — Flask entry point
  models/database.py        — SQLite schema + CRUD (sources + noticias tables)
  seed_sources.py           — Seeds 234 global RSS sources with lang + categoria
  scrapers/rss_scraper.py   — RSS fetch + parse, injects categoria from source
  services/
    content_extractor.py    — Full article fetch: title, content, image, multimedia
    media_parser.py         — Detects YouTube/Vimeo/HTML5 video in HTML
    news_service.py         — NewsAPI integration + in-memory cache
    fetch_service.py        — Concurrent ingestion orchestrator
    scheduler.py            — Auto-fetch every N minutes
  routes/
    api_routes.py           — /country-news (category-filtered), /article
    news_api_routes.py      — REST CRUD for sources/news
  static/js/components/
    terminal.js             — Category UI (arrows + dropdown)
    reader.js               — Article viewer (video > image > no-media priority)
    console.js              — Debug console overlay
  static/css/terminal.css   — All UI styles
```

## Architecture decisions

- **Category stored at source level**: Each RSS source in `seed_sources.py` has a `categoria` field (Spanish). When scraping, articles inherit the source category; if source is "General", category is inferred from the article URL path.
- **DB-first, NewsAPI fallback**: `/country-news` first queries the local SQLite DB (filtered by category, up to 200 results), then fills remaining slots with NewsAPI if available.
- **No 20-article cap**: `get_news()` defaults to `limit=200`. The old hardcoded `limit=20` cap has been removed.
- **Media priority in reader**: Video (YouTube/Vimeo iframe, HTML5) → Image (og:image, twitter:image, RSS media) → "No media" message. Full article text shown below.
- **ContentExtractor for /article**: The `/article` endpoint now uses the richer `ContentExtractor` (og:image, full paragraphs, multimedia detection) instead of the basic legacy extractor.

## Product

- 3D globe with clickable country nodes showing local news
- Category filter (General, Tecnología, Economía, Deportes, Entretenimiento, Salud, Ciencia) with swipe/click navigation
- DATA_DECRYPTOR reader panel with video priority, image fallback, and full article text
- 234 global RSS sources across 15+ languages and 10 category types
- Auto-ingestion scheduler (configurable interval)

## Gotchas

- Run `seed_sources.py` after cloning to populate `categoria` and `lang` in sources table
- After the first scheduler run, `noticias` will have proper `categoria` values on new articles
- Old articles (pre-migration) have `categoria = 'General'` by default
- RSS items inherit category from their source feed; URL-based inference only used for General-category sources

## Pointers

- See the `pnpm-workspace` skill for the Node.js monorepo structure
