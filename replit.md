### 1. `replit.md` - Despliegue Manual (Zero AI Agent Cost)

Este procedimiento garantiza que no se active el Agente de Replit durante la configuración inicial.

# 🌐 NEWS_GLOBO | Manual Replit Deployment

Para evitar el consumo de créditos del "Replit Agent", sigue estrictamente este flujo de trabajo de infraestructura manual.

### 1. Preparación del Entorno "Limpio"
* No uses el botón "Import from GitHub" del dashboard principal.
* Selecciona **"Create Repl"** y busca la plantilla **"Blank Repl"** (o "Nothing"). 
* Esto crea un contenedor vacío sin procesos de configuración de IA activos.

### 2. Clonación Soberana vía Shell
Abre la **Shell** (herramienta de terminal) y ejecuta:

 Elimina archivos visibles
```bash
rm -rf *
```

 Elimina archivos ocultos que bloquean el clone
```bash
rm -rf .* 2>/dev/null
```
 Clonamos el repositorio
```bash
git clone https://github.com/Virtual-Valhalla/News_globo.git .
```
*Nota: El punto (.) al final es crítico para clonar los archivos directamente en la raíz actual.*

### 3. Instalación Manual de Dependencias
En la misma Shell, instala el stack tecnológico sin asistencia:
```bash
pip install -r requirements.txt
```
### 4. Inyección de Secretos (Variables de Entorno)
Usa la herramienta **Secrets** (icono de candado) en la barra lateral. No permitas que el Agente las gestione por ti. Añade:
* `NEWS_API_KEY`: Tu clave de NewsAPI.org (opcional para live data).
* `DB_PATH`: `news_globo.db`

### 5. Configuración del Entrypoint
Asegúrate de que el archivo `.replit` (que ya está en el repo) tenga definido el comando de ejecución manual para que el botón **Run** no dispare un escaneo de IA.
```

---
