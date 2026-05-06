from flask import Flask, render_template, jsonify, request
import requests
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  CACHÉ EN MEMORIA
#  Estructura: { code: { articles, cached_at, expires_at } }
# ─────────────────────────────────────────────
_cache = {}
CACHE_TTL_COUNTRY = 6 * 3600   # 6 horas para países
CACHE_TTL_GLOBAL  = 4 * 3600   # 4 horas para global

def cache_get(key):
    entry = _cache.get(key)
    if not entry:
        return None
    if time.time() > entry['expires_at']:
        del _cache[key]
        logger.info(f"🗑️  Caché expirado para: {key}")
        return None
    age_min = int((time.time() - entry['cached_at']) / 60)
    logger.info(f"⚡ Caché HIT para '{key}' (edad: {age_min} min)")
    return entry

def cache_set(key, articles, ttl):
    now = time.time()
    _cache[key] = {
        'articles':   articles,
        'cached_at':  now,
        'expires_at': now + ttl,
        'ttl':        ttl,
    }
    logger.info(f"💾 Caché guardado para '{key}' (TTL: {ttl // 3600}h)")

def cache_entry_info(entry):
    remaining = max(0, entry['expires_at'] - time.time())
    h, m = divmod(int(remaining), 3600)
    m //= 60
    return {
        'cached':      True,
        'cached_at':   datetime.fromtimestamp(entry['cached_at'], tz=timezone.utc).isoformat(),
        'expires_in':  f"{h}h {m}m",
    }

# ─────────────────────────────────────────────
#  MAPA DE PAÍSES (código → nombre completo)
# ─────────────────────────────────────────────
COUNTRY_NAMES = {
    "ae": "United Arab Emirates", "ar": "Argentina", "at": "Austria",
    "au": "Australia", "be": "Belgium", "bg": "Bulgaria", "br": "Brazil",
    "ca": "Canada", "ch": "Switzerland", "cn": "China", "co": "Colombia",
    "cu": "Cuba", "cz": "Czech Republic", "de": "Germany", "eg": "Egypt",
    "fr": "France", "gb": "United Kingdom", "gr": "Greece", "hk": "Hong Kong",
    "hu": "Hungary", "id": "Indonesia", "ie": "Ireland", "il": "Israel",
    "in": "India", "it": "Italy", "jp": "Japan", "kr": "South Korea",
    "lt": "Lithuania", "lv": "Latvia", "ma": "Morocco", "mx": "Mexico",
    "my": "Malaysia", "ng": "Nigeria", "nl": "Netherlands", "no": "Norway",
    "nz": "New Zealand", "ph": "Philippines", "pl": "Poland", "pt": "Portugal",
    "ro": "Romania", "rs": "Serbia", "ru": "Russia", "sa": "Saudi Arabia",
    "se": "Sweden", "sg": "Singapore", "si": "Slovenia", "sk": "Slovakia",
    "th": "Thailand", "tr": "Turkey", "tw": "Taiwan", "ua": "Ukraine",
    "us": "United States", "ve": "Venezuela", "za": "South Africa",
    "es": "Spain", "pe": "Peru", "cl": "Chile", "ec": "Ecuador",
    "bo": "Bolivia", "py": "Paraguay", "uy": "Uruguay", "pa": "Panama",
    "cr": "Costa Rica", "gt": "Guatemala", "hn": "Honduras", "sv": "El Salvador",
    "ni": "Nicaragua", "do": "Dominican Republic", "pr": "Puerto Rico",
    "ke": "Kenya", "gh": "Ghana", "et": "Ethiopia", "tz": "Tanzania",
    "ug": "Uganda", "dz": "Algeria", "tn": "Tunisia", "ly": "Libya",
    "sd": "Sudan", "cm": "Cameroon", "ci": "Ivory Coast", "sn": "Senegal",
    "zw": "Zimbabwe", "zm": "Zambia", "mz": "Mozambique", "mg": "Madagascar",
    "ao": "Angola", "cd": "Congo", "pk": "Pakistan", "bd": "Bangladesh",
    "lk": "Sri Lanka", "np": "Nepal", "mm": "Myanmar", "vn": "Vietnam",
    "kh": "Cambodia", "la": "Laos", "af": "Afghanistan", "ir": "Iran",
    "iq": "Iraq", "sy": "Syria", "jo": "Jordan", "lb": "Lebanon",
    "om": "Oman", "kw": "Kuwait", "qa": "Qatar", "bh": "Bahrain",
    "ye": "Yemen", "fi": "Finland", "dk": "Denmark", "ee": "Estonia",
    "by": "Belarus", "md": "Moldova", "ge": "Georgia", "am": "Armenia",
    "az": "Azerbaijan", "kz": "Kazakhstan", "uz": "Uzbekistan",
    "al": "Albania", "ba": "Bosnia", "hr": "Croatia", "mk": "North Macedonia",
    "me": "Montenegro", "mt": "Malta", "cy": "Cyprus", "is": "Iceland",
    "lu": "Luxembourg", "li": "Liechtenstein", "mc": "Monaco", "ad": "Andorra",
    "sm": "San Marino", "va": "Vatican", "nk": "North Korea", "so": "Somalia",
    "mr": "Mauritania", "ml": "Mali", "bf": "Burkina Faso", "ne": "Niger",
    "td": "Chad", "cf": "Central African Republic", "rw": "Rwanda",
    "bi": "Burundi", "er": "Eritrea", "dj": "Djibouti",
}

# Países con soporte nativo en top-headlines de NewsAPI
NEWSAPI_COUNTRIES = {
    "ae","ar","at","au","be","bg","br","ca","ch","cn","co","cu","cz",
    "de","eg","fr","gb","gr","hk","hu","id","ie","il","in","it","jp",
    "kr","lt","lv","ma","mx","my","ng","nl","no","nz","ph","pl","pt",
    "ro","rs","ru","sa","se","sg","si","sk","th","tr","tw","ua","us","ve","za"
}

# ─────────────────────────────────────────────
#  API KEYS CON ROTACIÓN
# ─────────────────────────────────────────────
def build_api_keys():
    keys = []
    raw = os.environ.get("NEWS_API_KEY", "")
    for k in raw.split(","):
        k = k.strip()
        if k:
            keys.append({'key': k, 'requests_used': 0, 'rate_limited': False})
    if not keys:
        logger.warning("⚠️ No NEWS_API_KEY encontrada.")
        keys.append({'key': 'PLACEHOLDER', 'requests_used': 0, 'rate_limited': False})
    return keys

API_KEYS = build_api_keys()
current_api_index = 0

def get_next_available_key():
    global current_api_index
    if not API_KEYS[current_api_index]['rate_limited']:
        return API_KEYS[current_api_index]['key'], current_api_index
    for _ in range(len(API_KEYS)):
        current_api_index = (current_api_index + 1) % len(API_KEYS)
        if not API_KEYS[current_api_index]['rate_limited']:
            logger.info(f"🔄 Rotando a API Key #{current_api_index + 1}")
            return API_KEYS[current_api_index]['key'], current_api_index
    for key_obj in API_KEYS:
        key_obj['rate_limited'] = False
    current_api_index = 0
    return API_KEYS[current_api_index]['key'], current_api_index

def mark_rate_limited(index):
    API_KEYS[index]['rate_limited'] = True
    logger.warning(f"⚠️ API Key #{index + 1} marcada como rate-limited")

def increment_usage(index):
    API_KEYS[index]['requests_used'] += 1

def fetch_url(url_template, max_retries=len(API_KEYS) * 2):
    for attempt in range(max_retries):
        api_key, idx = get_next_available_key()
        url = url_template.replace('{api_key}', api_key)
        try:
            logger.info(f"📨 Fetch intento {attempt + 1} → {url.split('apiKey')[0]}...")
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            increment_usage(idx)
            if data.get('status') != 'ok':
                raise Exception(f"API error: {data.get('message', 'unknown')}")
            return data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                mark_rate_limited(idx)
                if attempt < max_retries - 1:
                    continue
                raise Exception("Todas las API Keys están rate-limited")
            raise
        except Exception:
            raise

def filter_articles(articles):
    valid = []
    for a in articles:
        if (a.get('title') and
                a['title'] != '[Removed]' and
                a.get('url') and
                a.get('source', {}).get('name') != '[Removed]'):
            valid.append(a)
    return valid

# ─────────────────────────────────────────────
#  RUTAS
# ─────────────────────────────────────────────
@app.route('/')
def index():
    resp = app.make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    return resp

VALID_CATEGORIES = {'business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'}

@app.route('/country-news')
def country_news():
    code     = request.args.get('country',  'world').lower().strip()
    category = request.args.get('category', '').lower().strip()
    force    = request.args.get('force',    '').lower() == 'true'

    if category not in VALID_CATEGORIES:
        category = ''

    cache_key = f"{code}:{category}" if category else code
    logger.info(f"📡 Solicitud para: '{code}' cat='{category}' force={force}")

    # ── Caché hit ──────────────────────────────
    if not force:
        cached = cache_get(cache_key)
        if cached:
            info = cache_entry_info(cached)
            return jsonify({'status': 'ok', 'articles': cached['articles'], **info}), 200

    # ── Fetch desde la API ─────────────────────
    try:
        if code in ('world', 'global'):
            # Global: top-headlines sin país. Si hay categoría, añadirla.
            cat_param = f'&category={category}' if category else ''
            url = (f'https://newsapi.org/v2/top-headlines'
                   f'?language=en&pageSize=20{cat_param}&apiKey={{api_key}}')
            ttl = CACHE_TTL_GLOBAL

        elif code in NEWSAPI_COUNTRIES:
            # Top-headlines por país (el más preciso).
            # Categoría sólo aplica en top-headlines.
            cat_param = f'&category={category}' if category else ''
            url = (f'https://newsapi.org/v2/top-headlines'
                   f'?country={code}&pageSize=20{cat_param}&apiKey={{api_key}}')
            ttl = CACHE_TTL_COUNTRY

        else:
            # País sin soporte nativo: buscar por nombre en cualquier campo.
            # Ventana de 7 días, sin restricción de campo, ordenar por fecha.
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

        data     = fetch_url(url)
        articles = filter_articles(data.get('articles', []))

        # Si top-headlines de país devuelve vacío → fallback everything (7 días, sin searchIn)
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
            data     = fetch_url(url)
            articles = filter_articles(data.get('articles', []))

        if not articles:
            label = COUNTRY_NAMES.get(code, code.replace('_', ' ').title())
            return jsonify({
                'status':   'warning',
                'message':  f'No se encontraron noticias para {label} en este momento.',
                'articles': [], 'cached': False,
            }), 200

        cache_set(cache_key, articles, ttl)
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

@app.route('/cache-status')
def cache_status():
    now = time.time()
    entries = []
    for key, entry in _cache.items():
        remaining = max(0, entry['expires_at'] - now)
        h, rem = divmod(int(remaining), 3600)
        m = rem // 60
        entries.append({
            'country':      key,
            'articles':     len(entry['articles']),
            'cached_at':    datetime.fromtimestamp(entry['cached_at'], tz=timezone.utc).isoformat(),
            'expires_in':   f"{h}h {m}m",
            'ttl_hours':    entry['ttl'] // 3600,
        })
    entries.sort(key=lambda x: x['country'])
    total_requests = sum(k['requests_used'] for k in API_KEYS)
    return jsonify({
        'cached_countries': len(entries),
        'total_api_requests': total_requests,
        'entries': entries,
        'api_keys': [
            {'index': i + 1, 'requests_used': k['requests_used'],
             'rate_limited': k['rate_limited']}
            for i, k in enumerate(API_KEYS)
        ],
    }), 200

@app.route('/cache-clear', methods=['POST'])
def cache_clear():
    country = request.args.get('country')
    if country:
        removed = _cache.pop(country.lower(), None)
        msg = f"Caché de '{country}' eliminado" if removed else f"'{country}' no estaba en caché"
    else:
        count = len(_cache)
        _cache.clear()
        msg = f"{count} entradas de caché eliminadas"
    logger.info(f"🗑️  {msg}")
    return jsonify({'status': 'success', 'message': msg}), 200

@app.route('/api-status')
def api_status():
    return jsonify({
        'current_key_index': current_api_index,
        'keys': [
            {'index': i, 'requests_used': k['requests_used'], 'rate_limited': k['rate_limited']}
            for i, k in enumerate(API_KEYS)
        ],
    }), 200

@app.route('/reset-api-limits', methods=['POST'])
def reset_limits():
    for key_obj in API_KEYS:
        key_obj['requests_used'] = 0
        key_obj['rate_limited'] = False
    return jsonify({'status': 'success', 'message': 'Límites reseteados'}), 200

def extract_video(soup):
    """
    Intenta extraer un video embebible de la página:
    1. YouTube <iframe>
    2. og:video meta
    3. <video src=...>
    Devuelve dict con 'type' ('youtube'|'video'|None) y 'url'.
    """
    # 1 ── YouTube iframe
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src', '')
        if 'youtube.com/embed/' in src or 'youtu.be/' in src:
            # Asegurar que no tenga autoplay problemático
            if 'autoplay' not in src:
                src += ('&' if '?' in src else '?') + 'autoplay=0'
            return {'type': 'youtube', 'url': src}

    # 2 ── og:video
    og = soup.find('meta', property='og:video')
    if og and og.get('content'):
        return {'type': 'video', 'url': og['content']}

    # 3 ── <video> tag
    vid = soup.find('video')
    if vid:
        src = vid.get('src') or (vid.find('source') or {}).get('src', '')
        if src:
            return {'type': 'video', 'url': src}

    return {'type': None, 'url': None}


def extract_article(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/124.0 Safari/537.36'
        }
        r = requests.get(url, headers=headers, timeout=6)
        soup = BeautifulSoup(r.text, 'html.parser')
        title   = soup.title.string if soup.title else 'Sin título'
        content = '\n'.join(p.get_text() for p in soup.find_all('p'))
        video   = extract_video(soup)
        return {
            'title':   title,
            'content': content[:5000],
            'video':   video,
        }
    except Exception as e:
        return {'title': 'Error', 'content': f'No se pudo cargar: {str(e)}',
                'video': {'type': None, 'url': None}}


@app.route('/article')
def get_article():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Falta URL'}), 400
    return jsonify(extract_article(url))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Iniciando News_globo en puerto {port}")
    logger.info(f"🔑 {len(API_KEYS)} API Key(s) configuradas")
    logger.info(f"⚡ Caché: {CACHE_TTL_COUNTRY // 3600}h países | {CACHE_TTL_GLOBAL // 3600}h global")
    app.run(host='0.0.0.0', port=port, debug=False)
