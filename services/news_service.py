import time
import logging
import requests
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from config import COUNTRY_NAMES, NEWSAPI_COUNTRIES, build_api_keys

logger = logging.getLogger(__name__)

# ── In-memory cache ───────────────────────────────────────────────────────────
_cache = {}

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
        'cached':     True,
        'cached_at':  datetime.fromtimestamp(entry['cached_at'], tz=timezone.utc).isoformat(),
        'expires_in': f"{h}h {m}m",
    }

# ── API key rotation ──────────────────────────────────────────────────────────
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

# ── HTTP fetch with key rotation ─────────────────────────────────────────────
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

# ── Article scraping ──────────────────────────────────────────────────────────
def extract_video(soup):
    for iframe in soup.find_all('iframe'):
        src = iframe.get('src', '')
        if 'youtube.com/embed/' in src or 'youtu.be/' in src:
            if 'autoplay' not in src:
                src += ('&' if '?' in src else '?') + 'autoplay=0'
            return {'type': 'youtube', 'url': src}
    og = soup.find('meta', property='og:video')
    if og and og.get('content'):
        return {'type': 'video', 'url': og['content']}
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
        return {'title': title, 'content': content[:5000], 'video': video}
    except Exception as e:
        return {'title': 'Error', 'content': f'No se pudo cargar: {str(e)}',
                'video': {'type': None, 'url': None}}
