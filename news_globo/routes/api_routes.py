import time
import logging
import requests
from datetime import datetime, timezone, timedelta
from flask import Blueprint, jsonify, request
import services.news_service as svc
from config import (CACHE_TTL_COUNTRY, CACHE_TTL_GLOBAL,
                    COUNTRY_NAMES, NEWSAPI_COUNTRIES)
from models import database as db
from services.content_extractor import content_extractor

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

VALID_CATEGORIES = {'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'}

# Map from NewsAPI category names (English) to Spanish DB categories
CATEGORY_MAP = {
    'technology':     'Tecnología',
    'business':       'Economía',
    'sports':         'Deportes',
    'entertainment':  'Entretenimiento',
    'health':         'Salud',
    'science':        'Ciencia',
    'politics':       'Política',
    'general':        'General',
    '':               None,  # no filter
}


def _quote_name(country_name):
    """Always wrap in quotes for exact match."""
    return f'"{country_name}"'


def build_everything_tier1(country_name, category=''):
    since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
    base  = _quote_name(country_name)
    if category and category != 'general':
        term = f'{base} AND {category}'
    else:
        term = base
    q = requests.utils.quote(term)
    return (
        f'https://newsapi.org/v2/everything'
        f'?q={q}&searchIn=title&sortBy=publishedAt&from={since}&pageSize=15&apiKey={{api_key}}'
    )


def build_everything_tier2(country_name):
    since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S')
    q = requests.utils.quote(_quote_name(country_name))
    return (
        f'https://newsapi.org/v2/everything'
        f'?q={q}&sortBy=publishedAt&from={since}&pageSize=15&apiKey={{api_key}}'
    )


def fetch_everything_with_fallback(country_name, category=''):
    url1 = build_everything_tier1(country_name, category)
    data = svc.fetch_url(url1)
    articles = svc.filter_articles(data.get('articles', []))
    if articles:
        return articles, 1
    logger.info(
        f"⬇️ Tier 1 vacío para '{country_name}' [{category}] → "
        f"Tier 2: búsqueda amplia 30 días sin filtro de idioma"
    )
    url2 = build_everything_tier2(country_name)
    data = svc.fetch_url(url2)
    articles = svc.filter_articles(data.get('articles', []))
    return articles, 2


def get_db_news_by_country(country_code, category='', limit=200):
    """
    Fetch news from DB.
    - category: English NewsAPI name ('technology', 'sports', etc.) — mapped to Spanish DB value.
    - No artificial cap: limit defaults to 200.
    """
    try:
        # Map English API category to Spanish DB category
        db_categoria = CATEGORY_MAP.get(category, None) if category else None

        news_items = db.get_news(categoria=db_categoria, limit=limit)

        articles = []
        for item in news_items:
            articles.append({
                'title':       item.get('titulo', 'Sin título'),
                'description': item.get('resumen') or item.get('contenido', ''),
                'url':         item.get('url_original', ''),
                'urlToImage':  item.get('imagen') or None,
                'imagen':      item.get('imagen') or None,
                'publishedAt': item.get('fecha_publicacion'),
                'source':      {'id': None, 'name': item.get('source_name', 'BD Local')},
                'content':     item.get('contenido', ''),
                'categoria':   item.get('categoria', 'General'),
                'db_source':   True,
            })

        logger.info(f"📚 BD: {len(articles)} noticias para '{country_code}' [cat={db_categoria}]")
        return articles
    except Exception as e:
        logger.warning(f"⚠️ Error al consultar BD: {e}")
        return []


@api_bp.route('/country-news')
def country_news():
    code     = request.args.get('country',  'world').lower().strip()
    category = request.args.get('category', '').lower().strip()
    force    = request.args.get('force',    '').lower() == 'true'

    if category not in VALID_CATEGORIES:
        category = ''

    cache_key = f"{code}:{category}" if category else code
    logger.info(f"📡 Solicitud para: '{code}' cat='{category}' force={force}")

    if not force:
        cached = svc.cache_get(cache_key)
        if cached:
            info = svc.cache_entry_info(cached)
            return jsonify({
                'status':    'ok',
                'articles':  cached['articles'],
                'scan_mode': cached.get('scan_mode', 'direct'),
                **info,
            }), 200

    try:
        scan_mode = 'direct'
        articles = []

        # ── PASO 1: BD (scraping) — filtrada por categoría, sin límite artificial ──
        db_articles = get_db_news_by_country(code, category=category, limit=200)
        if db_articles:
            articles.extend(db_articles)
            scan_mode = 'database-primary'
            logger.info(f"✅ BD para '{code}' cat='{category}': {len(db_articles)} artículos")

        # ── PASO 2: Complementa con NewsAPI si no hay suficientes ──────────────────
        try:
            api_articles = None
            ttl = CACHE_TTL_COUNTRY

            if code in ('world', 'global'):
                cat_param = f'&category={category}' if category else ''
                url = (f'https://newsapi.org/v2/top-headlines'
                       f'?language=en&pageSize=15{cat_param}&apiKey={{api_key}}')
                data         = svc.fetch_url(url)
                api_articles = svc.filter_articles(data.get('articles', []))
                ttl          = CACHE_TTL_GLOBAL
                if articles:
                    scan_mode = 'database-global-hybrid'

            elif code in NEWSAPI_COUNTRIES:
                cat_param = f'&category={category}' if category else ''
                url = (f'https://newsapi.org/v2/top-headlines'
                       f'?country={code}&pageSize=15{cat_param}&apiKey={{api_key}}')
                data         = svc.fetch_url(url)
                api_articles = svc.filter_articles(data.get('articles', []))
                ttl          = CACHE_TTL_COUNTRY
                if not api_articles:
                    country_name = COUNTRY_NAMES.get(code, code.upper())
                    logger.info(f"🔄 top-headlines vacío → everything tiered para '{country_name}'")
                    api_articles, tier = fetch_everything_with_fallback(country_name, category)
                    scan_mode = f'database-deep-scan-t{tier}' if articles else f'deep-scan-t{tier}'

            else:
                country_name = COUNTRY_NAMES.get(code, code.replace('_', ' ').title())
                logger.info(f"🌍 ISO '{code}' no soportado → Deep-Scan para '{country_name}'")
                api_articles, tier = fetch_everything_with_fallback(country_name, category)
                scan_mode = f'database-deep-scan-t{tier}' if articles else f'deep-scan-t{tier}'

            if api_articles:
                if len(articles) < 15:
                    articles.extend(api_articles[:15 - len(articles)])
                    if scan_mode == 'database-primary':
                        scan_mode = 'database-api-hybrid'

        except Exception as e:
            logger.warning(f"⚠️ Error al obtener noticias de API: {e}")
            if articles:
                logger.info(f"✅ Continuando solo con noticias de BD ({len(articles)} artículos)")
            else:
                raise

        # ── RESULTADO FINAL ────────────────────────────────────────────────────────
        if not articles:
            label = COUNTRY_NAMES.get(code, code.replace('_', ' ').title())
            return jsonify({
                'status':    'warning',
                'message':   f'Sin noticias disponibles para {label}.',
                'articles':  [],
                'cached':    False,
                'scan_mode': scan_mode,
            }), 200

        svc.cache_set(cache_key, articles, ttl, scan_mode=scan_mode)
        logger.info(f"✅ {cache_key}: {len(articles)} artículos [{scan_mode}]")
        return jsonify({
            'status':    'ok',
            'articles':  articles,
            'cached':    False,
            'scan_mode': scan_mode,
        }), 200

    except requests.exceptions.Timeout:
        logger.error(f"⏱️ TIMEOUT para {code}")
        return jsonify({'status': 'error', 'type': 'timeout',
                        'message': 'Servidor tardó demasiado. Intenta de nuevo.',
                        'articles': [], 'scan_mode': 'error'}), 504
    except requests.exceptions.ConnectionError:
        logger.error(f"🔌 CONNECTION ERROR para {code}")
        return jsonify({'status': 'error', 'type': 'connection',
                        'message': 'Error de conexión con NewsAPI.',
                        'articles': [], 'scan_mode': 'error'}), 503
    except Exception as e:
        logger.error(f"❌ ERROR para {code}: {e}")
        return jsonify({'status': 'error', 'type': 'unknown',
                        'message': 'Error inesperado. Intenta más tarde.',
                        'details': str(e), 'articles': [],
                        'scan_mode': 'error'}), 500


def _db_fallback(url: str) -> dict | None:
    """
    Return article data from the local DB (clean RSS content, no scraping errors).
    Returns None if the article isn't in the DB.
    """
    stored = db.get_news_by_url(url)
    if not stored:
        return None
    contenido = stored.get("contenido") or stored.get("resumen") or ""
    return {
        "titulo":       stored.get("titulo", ""),
        "contenido":    contenido,
        "resumen":      stored.get("resumen", ""),
        "imagen":       stored.get("imagen", ""),
        "multimedia":   stored.get("multimedia", []),
        "url_original": url,
        "_source":      "db",
    }


@api_bp.route('/article')
def get_article():
    """
    Extracts full article content, media, and image.
    Priority:
      1. Live scrape via ContentExtractor (og:image, full paragraphs, multimedia)
      2. DB fallback — clean RSS content stored at ingest time (no scraping errors)
    Response: titulo, contenido, resumen, imagen, multimedia (list), url_original
    """
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Falta URL'}), 400

    try:
        data = content_extractor.extract(url)

        # If extraction was blocked (403/timeout/etc.), fall back to DB content
        if data.get("_blocked") or not data.get("contenido"):
            if data.get("_blocked"):
                logger.info("🔄 Extracción bloqueada → usando contenido de BD para %s", url)
            fallback = _db_fallback(url)
            if fallback:
                # Keep better image/multimedia from live fetch if available
                if not data.get("imagen"):
                    data["imagen"] = fallback["imagen"]
                if not data.get("multimedia"):
                    data["multimedia"] = fallback["multimedia"]
                data["contenido"] = fallback["contenido"]
                data["resumen"]   = data["resumen"] or fallback["resumen"]
                data["titulo"]    = data["titulo"]  or fallback["titulo"]
            data.pop("_blocked", None)

        data.pop("_blocked", None)
        return jsonify(data)

    except Exception as e:
        logger.warning("⚠️ Error extrayendo artículo %s: %s", url, e)
        fallback = _db_fallback(url)
        if fallback:
            return jsonify(fallback)
        return jsonify(svc.extract_article(url))


@api_bp.route('/cache-status')
def cache_status():
    now = time.time()
    entries = []
    for key, entry in svc._cache.items():
        remaining = max(0, entry['expires_at'] - now)
        h, rem = divmod(int(remaining), 3600)
        m = rem // 60
        entries.append({
            'country':    key,
            'articles':   len(entry['articles']),
            'cached_at':  datetime.fromtimestamp(entry['cached_at'], tz=timezone.utc).isoformat(),
            'expires_in': f"{h}h {m}m",
            'ttl_hours':  entry['ttl'] // 3600,
            'scan_mode':  entry.get('scan_mode', 'direct'),
        })
    entries.sort(key=lambda x: x['country'])
    total_requests = sum(k['requests_used'] for k in svc.API_KEYS)
    return jsonify({
        'cached_countries':   len(entries),
        'total_api_requests': total_requests,
        'entries': entries,
        'api_keys': [
            {'index': i + 1, 'requests_used': k['requests_used'],
             'rate_limited': k['rate_limited']}
            for i, k in enumerate(svc.API_KEYS)
        ],
    }), 200


@api_bp.route('/cache-clear', methods=['POST'])
def cache_clear():
    country = request.args.get('country')
    if country:
        removed = svc._cache.pop(country.lower(), None)
        msg = f"Caché de '{country}' eliminado" if removed else f"'{country}' no estaba en caché"
    else:
        count = len(svc._cache)
        svc._cache.clear()
        msg = f"{count} entradas de caché eliminadas"
    logger.info(f"🗑️  {msg}")
    return jsonify({'status': 'success', 'message': msg}), 200


@api_bp.route('/api-status')
def api_status():
    return jsonify({
        'current_key_index': svc.current_api_index,
        'keys': [
            {'index': i, 'requests_used': k['requests_used'], 'rate_limited': k['rate_limited']}
            for i, k in enumerate(svc.API_KEYS)
        ],
    }), 200


@api_bp.route('/reset-api-limits', methods=['POST'])
def reset_limits():
    for key_obj in svc.API_KEYS:
        key_obj['requests_used'] = 0
        key_obj['rate_limited'] = False
    return jsonify({'status': 'success', 'message': 'Límites reseteados'}), 200
