import time
import logging
import requests
from datetime import datetime, timezone, timedelta
from flask import Blueprint, jsonify, request
import services.news_service as svc
from config import (CACHE_TTL_COUNTRY, CACHE_TTL_GLOBAL,
                    COUNTRY_NAMES, NEWSAPI_COUNTRIES)

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

VALID_CATEGORIES = {'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'}


def _quote_name(country_name):
    """Always wrap in quotes for exact match."""
    return f'"{country_name}"'


def build_everything_tier1(country_name, category=''):
    """
    Tier 1 (specific): country name in title + optional AND category, last 7 days.
    No language filter so local-language articles are included.
    """
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
    """
    Tier 2 (broad): country name only, no searchIn restriction, no language filter,
    last 30 days. Wide net to ensure something is always returned.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%S')
    q = requests.utils.quote(_quote_name(country_name))
    return (
        f'https://newsapi.org/v2/everything'
        f'?q={q}&sortBy=publishedAt&from={since}&pageSize=15&apiKey={{api_key}}'
    )


def fetch_everything_with_fallback(country_name, category=''):
    """
    Tiered fetch for the /everything endpoint.

    Tier 1: "{Country}" [AND category] in title — specific, 7 days.
    Tier 2: "{Country}" anywhere — broad, 30 days, no language filter.

    Falls through to Tier 2 only when Tier 1 returns 0 articles, so most
    supported-category + large-country combos only use 1 API call.
    Returns (articles, scan_tier).
    """
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

        # ── Ruta Global ───────────────────────────────────────────────────────
        if code in ('world', 'global'):
            cat_param = f'&category={category}' if category else ''
            url = (f'https://newsapi.org/v2/top-headlines'
                   f'?language=en&pageSize=15{cat_param}&apiKey={{api_key}}')
            data     = svc.fetch_url(url)
            articles = svc.filter_articles(data.get('articles', []))
            ttl      = CACHE_TTL_GLOBAL

        # ── Ruta A: ISO compatible → top-headlines directo ───────────────────
        elif code in NEWSAPI_COUNTRIES:
            cat_param = f'&category={category}' if category else ''
            url = (f'https://newsapi.org/v2/top-headlines'
                   f'?country={code}&pageSize=15{cat_param}&apiKey={{api_key}}')
            data     = svc.fetch_url(url)
            articles = svc.filter_articles(data.get('articles', []))
            ttl      = CACHE_TTL_COUNTRY

            # Fallback: top-headlines vacío → everything tiered
            if not articles:
                country_name = COUNTRY_NAMES.get(code, code.upper())
                logger.info(f"🔄 top-headlines vacío para '{code}' → everything tiered para '{country_name}'")
                articles, tier = fetch_everything_with_fallback(country_name, category)
                scan_mode = f'deep-scan-t{tier}'

        # ── Ruta C: ISO no compatible → everything tiered ─────────────────────
        else:
            country_name = COUNTRY_NAMES.get(code, code.replace('_', ' ').title())
            logger.info(f"🌍 ISO '{code}' no soportado → Deep-Scan para '{country_name}'")
            articles, tier = fetch_everything_with_fallback(country_name, category)
            scan_mode = f'deep-scan-t{tier}'
            ttl       = CACHE_TTL_COUNTRY

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


@api_bp.route('/article')
def get_article():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Falta URL'}), 400
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
