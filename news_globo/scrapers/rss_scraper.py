"""
RssScraper — Fetches and parses RSS/Atom feeds.
Returns normalized article dicts ready for upsert_news().
"""
import logging
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from services.media_parser import media_parser

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NewsGloboBot/1.0)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


def _parse_date(date_str):
    """Try to parse common RSS date formats."""
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).isoformat()
        except (ValueError, TypeError):
            continue
    return date_str


def _extract_image_from_item(item):
    """Try several image sources from an RSS item element."""
    # <media:content> or <media:thumbnail>
    for tag in ("media:content", "media:thumbnail"):
        el = item.find(tag)
        if el and el.get("url"):
            return el["url"]

    # <enclosure>
    enc = item.find("enclosure")
    if enc and enc.get("type", "").startswith("image"):
        return enc.get("url", "")

    # og:image inside description HTML
    desc = item.find("description")
    if desc:
        html = desc.get_text()
        soup = BeautifulSoup(html, "html.parser")
        img = soup.find("img", src=True)
        if img:
            return img["src"]

    return ""


def _infer_categoria_from_url(url: str) -> str:
    """
    Try to infer category from the article URL path.
    Returns a Spanish category name or 'General'.
    """
    url_lower = url.lower()
    mapping = {
        "technology": "Tecnología",
        "tech": "Tecnología",
        "science": "Ciencia",
        "health": "Salud",
        "sport": "Deportes",
        "sports": "Deportes",
        "business": "Economía",
        "economy": "Economía",
        "finance": "Economía",
        "money": "Economía",
        "entertainment": "Entretenimiento",
        "culture": "Entretenimiento",
        "arts": "Entretenimiento",
        "politics": "Política",
        "world": "General",
        "news": "General",
        "environment": "Medio Ambiente",
        "climate": "Medio Ambiente",
        "security": "Ciberseguridad",
        "cyber": "Ciberseguridad",
    }
    for keyword, categoria in mapping.items():
        if f"/{keyword}" in url_lower or f"/{keyword}/" in url_lower:
            return categoria
    return "General"


def scrape_rss(source: dict) -> list:
    """
    Fetch and parse an RSS feed.
    Returns list of normalized news dicts with 'categoria' field.
    The category comes from the source record; if missing it tries
    to infer it from each article's URL.
    """
    url = source["url"]
    source_id = source["id"]
    # Category defined at source level (from seed_sources.py)
    source_categoria = source.get("categoria") or "General"
    logger.info("📡 RSS fetch: %s [cat: %s]", url, source_categoria)

    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=12)
        resp.raise_for_status()
    except Exception as e:
        logger.error("❌ Error fetching RSS %s: %s", url, e)
        return []

    soup = BeautifulSoup(resp.content, "xml")
    items = soup.find_all("item") or soup.find_all("entry")

    articles = []
    for item in items[:30]:
        try:
            # Title
            title_tag = item.find("title")
            titulo = title_tag.get_text(strip=True) if title_tag else ""
            if not titulo:
                continue

            # URL
            link_tag = item.find("link")
            if link_tag and link_tag.string:
                url_original = link_tag.string.strip()
            elif link_tag and link_tag.get("href"):
                url_original = link_tag["href"].strip()
            else:
                url_original = ""

            # Category: use source-level if available, otherwise infer from URL
            if source_categoria and source_categoria != "General":
                categoria = source_categoria
            else:
                categoria = _infer_categoria_from_url(url_original) if url_original else "General"

            # Description / summary
            desc_tag = item.find("description") or item.find("summary")
            raw_desc = desc_tag.get_text(strip=True) if desc_tag else ""
            desc_soup = BeautifulSoup(raw_desc, "html.parser")
            resumen = desc_soup.get_text(separator=" ", strip=True)[:500]

            # Full content
            content_tag = (
                item.find("content:encoded")
                or item.find("content")
                or item.find("description")
            )
            raw_content = content_tag.get_text(strip=True) if content_tag else resumen
            content_soup = BeautifulSoup(raw_content, "html.parser")
            contenido = content_soup.get_text(separator="\n", strip=True)[:6000]

            # Image
            imagen = _extract_image_from_item(item)

            # Date
            date_tag = item.find("pubDate") or item.find("published") or item.find("updated")
            fecha = _parse_date(date_tag.get_text(strip=True) if date_tag else None)

            # Multimedia from description/content HTML
            multimedia = media_parser.parse_text(raw_content)

            articles.append({
                "titulo":            titulo,
                "contenido":         contenido,
                "resumen":           resumen,
                "imagen":            imagen,
                "fecha_publicacion": fecha,
                "fuente_id":         source_id,
                "url_original":      url_original,
                "multimedia":        multimedia,
                "categoria":         categoria,
            })
        except Exception as e:
            logger.warning("⚠️ Error parsing RSS item: %s", e)
            continue

    logger.info("✅ RSS %s → %d artículos", url, len(articles))
    return articles
