"""
HtmlScraper — Scrapes news articles from HTML pages.
Extracts article links from an index page, then fetches each one.
"""
import logging
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from services.content_extractor import content_extractor

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
}

MAX_ARTICLES_PER_SOURCE = 10


def _is_article_link(href, base_url):
    """Heuristic: skip navigation, home, social, and anchor links."""
    if not href or href.startswith("#") or href.startswith("javascript:"):
        return False
    skip_patterns = (
        "/tag/", "/category/", "/author/", "/page/",
        "/about", "/contact", "/privacy", "/terms",
        "twitter.com", "facebook.com", "instagram.com",
        "youtube.com", "whatsapp", "mailto:"
    )
    for pat in skip_patterns:
        if pat in href:
            return False
    # Must look like a full article URL (has path depth >= 2)
    from urllib.parse import urlparse
    parsed = urlparse(href)
    path_depth = len([p for p in parsed.path.split("/") if p])
    return path_depth >= 2


def _absolute_url(href, base_url):
    from urllib.parse import urljoin
    return urljoin(base_url, href)


def scrape_html(source: dict, max_articles: int = MAX_ARTICLES_PER_SOURCE) -> list:
    """
    Scrape an HTML source page and extract articles.
    Returns list of normalized news dicts.
    """
    url = source["url"]
    source_id = source["id"]
    logger.info("🔎 HTML scrape: %s", url)

    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=12)
        resp.raise_for_status()
    except Exception as e:
        logger.error("❌ Error fetching HTML index %s: %s", url, e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    seen = set()

    for a in soup.find_all("a", href=True):
        href = _absolute_url(a["href"], url)
        if href not in seen and _is_article_link(href, url):
            seen.add(href)
            links.append(href)
        if len(links) >= max_articles * 3:
            break

    articles = []
    for link in links[:max_articles]:
        try:
            data = content_extractor.extract(link, timeout=8)
            if not data.get("titulo") or data["titulo"] in ("Error", "Sin título"):
                continue
            data["fuente_id"] = source_id
            data["fecha_publicacion"] = datetime.now(timezone.utc).isoformat()
            articles.append(data)
        except Exception as e:
            logger.warning("⚠️ Error extrayendo %s: %s", link, e)
            continue

    logger.info("✅ HTML %s → %d artículos", url, len(articles))
    return articles
