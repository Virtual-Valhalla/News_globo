# 🌍 NEWS_GLOBO | Terminal V.1 Geo-Scanner

News_globo es una plataforma de visualización geoespacial con estética **cyberpunk** para el monitoreo de noticias globales en tiempo real. El sistema utiliza un motor 3D interactivo para proyectar datos informativos sobre un globo terrestre dinámico.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML5, CSS3 (Neon-custom), JavaScript (Vanilla modular) |
| Globo 3D | [Globe.gl](https://globe.gl/) + [Three.js](https://threejs.org/) |
| Animaciones | [GSAP 3](https://gsap.com/) |
| Backend | Python 3.12 + [Flask](https://flask.palletsprojects.com/) (Blueprints) |
| Scraping | BeautifulSoup4 |
| Datos | [NewsAPI.org](https://newsapi.org/) + GeoJSON |
| Servidor prod | Gunicorn |

---

## 📁 Estructura del Proyecto

```
News_globo/
├── app.py                          # Punto de entrada — registra Blueprints
├── config.py                       # Constantes: TTLs, países, builder de API keys
├── requirements.txt                # Dependencias Python
├── services/
│   └── news_service.py             # Caché, rotación de keys, fetch, scraping
├── routes/
│   ├── main_routes.py              # Blueprint: GET /
│   └── api_routes.py               # Blueprint: /country-news, /article, /cache-*, /api-status
├── templates/
│   └── index.html                  # Página principal (UI cyberpunk)
└── static/
    ├── css/
    │   ├── main.css                # Estilos base, globo, tipografía, responsive
    │   └── terminal.css            # Consola, terminal, lector, noticias, botones
    ├── js/
    │   ├── components/
    │   │   ├── console.js          # logToConsole, clearConsole, toggleConsole
    │   │   ├── terminal.js         # Selector de categorías, toggleTerminal
    │   │   └── reader.js           # openReader, closeReader, loadArticle
    │   ├── core/
    │   │   └── globe_engine.js     # Init Globe.gl, GeoJSON, eventos click/hover
    │   ├── app.js                  # selectNode, loadNews, resetToGlobal, onload
    │   ├── intro.js                # Animación de intro con GSAP
    │   └── shaders/
    │       └── waterDrop.js        # Shader Three.js (reservado)
    ├── vendor/
    │   ├── three.min.js            # Three.js (local)
    │   └── globe.gl.min.js         # Globe.gl (local)
    └── data/
        ├── countries.geojson
        ├── ne_50m_admin_0_countries.json
        └── ...                     # Otros archivos GeoJSON
```

---

## 🔧 Requisitos Previos

- **Python 3.8+**
- **pip**
- Una API key gratuita de [NewsAPI.org](https://newsapi.org/register)

---

## 📦 Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Virtual-Valhalla/News_globo.git
cd News_globo

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar la API key como variable de entorno
export NEWS_API_KEY=tu_api_key

# Soporta múltiples keys separadas por coma para rotación automática:
export NEWS_API_KEY=key1,key2,key3

# 4. Ejecutar el servidor
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

Para producción:
```bash
gunicorn --bind=0.0.0.0:5000 --reuse-port app:app
```

---

## 🚀 Uso

1. **Intro:** Al cargar la página aparece el globo en vista lejana con un punto pulsante. Haz **clic** para iniciar el zoom de entrada.
2. **Zoom de entrada:** La cámara hace un zoom fluido hacia el globo (animado con GSAP).
3. **Paneles:** Al finalizar el zoom, aparecen con animación los paneles `NEWS_TERMINAL` y `CONSOLE`.
4. **Seleccionar país:** Haz clic sobre cualquier país en el globo para cargar sus noticias.
5. **Filtrar categoría:** Usa las flechas del selector para cambiar entre categorías (General, Tecnología, Negocios, Deportes, etc.).
6. **Leer noticia:** Haz clic sobre un titular para ver el resumen completo y el enlace a la fuente en el panel `DATA_DECRYPTOR`.
7. **Resetear:** Usa el botón `RESET_CAMERA` para volver a la vista global.

---

## ⚙️ Configuración de API Keys

El servidor soporta **múltiples API keys** con rotación automática en caso de rate-limit:

```bash
export NEWS_API_KEY=key1,key2,key3
```

El sistema rotará automáticamente entre ellas si alguna alcanza el límite de solicitudes, y las reseteará si todas están bloqueadas.

---

## 📋 Endpoints del Servidor

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Página principal |
| `GET` | `/country-news?country=XX` | Noticias por código ISO de país |
| `GET` | `/country-news?country=XX&category=YY` | Noticias filtradas por categoría |
| `GET` | `/article?url=...` | Extrae contenido completo de un artículo |
| `GET` | `/cache-status` | Estado del caché en memoria |
| `POST` | `/cache-clear` | Limpia el caché (total o por país) |
| `GET` | `/api-status` | Estado de las API keys |
| `POST` | `/reset-api-limits` | Resetea contadores de rate-limit |

---

## 🎨 Interfaz

- **NEWS_TERMINAL** (panel izquierdo): lista de titulares del país seleccionado con selector de categoría y botón de minimizar.
- **CONSOLE** (panel superior derecho): log de eventos en tiempo real con niveles INFO / SUCCESS / WARNING / ERROR / DEBUG.
- **DATA_DECRYPTOR** (panel inferior derecho): muestra imagen, resumen y enlace de la noticia seleccionada. Embebe video de YouTube si está disponible.

---

## 📦 Dependencias Python

```
Flask==3.1.1
requests==2.32.4
beautifulsoup4==4.14.3
python-dotenv==1.2.2
gunicorn
```

---

## 👨‍💻 Autor

**Virtual-Valhalla**
- GitHub: [@Virtual-Valhalla](https://github.com/Virtual-Valhalla)

---

## 🔗 Enlaces Útiles

- [Globe.gl Docs](https://globe.gl/)
- [NewsAPI Docs](https://newsapi.org/docs)
- [Three.js](https://threejs.org/)
- [GSAP Docs](https://gsap.com/docs/)
- [Flask Docs](https://flask.palletsprojects.com/)

---

✨ *Made with ❤️ and cyberpunk aesthetics* ✨
