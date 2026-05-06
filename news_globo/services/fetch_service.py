"""
FetchService — Orchestrates ingestion from all active sources.
Dispatches to RssScraper or HtmlScraper based on source type.
Runs each source in a thread pool for concurrency.
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.database import get_all_sources, upsert_news
from scrapers.rss_scraper import scrape_rss
from scrapers.html_scraper import scrape_html

logger = logging.getLogger(__name__)

MAX_WORKERS = 5


def fetch_all_sources(only_active=True):
    """
    Fetch news from all (active) sources concurrently.
    Returns summary dict with counts per source.
    """
    sources = get_all_sources(only_active=only_active)
    if not sources:
        logger.warning("⚠️ No hay fuentes configuradas")
        return {"total_sources": 0, "total_inserted": 0, "results": []}

    results = []
    total_inserted = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_source = {
            executor.submit(_fetch_source, src): src
            for src in sources
        }
        for future in as_completed(future_to_source):
            src = future_to_source[future]
            try:
                fetched, inserted, error = future.result()
                total_inserted += inserted
                results.append({
                    "source_id":   src["id"],
                    "source_name": src["nombre"],
                    "tipo":        src["tipo"],
                    "fetched":     fetched,
                    "inserted":    inserted,
                    "error":       error,
                })
            except Exception as e:
                results.append({
                    "source_id":   src["id"],
                    "source_name": src["nombre"],
                    "tipo":        src["tipo"],
                    "fetched":     0,
                    "inserted":    0,
                    "error":       str(e),
                })

    logger.info("🏁 Ingesta completa: %d nuevos artículos de %d fuentes",
                total_inserted, len(sources))
    return {
        "total_sources":  len(sources),
        "total_inserted": total_inserted,
        "results":        results,
    }


def fetch_source_by_id(source_id):
    """Fetch from a single source by ID."""
    from models.database import get_source_by_id
    source = get_source_by_id(source_id)
    if not source:
        return None, 0, "Fuente no encontrada"
    fetched, inserted, error = _fetch_source(source)
    return {
        "source_id":   source["id"],
        "source_name": source["nombre"],
        "tipo":        source["tipo"],
        "fetched":     fetched,
        "inserted":    inserted,
        "error":       error,
    }


def _fetch_source(source):
    """Dispatch to the correct scraper and upsert results. Returns (fetched, inserted, error)."""
    tipo = source.get("tipo", "rss").lower()
    try:
        if tipo == "rss":
            articles = scrape_rss(source)
        elif tipo == "scraping":
            articles = scrape_html(source)
        else:
            logger.warning("⚠️ Tipo desconocido '%s' para fuente %s", tipo, source["nombre"])
            articles = []

        if not articles:
            return 0, 0, None

        inserted = upsert_news(articles)
        return len(articles), inserted, None

    except Exception as e:
        logger.error("❌ Error en fuente '%s': %s", source["nombre"], e)
        return 0, 0, str(e)
