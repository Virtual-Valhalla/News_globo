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

NEWS_API_KEY = 'NEWS_API_KEY'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/country-news")
def country_news():
    code = request.args.get("country", "world").lower()
    
    logger.info(f"📡 Solicitud de noticias recibida para: {code}")
    
    try:
        # 🌍 GLOBAL
        if code == "world" or code == "global":
            logger.info("🌍 Modo GLOBAL activado")
            url = f'https://newsapi.org/v2/everything?q=world&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                raise Exception(f"API retornó estado no-ok: {data.get('message', 'Unknown error')}")
            
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
        url = f'https://newsapi.org/v2/top-headlines?country={code}&apiKey={NEWS_API_KEY}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "ok":
            logger.warning(f"⚠️ top-headlines falló: {data.get('message', 'Unknown error')}")
            raise Exception(f"API error en top-headlines: {data.get('message', 'Unknown error')}")
        
        # 🔻 2. Si no hay noticias → fallback
        if not data.get("articles"):
            logger.info(f"🔻 top-headlines sin resultados, activando fallback para: {code}")
            url = f'https://newsapi.org/v2/everything?q={code}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "ok":
                logger.error(f"❌ Fallback también falló: {data.get('message', 'Unknown error')}")
                raise Exception(f"API error en fallback: {data.get('message', 'Unknown error')}")
            
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
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"❌ HTTP ERROR {e.response.status_code}: {str(e)} para {code}"
        logger.error(error_msg)
        
        if e.response.status_code == 401:
            return jsonify({
                "status": "error",
                "type": "auth",
                "message": "Error de autenticación con NewsAPI. Verifica tu API key.",
                "details": error_msg,
                "articles": []
            }), 401
        elif e.response.status_code == 429:
            return jsonify({
                "status": "error",
                "type": "ratelimit",
                "message": "Límite de solicitudes excedido. Intenta más tarde.",
                "details": error_msg,
                "articles": []
            }), 429
        elif e.response.status_code == 404:
            return jsonify({
                "status": "error",
                "type": "not_found",
                "message": f"El código de país '{code}' no es válido o no tiene noticias disponibles.",
                "details": error_msg,
                "articles": []
            }), 404
        else:
            return jsonify({
                "status": "error",
                "type": "http_error",
                "message": "Error al conectar con el servidor de noticias.",
                "details": error_msg,
                "articles": []
            }), e.response.status_code
            
    except ValueError as e:
        error_msg = f"🔧 JSON PARSE ERROR: No se pudo procesar la respuesta para {code}: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "type": "parse",
            "message": "Error al procesar la respuesta del servidor de noticias.",
            "details": error_msg,
            "articles": []
        }), 502
        
    except Exception as e:
        error_msg = f"❌ UNEXPECTED ERROR para {code}: {str(e)} | Tipo: {type(e).__name__}"
        logger.error(error_msg)
        return jsonify({
            "status": "error",
            "type": "unknown",
            "message": "Ocurrió un error inesperado. Por favor, intenta nuevamente más tarde.",
            "details": error_msg,
            "articles": []
        }), 500

if __name__ == "__main__":
    logger.info("🚀 Iniciando servidor News_globo en puerto 5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
