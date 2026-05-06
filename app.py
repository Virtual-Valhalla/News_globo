import os
import logging
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from routes.main_routes import main_bp
from routes.api_routes import api_bp
from routes.news_api_routes import news_api_bp
from routes.docs_routes import docs_bp
import services.news_service as svc
from models.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

init_db()

app.register_blueprint(main_bp)
app.register_blueprint(api_bp)
app.register_blueprint(news_api_bp)
app.register_blueprint(docs_bp)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Iniciando News_globo en puerto {port}")
    logger.info(f"🔑 {len(svc.API_KEYS)} API Key(s) configuradas")
    logger.info(f"⚡ Caché: 6h países | 4h global")
    logger.info(f"📡 REST API disponible en /api/")
    app.run(host='0.0.0.0', port=port, debug=False)
