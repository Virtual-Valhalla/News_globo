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
            return jsonify({'status': 'ok', 'articles': cached['articles'], **info}), 200

    try:
        if code in ('world', 'global'):
            cat_param = f'&category={category}' if category else ''
            url = (f'https://newsapi.org/v2/top-headlines'
                   f'?language=en&pageSize=20{cat_param}&apiKey={{api_key}}')
            ttl = CACHE_TTL_GLOBAL

        elif code in NEWSAPI_COUNTRIES:
            cat_param = f'&category={category}' if category else ''
            url = (f'https://newsapi.org/v2/top-headlines'
                   f'?country={code}&pageSize=20{cat_param}&apiKey={{api_key}}')
            ttl = CACHE_TTL_COUNTRY

        else:
            country_name = COUNTRY_NAMES.get(code, code.replace('_', ' ').title())
            since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
            q_parts = [country_name]
            if category:
                q_parts.append(category)
            q = requests.utils.quote(' '.join(q_parts))
            url = (f'https://newsapi.org/v2/everything'
                   f'?q={q}&sortBy=publishedAt'
                   f'&from={since}&pageSize=20&language=en&apiKey={{api_key}}')
            ttl = CACHE_TTL_COUNTRY

        data     = svc.fetch_url(url)
        articles = svc.filter_articles(data.get('articles', []))

        if not articles and code in NEWSAPI_COUNTRIES:
            country_name = COUNTRY_NAMES.get(code, code)
            since = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%S')
            q_parts = [country_name]
            if category:
                q_parts.append(category)
            q = requests.utils.quote(' '.join(q_parts))
            url = (f'https://newsapi.org/v2/everything'
                   f'?q={q}&sortBy=publishedAt'
                   f'&from={since}&pageSize=20&language=en&apiKey={{api_key}}')
            logger.info(f"🔄 Fallback everything para {code}")
            data     = svc.fetch_url(url)
            articles = svc.filter_articles(data.get('articles', []))

        if not articles:
            label = COUNTRY_NAMES.get(code, code.replace('_', ' ').title())
            return jsonify({
                'status':   'warning',
                'message':  f'No se encontraron noticias para {label} en este momento.',
                'articles': [], 'cached': False,
            }), 200

        svc.cache_set(cache_key, articles, ttl)
        logger.info(f"✅ {cache_key}: {len(articles)} artículos (API fresca)")
        return jsonify({'status': 'ok', 'articles': articles, 'cached': False}), 200

    except requests.exceptions.Timeout:
        logger.error(f"⏱️ TIMEOUT para {code}")
        return jsonify({'status': 'error', 'type': 'timeout',
                        'message': 'Servidor tardó demasiado. Intenta de nuevo.', 'articles': []}), 504
    except requests.exceptions.ConnectionError:
        logger.error(f"🔌 CONNECTION ERROR para {code}")
        return jsonify({'status': 'error', 'type': 'connection',
                        'message': 'Error de conexión con NewsAPI.', 'articles': []}), 503
    except Exception as e:
        logger.error(f"❌ ERROR para {code}: {e}")
        return jsonify({'status': 'error', 'type': 'unknown',
                        'message': 'Error inesperado. Intenta más tarde.',
                        'details': str(e), 'articles': []}), 500


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
