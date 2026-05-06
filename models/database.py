import sqlite3
import json
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "news_globo.db"))


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sources (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre      TEXT    NOT NULL,
                url         TEXT    NOT NULL UNIQUE,
                tipo        TEXT    NOT NULL DEFAULT 'rss',
                activa      INTEGER NOT NULL DEFAULT 1,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS noticias (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo           TEXT,
                contenido        TEXT,
                resumen          TEXT,
                imagen           TEXT,
                fecha_publicacion TEXT,
                fuente_id        INTEGER REFERENCES sources(id) ON DELETE SET NULL,
                url_original     TEXT UNIQUE,
                multimedia       TEXT DEFAULT '[]',
                created_at       TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_noticias_fuente  ON noticias(fuente_id);
            CREATE INDEX IF NOT EXISTS idx_noticias_fecha   ON noticias(fecha_publicacion DESC);
            CREATE INDEX IF NOT EXISTS idx_sources_activa   ON sources(activa);
        """)
        _seed_sources(conn)
    logger.info("✅ Base de datos inicializada en %s", DB_PATH)


def _seed_sources(conn):
    defaults = [
        ("BBC News (RSS)",      "http://feeds.bbci.co.uk/news/rss.xml",             "rss"),
        ("Reuters (RSS)",       "https://feeds.reuters.com/reuters/topNews",          "rss"),
        ("Al Jazeera (RSS)",    "https://www.aljazeera.com/xml/rss/all.xml",         "rss"),
        ("CNN (RSS)",           "http://rss.cnn.com/rss/edition.rss",                "rss"),
        ("El País (RSS)",       "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "rss"),
    ]
    existing = conn.execute("SELECT url FROM sources").fetchall()
    existing_urls = {r["url"] for r in existing}
    for nombre, url, tipo in defaults:
        if url not in existing_urls:
            conn.execute(
                "INSERT OR IGNORE INTO sources (nombre, url, tipo, activa) VALUES (?,?,?,1)",
                (nombre, url, tipo)
            )


# ── Sources CRUD ──────────────────────────────────────────────────────────────

def get_all_sources(only_active=False):
    with get_db() as conn:
        q = "SELECT * FROM sources"
        if only_active:
            q += " WHERE activa = 1"
        q += " ORDER BY id"
        rows = conn.execute(q).fetchall()
        return [dict(r) for r in rows]


def get_source_by_id(source_id):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
        return dict(row) if row else None


def create_source(nombre, url, tipo="rss", activa=True):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO sources (nombre, url, tipo, activa) VALUES (?,?,?,?)",
            (nombre, url, tipo, 1 if activa else 0)
        )
        return get_source_by_id(cur.lastrowid)


def update_source(source_id, **kwargs):
    allowed = {"nombre", "url", "tipo", "activa"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if not fields:
        return get_source_by_id(source_id)
    fields["updated_at"] = "datetime('now')"
    set_clause = ", ".join(
        f"{k} = datetime('now')" if k == "updated_at" else f"{k} = ?"
        for k in fields
    )
    values = [v for k, v in fields.items() if k != "updated_at"]
    values.append(source_id)
    with get_db() as conn:
        conn.execute(f"UPDATE sources SET {set_clause} WHERE id = ?", values)
    return get_source_by_id(source_id)


def delete_source(source_id):
    with get_db() as conn:
        affected = conn.execute("DELETE FROM sources WHERE id = ?", (source_id,)).rowcount
    return affected > 0


# ── News CRUD ─────────────────────────────────────────────────────────────────

def upsert_news(items):
    """Insert list of news dicts, ignoring duplicates by url_original."""
    inserted = 0
    with get_db() as conn:
        for item in items:
            try:
                conn.execute(
                    """INSERT OR IGNORE INTO noticias
                       (titulo, contenido, resumen, imagen, fecha_publicacion, fuente_id, url_original, multimedia)
                       VALUES (?,?,?,?,?,?,?,?)""",
                    (
                        item.get("titulo"),
                        item.get("contenido"),
                        item.get("resumen"),
                        item.get("imagen"),
                        item.get("fecha_publicacion"),
                        item.get("fuente_id"),
                        item.get("url_original"),
                        json.dumps(item.get("multimedia", [])),
                    )
                )
                inserted += conn.execute("SELECT changes()").fetchone()[0]
            except Exception as e:
                logger.warning("⚠️ No se pudo insertar noticia %s: %s", item.get("url_original"), e)
    return inserted


def get_news(source_id=None, limit=50, offset=0):
    with get_db() as conn:
        base = """
            SELECT n.*, s.nombre AS source_name, s.url AS source_url
            FROM noticias n
            LEFT JOIN sources s ON n.fuente_id = s.id
        """
        params = []
        if source_id:
            base += " WHERE n.fuente_id = ?"
            params.append(source_id)
        base += " ORDER BY n.fecha_publicacion DESC, n.id DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        rows = conn.execute(base, params).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            try:
                d["multimedia"] = json.loads(d.get("multimedia") or "[]")
            except Exception:
                d["multimedia"] = []
            result.append(d)
        return result


def get_news_by_id(news_id):
    with get_db() as conn:
        row = conn.execute(
            """SELECT n.*, s.nombre AS source_name FROM noticias n
               LEFT JOIN sources s ON n.fuente_id = s.id WHERE n.id = ?""",
            (news_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["multimedia"] = json.loads(d.get("multimedia") or "[]")
        except Exception:
            d["multimedia"] = []
        return d
