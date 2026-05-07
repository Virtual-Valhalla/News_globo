# NEWS_GLOBO — Comandos de inicio rápido

> Referencia rápida. Documentación completa en [README.md](README.md).

---

## Requisitos

- Python 3.8+
- API key gratuita: [newsapi.org/register](https://newsapi.org/register) _(opcional)_

---

## Setup inicial (una sola vez)

```bash
git clone https://github.com/Virtual-Valhalla/News_globo.git
cd News_globo
python -m venv venv
```

**Activar el entorno virtual:**

| Sistema | Comando |
|---------|---------|
| Windows PowerShell | `.\venv\Scripts\Activate.ps1` |
| Windows CMD | `venv\Scripts\activate.bat` |
| macOS / Linux | `source venv/bin/activate` |

```bash
pip install -r requirements.txt
```

---

## Iniciar la aplicación

### Windows — PowerShell (una sola key)
```powershell
$env:NEWS_API_KEY="TU_API_KEY"; python app.py
```

### Windows — PowerShell (varias keys, rotación automática)
```powershell
$env:NEWS_API_KEY="API_KEY_1,API_KEY_2,API_KEY_3"; python app.py
```

### Windows — CMD
```cmd
set NEWS_API_KEY=API_KEY_1,API_KEY_2,API_KEY_3 && python app.py
```

### macOS / Linux
```bash
NEWS_API_KEY="API_KEY_1,API_KEY_2,API_KEY_3" python app.py
```

### Sin API key (solo BD local)
```bash
python app.py
```

Abrir en el navegador: **http://localhost:5000**

---

## Archivo `.env` (alternativa persistente)

Crea `.env` en la raíz del proyecto:
```env
NEWS_API_KEY=API_KEY_1,API_KEY_2,API_KEY_3
```
Luego ejecuta simplemente `python app.py`.

---

## Producción (Gunicorn)

```bash
gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 app:app
```

Con API key:

**PowerShell**
```powershell
$env:NEWS_API_KEY="API_KEY_1,API_KEY_2,API_KEY_3"; gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 app:app
```

**macOS / Linux**
```bash
NEWS_API_KEY="API_KEY_1,API_KEY_2,API_KEY_3" gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=2 app:app
```

---

## Endpoints de diagnóstico

```
http://localhost:5000/          → Aplicación
http://localhost:5000/docs      → Documentación de la API
http://localhost:5000/v1/health → Healthcheck
http://localhost:5000/api-status     → Estado de las API keys
http://localhost:5000/cache-status   → Estado del caché
http://localhost:5000/v1/scheduler   → Estado del scheduler
```

---

## Ingesta manual de noticias

```bash
# Disparar scraping de todas las fuentes activas
curl -X POST http://localhost:5000/v1/fetch

# Scraping de una fuente concreta (ID numérico)
curl -X POST "http://localhost:5000/v1/fetch?source_id=1"

# Ejecución inmediata del scheduler en background
curl -X POST http://localhost:5000/v1/scheduler/run-now
```

---

## Poblar la BD con fuentes RSS (opcional)

```bash
python seed_sources.py
```

Añade más de 150 fuentes RSS internacionales a la base de datos local.
