### 3. `start.md` - Lógica Interna y Flujo Crítico

```markdown
# 🛠️ SYSTEM_INTERNAL | start.md

### Orden Crítico de Carga (Frontend)
El motor geoespacial es sensible al orden de ejecución de los scripts en `static/`. El `app.js` es el orquestador final.
1. `console.js` -> `terminal.js` -> `reader.js` (Estructura UI)
2. `intro.js` -> `globe_engine.js` (Motor visual Three.js)
3. `app.js` (Lógica de negocio y eventos)

### Gestión de Ingesta (Scheduler)
El hilo secundario de ingesta (`services/scheduler.py`) arranca con un delay inicial de 30s para no bloquear el inicio del servidor Flask. 

### Endpoints de Mantenimiento
* `/v1/fetch`: Disparador de scraping manual (ignora el caché).
* `/v1/cache-clear`: Limpieza selectiva de memoria por país.
```

---

