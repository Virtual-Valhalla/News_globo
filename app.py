import os
import logging
from flask import Flask
from routes.main_routes import main_bp
from routes.api_routes import api_bp
import services.news_service as svc

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Iniciando News_globo en puerto {port}")
    logger.info(f"🔑 {len(svc.API_KEYS)} API Key(s) configuradas")
    logger.info(f"⚡ Caché: 6h países | 4h global")
    app.run(host='0.0.0.0', port=port, debug=False)
