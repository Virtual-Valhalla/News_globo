"""
ContentExtractor — Decoupled service for fetching and cleaning article content.
Responsible for: HTTP fetch, HTML parsing, text normalization, multimedia detection.
"""
import re
import logging
import requests
from bs4 import BeautifulSoup
from services.media_parser import media_parser

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

UNWANTED_TAGS = {"script", "style", "nav", "header", "footer", "aside",
                 "form", "button", "noscript", "svg", "figure"}


class ContentExtractor:
    """Fetch a URL and extract clean article data."""

    def extract(self, url: str, timeout: int = 8) -> dict:
        """
        Returns a dict with:
          title, content, resumen, imagen, multimedia, url_original
        """
        try:
            resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
            resp.raise_for_status()
        except requests.exceptions.Timeout:
            logger.warning("⏱️ Timeout al extraer: %s", url)
            return self._error(url, "Timeout al cargar el artículo")
        except requests.exceptions.RequestException as e:
            logger.warning("🔌 Error de red al extraer %s: %s", url, e)
            return self._error(url, f"Error de red: {e}")

        soup = BeautifulSoup(resp.text, "html.parser")
        return {
            "titulo":          self._extract_title(soup),
            "contenido":       self._extract_content(soup),
            "resumen":         self._extract_description(soup),
            "imagen":          self._extract_image(soup),
            "multimedia":      media_parser.parse_soup(soup),
            "url_original":    url,
        }

    # ── Extraction helpers ────────────────────────────────────────────────────

    def _extract_title(self, soup) -> str:
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            return og["content"].strip()
        twitter = soup.find("meta", {"name": "twitter:title"})
        if twitter and twitter.get("content"):
            return twitter["content"].strip()
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        h1 = soup.find("h1")
        return h1.get_text(strip=True) if h1 else "Sin título"

    def _extract_description(self, soup) -> str:
        for attr, name in [("property", "og:description"),
                           ("name", "description"),
                           ("name", "twitter:description")]:
            tag = soup.find("meta", {attr: name})
            if tag and tag.get("content"):
                return tag["content"].strip()
        return ""

    def _extract_image(self, soup) -> str:
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"].strip()
        twitter = soup.find("meta", {"name": "twitter:image"})
        if twitter and twitter.get("content"):
            return twitter["content"].strip()
        img = soup.find("img", src=True)
        return img["src"].strip() if img else ""

    def _extract_content(self, soup) -> str:
        # Remove clutter
        for tag in soup.find_all(UNWANTED_TAGS):
            tag.decompose()

        # Try article body selectors
        article = (
            soup.find("article")
            or soup.find(class_=re.compile(r"article|post|content|entry|body", re.I))
            or soup.find("main")
        )
        target = article or soup

        paragraphs = target.find_all("p")
        text = "\n\n".join(p.get_text(separator=" ", strip=True) for p in paragraphs if p.get_text(strip=True))
        text = self._normalize(text)
        return text[:8000]

    @staticmethod
    def _normalize(text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        return text

    @staticmethod
    def _error(url, message):
        return {
            "titulo":       "Error",
            "contenido":    message,
            "resumen":      "",
            "imagen":       "",
            "multimedia":   [],
            "url_original": url,
        }


content_extractor = ContentExtractor()
