from flask import Flask, render_template, jsonify, request
import requests
import logging
from datetime import datetime

app = Flask(__name__)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 🔑 LISTA DE API KEYS CON GESTIÓN DE LÍMITES
API_KEYS = [
    {'key': 'fghjfghdfgh', 'requests_used': 0, 'rate_limited': False},
    {'key': 'fghjfghdfgh', 'requests_used': 0, 'rate_limited': False},
]
current_api_index = 0
MAX_RETRIES = 99

def get_next_available_key():
    """Obtiene la siguiente API key disponible (no rate-limited)"""
    global current_api_index
    
    # Primero intenta la actual si no está rate-limited
    if not API_KEYS[current_api_index]['rate_limited']:
        logger.info(f"🔑 Usando API Key #{current_api_index + 1}")
        return API_KEYS[current_api_index]['key'], current_api_index
    
    # Si la actual está rate-limited, busca la siguiente disponible
    for attempt in range(len(API_KEYS)):
        current_api_index = (current_api_index + 1) % len(API_KEYS)
        if not API_KEYS[current_api_index]['rate_limited']:
            logger.info(f"🔄 Rotando a API Key #{current_api_index + 1}")
            return API_KEYS[current_api_index]['key'], current_api_index
    
    # Si todas están rate-limited, resetea el estado y usa la primera
    logger.warning("⚠️ Todas las keys estaban rate-limited. Reseteando estado...")
    for key_obj in API_KEYS:
        key_obj['rate_limited'] = False
    current_api_index = 0
    return API_KEYS[current_api_index]['key'], current_api_index

def mark_rate_limited(index):
    """Marca una API key como rate-limited"""
    API_KEYS[index]['rate_limited'] = True
    logger.warning(f"⚠️ API Key #{index + 1} marcada como rate-limited")

def increment_api_usage(index):
    """Incrementa el contador de solicitudes"""
    API_KEYS[index]['requests_used'] += 1

def log_api_status():
    """Log del estado de todas las keys"""
    status = " | ".join([
        f"Key {i+1}: {k['requests_used']} requests {'🚫 RATE-LIMITED' if k['rate_limited'] else '✅'}" 
        for i, k in enumerate(API_KEYS)
    ])
    logger.info(f"📊 Estado de API Keys: {status}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api-status")
def api_status():
    """Endpoint para verificar el estado de las API Keys"""
    status = {
        "current_key_index": current_api_index,
        "keys": [
            {
                "index": i,
                "requests_used": k['requests_used'],
                "rate_limited": k['rate_limited'],
            }
            for i, k in enumerate(API_KEYS)
        ]
    }
    return jsonify(status), 200

def fetch_news_with_retry(url_template, country_code, max_retries=MAX_RETRIES):
    """
    Intenta obtener noticias con retry automático en caso de 429.
    Rota entre API keys hasta encontrar una disponible.
    """
    for attempt in range(max_retries):
        try:
            api_key, key_index = get_next_available_key()
            url = url_template.format(api_key=api_key)
            
            logger.info(f"📨 Intento {attempt + 1}/{max_retries} con API Key #{key_index + 1}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            increment_api_usage(key_index)
            
            if data.get("status") != "ok":
                raise Exception(f"API retornó estado no-ok: {data.get('message', 'Unknown error')}")
            
            return data, key_index
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                logger.warning(f"🚫 429 Too Many Requests en Key #{key_index + 1}")
                mark_rate_limited(key_index)
                
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Reintentando con siguiente API key...")
                    continue
                else:
                    logger.critical("❌ Se agotaron todos los reintentos con todas las API keys")
                    raise Exception("Todas las API Keys están rate-limited")
            else:
                raise
        
        except requests.exceptions.Timeout:
            raise
        except requests.exceptions.ConnectionError:
            raise
        except Exception as e:
            raise

@app.route("/country-news")
def country_news():
    code = request.args.get("country", "world").lower()
    
    logger.info(f"📡 Solicitud de noticias recibida para: {code}")
    log_api_status()
    
    try:
        # 🌍 GLOBAL
        if code == "world" or code == "global":
            logger.info("🌍 Modo GLOBAL activado")
            url_template = 'https://newsapi.org/v2/everything?q=world&sortBy=publishedAt&apiKey={api_key}'
            
            try:
                data, key_index = fetch_news_with_retry(url_template, code)
            except Exception as e:
                if "rate-limited" in str(e).lower():
                    return jsonify({
                        "status": "error",
                        "type": "ratelimit",
                        "message": "Todas las API keys están rate-limited. Por favor, intenta en unos minutos.",
                        "articles": []
                    }), 429
                raise
            
            if not data.get("articles"):
                logger.warning("⚠️ GLOBAL: No se encontraron artículos")
                return jsonify({
                    "status": "warning",
                    "message": "No se encontraron noticias en este momento para el feed global",
                    "articles": []
                }), 200
            
            logger.info(f"✅ GLOBAL: {len(data.get('articles', []))} artículos encontrados")
            return jsonify(data), 200
        
        # 🔹 1. Intento con top-headlines
        logger.info(f"🔹 Intentando top-headlines para país: {code}")
        url_template = 'https://newsapi.org/v2/top-headlines?country={code}&apiKey={{api_key}}'
        url_template = url_template.format(code=code)
        
        try:
            data, key_index = fetch_news_with_retry(url_template, code)
        except Exception as e:
            if "rate-limited" in str(e).lower():
                return jsonify({
                    "status": "error",
                    "type": "ratelimit",
                    "message": "Todas las API keys están rate-limited. Por favor, intenta en unos minutos.",
                    "articles": []
                }), 429
            logger.warning(f"⚠️ top-headlines falló: {str(e)}")
            raise Exception(f"API error en top-headlines: {str(e)}")
        
        # 🔻 2. Si no hay noticias → fallback
        if not data.get("articles"):
            logger.info(f"🔻 top-headlines sin resultados, activando fallback para: {code}")
            url_template = 'https://newsapi.org/v2/everything?q={code}&sortBy=publishedAt&apiKey={{api_key}}'
            url_template = url_template.format(code=code)
            
            try:
                data, key_index = fetch_news_with_retry(url_template, code)
            except Exception as e:
                if "rate-limited" in str(e).lower():
                    return jsonify({
                        "status": "error",
                        "type": "ratelimit",
                        "message": "Todas las API keys están rate-limited. Por favor, intenta en unos minutos.",
                        "articles": []
                    }), 429
                logger.error(f"❌ Fallback también falló: {str(e)}")
                raise
            
            if not data.get("articles"):
                logger.warning(f"⚠️ Fallback: No se encontraron artículos para {code}")
                return jsonify({
                    "status": "warning",
                    "message": f"No se encontraron noticias para {code.upper()} en este momento. Intenta más tarde.",
                    "articles": []
                }), 200
        
        logger.info(f"✅ {code.upper()}: {len(data.get('articles', []))} artículos encontrados")
        return jsonify(data), 200
        
    except requests.exceptions.Timeout:
        error_msg = f"⏱️ TIMEOUT: La solicitud a NewsAPI tardó demasiado tiempo para {code}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "type": "timeout",
            "message": "El servidor tardó demasiado en responder. Por favor, intenta nuevamente.",
            "details": error_msg,
            "articles": []
        }), 504
        
    except requests.exceptions.ConnectionError:
        error_msg = f"🔌 CONNECTION ERROR: No se pudo conectar a NewsAPI para {code}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "type": "connection",
            "message": "Error de conexión con el servidor de noticias. Verifica tu conexión a internet.",
            "details": error_msg,
            "articles": []
        }), 503
        
    except Exception as e:
        error_msg = f"❌ ERROR para {code}: {str(e)} | Tipo: {type(e).__name__}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "type": "unknown",
            "message": "Ocurrió un error inesperado. Por favor, intenta nuevamente más tarde.",
            "details": error_msg,
            "articles": []
        }), 500

@app.route("/reset-api-limits", methods=['POST'])
def reset_limits():
    """Endpoint para resetear los límites (solo para administración)"""
    for key_obj in API_KEYS:
        key_obj['requests_used'] = 0
        key_obj['rate_limited'] = False
    logger.info("✅ Límites de API Keys reseteados")
    return jsonify({
        "status": "success", 
        "message": "Límites reseteados",
        "keys_info": [
            {
                "index": i,
                "requests_used": k['requests_used'],
                "rate_limited": k['rate_limited']
            }
            for i, k in enumerate(API_KEYS)
        ]
    }), 200

if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor News_globo en puerto 5000")
    logger.info(f"🔑 Configuradas {len(API_KEYS)} API Keys")
    log_api_status()
    app.run(host="0.0.0.0", port=5000, debug=True)