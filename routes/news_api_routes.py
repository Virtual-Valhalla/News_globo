"""
News API REST Routes — the new robust API layer.

Endpoints:
  GET  /v1/news              — list news (filterable by ?source=)
  GET  /v1/news/<id>         — single news detail
  GET  /v1/sources           — list all sources
  POST /v1/sources           — create a source
  PUT  /v1/sources/<id>      — update a source
  DELETE /v1/sources/<id>    — delete a source
  POST /v1/fetch             — trigger ingestion (all or ?source_id=)
  GET  /v1/scheduler         — scheduler status
  POST /v1/scheduler/start   — start automatic ingestion
  POST /v1/scheduler/stop    — stop automatic ingestion
  POST /v1/scheduler/run-now — trigger immediate run
  PUT  /v1/scheduler/interval — change interval (minutes)
"""
import logging
from flask import Blueprint, jsonify, request
from models import database as db
from services.fetch_service import fetch_all_sources, fetch_source_by_id
from services.content_extractor import content_extractor
from services.scheduler import scheduler

logger = logging.getLogger(__name__)

news_api_bp = Blueprint("news_api", __name__, url_prefix="/v1")

_in_memory_cache = {}


def _ok(data, status=200):
    return jsonify({"status": "ok", **data}), status


def _error(message, status=400, **extra):
    return jsonify({"status": "error", "message": message, **extra}), status


# ── News endpoints ────────────────────────────────────────────────────────────

@news_api_bp.route("/news", methods=["GET"])
def list_news():
    source_id = request.args.get("source")
    limit = min(int(request.args.get("limit", 50)), 100)
    offset = int(request.args.get("offset", 0))

    source_id_int = None
    if source_id:
        try:
            source_id_int = int(source_id)
        except ValueError:
            return _error("Parámetro 'source' debe ser un entero")

    news = db.get_news(source_id=source_id_int, limit=limit, offset=offset)
    return _ok({"news": news, "count": len(news), "offset": offset, "limit": limit})


@news_api_bp.route("/news/<int:news_id>", methods=["GET"])
def get_news(news_id):
    item = db.get_news_by_id(news_id)
    if not item:
        return _error("Noticia no encontrada", 404)

    # Optionally enrich with full content extraction on demand
    fetch_full = request.args.get("full", "").lower() == "true"
    if fetch_full and item.get("url_original"):
        extracted = content_extractor.extract(item["url_original"])
        item["contenido"]  = extracted.get("contenido") or item.get("contenido")
        item["multimedia"] = extracted.get("multimedia") or item.get("multimedia", [])

    return _ok({"news": item})


# ── Sources endpoints ─────────────────────────────────────────────────────────

@news_api_bp.route("/sources", methods=["GET"])
def list_sources():
    only_active = request.args.get("active", "").lower() == "true"
    sources = db.get_all_sources(only_active=only_active)
    return _ok({"sources": sources, "count": len(sources)})


@news_api_bp.route("/sources", methods=["POST"])
def create_source():
    body = request.get_json(silent=True) or {}
    nombre = (body.get("nombre") or "").strip()
    url    = (body.get("url")    or "").strip()
    tipo   = (body.get("tipo")   or "rss").strip().lower()
    activa = body.get("activa", True)

    if not nombre:
        return _error("El campo 'nombre' es obligatorio")
    if not url:
        return _error("El campo 'url' es obligatorio")
    if tipo not in ("rss", "scraping", "api"):
        return _error("El campo 'tipo' debe ser 'rss', 'scraping' o 'api'")

    try:
        source = db.create_source(nombre, url, tipo, activa)
        return _ok({"source": source}, 201)
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            return _error(f"Ya existe una fuente con la URL: {url}", 409)
        logger.error("❌ Error al crear fuente: %s", e)
        return _error(str(e), 500)


@news_api_bp.route("/sources/<int:source_id>", methods=["PUT"])
def update_source(source_id):
    if not db.get_source_by_id(source_id):
        return _error("Fuente no encontrada", 404)

    body = request.get_json(silent=True) or {}
    allowed = {}
    if "nombre" in body:
        allowed["nombre"] = str(body["nombre"]).strip()
    if "url" in body:
        allowed["url"] = str(body["url"]).strip()
    if "tipo" in body:
        t = str(body["tipo"]).strip().lower()
        if t not in ("rss", "scraping", "api"):
            return _error("El campo 'tipo' debe ser 'rss', 'scraping' o 'api'")
        allowed["tipo"] = t
    if "activa" in body:
        allowed["activa"] = 1 if body["activa"] else 0

    updated = db.update_source(source_id, **allowed)
    return _ok({"source": updated})


@news_api_bp.route("/sources/<int:source_id>", methods=["DELETE"])
def delete_source(source_id):
    if not db.get_source_by_id(source_id):
        return _error("Fuente no encontrada", 404)
    db.delete_source(source_id)
    return _ok({"message": f"Fuente {source_id} eliminada"})


# ── Fetch/ingestion endpoint ──────────────────────────────────────────────────

@news_api_bp.route("/fetch", methods=["POST"])
def trigger_fetch():
    source_id = request.args.get("source_id") or (request.get_json(silent=True) or {}).get("source_id")

    if source_id:
        try:
            source_id = int(source_id)
        except (ValueError, TypeError):
            return _error("'source_id' debe ser un entero")
        result = fetch_source_by_id(source_id)
        if result is None:
            return _error("Fuente no encontrada", 404)
        return _ok({"result": result})
    else:
        summary = fetch_all_sources(only_active=True)
        return _ok({"summary": summary})


# ── Scheduler endpoints ───────────────────────────────────────────────────────

@news_api_bp.route("/scheduler", methods=["GET"])
def scheduler_status():
    return _ok({"scheduler": scheduler.status()})


@news_api_bp.route("/scheduler/start", methods=["POST"])
def scheduler_start():
    scheduler.start()
    return _ok({"scheduler": scheduler.status(), "message": "Scheduler iniciado"})


@news_api_bp.route("/scheduler/stop", methods=["POST"])
def scheduler_stop():
    scheduler.stop()
    return _ok({"scheduler": scheduler.status(), "message": "Scheduler detenido"})


@news_api_bp.route("/scheduler/run-now", methods=["POST"])
def scheduler_run_now():
    scheduler.run_now()
    return _ok({"message": "Ingesta manual lanzada en background"})


@news_api_bp.route("/scheduler/interval", methods=["PUT"])
def scheduler_interval():
    body = request.get_json(silent=True) or {}
    minutes = body.get("minutes")
    if minutes is None:
        return _error("Campo 'minutes' requerido (entero, mínimo 1)")
    try:
        minutes = int(minutes)
    except (ValueError, TypeError):
        return _error("'minutes' debe ser un entero")
    if minutes < 1:
        return _error("El intervalo mínimo es 1 minuto")
    scheduler.set_interval(minutes)
    return _ok({"scheduler": scheduler.status(), "message": f"Intervalo actualizado a {minutes} min"})


# ── Healthcheck ───────────────────────────────────────────────────────────────

@news_api_bp.route("/health", methods=["GET"])
def health():
    return _ok({"service": "news-globo-api", "version": "2.1", "scheduler": scheduler.status()})
