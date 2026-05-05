# 🌍 NEWS_GLOBO | Terminal V.1 Geo-Scanner

News_globo es una plataforma de visualización geoespacial con estética **cyberpunk** para el monitoreo de noticias globales en tiempo real. El sistema utiliza un motor 3D interactivo para proyectar datos informativos sobre un globo terrestre dinámico.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | HTML5, CSS3 (Neon-custom), JavaScript |
| Globo 3D | [Globe.gl](https://globe.gl/) + [Three.js](https://threejs.org/) |
| Animaciones | [GSAP 3](https://gsap.com/) |
| Backend | Python 3 + [Flask](https://flask.palletsprojects.com/) |
| Datos | [NewsAPI.org](https://newsapi.org/) + GeoJSON |

---

## 📁 Estructura del Proyecto

```
news-globo/
├── app.py                          # Servidor Flask (proxy API + rutas)
├── requirements.txt                # Dependencias Python
├── templates/
│   └── index.html                  # Página principal (UI cyberpunk)
└── static/
    ├── style.css                   # Estilos neon / cyberpunk
    ├── countries.geojson           # Límites de países (110m)
    ├── custom.geo.json             # GeoJSON alternativo
    ├── ne_50m_admin_0_countries.json
    └── js/
        ├── app.js                  # Lógica principal del globo y noticias
        ├── intro.js                # Animación de intro (zoom con GSAP)
        └── shaders/
            └── waterDrop.js        # Shader visual (Three.js)
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

# 3. Configurar la API key (variable de entorno - crea el archivo .env con este contenido)
NEWS_API_KEY=key1,key2,key3

# 4. Ejecutar el servidor
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

---

## 🚀 Uso

1. **Intro:** Al cargar la página aparece el globo en vista lejana con un punto pulsante. Haz **clic** para iniciar el zoom de entrada.
2. **Zoom de entrada:** La cámara hace un zoom fluido hacia el globo (animado con GSAP).
3. **Paneles:** Al finalizar el zoom, aparecen con animación los paneles `NEWS_TERMINAL` y `CONSOLE`.
4. **Seleccionar país:** Haz clic sobre cualquier país en el globo para cargar sus noticias.
5. **Leer noticia:** Haz clic sobre un titular para ver el resumen y el enlace a la fuente.
6. **Resetear:** Usa el botón `RESET_CAMERA` para volver a la vista global.

---

## ⚙️ Configuración de API Keys

El servidor soporta **múltiples API keys** con rotación automática en caso de rate-limit. Puedes configurar varias separadas por coma:

```bash
export NEWS_API_KEY=key1,key2,key3
```

El sistema rotará automáticamente entre ellas si alguna alcanza el límite de solicitudes.

---

## 📋 Endpoints del Servidor

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Página principal |
| `GET` | `/country-news?country=XX` | Noticias por código de país ISO |
| `GET` | `/article?url=...` | Extrae contenido de un artículo |
| `GET` | `/api-status` | Estado de las API keys |
| `POST` | `/reset-api-limits` | Resetea contadores de rate-limit |

---

## 🎨 Interfaz

- **NEWS_TERMINAL** (panel izquierdo): lista de titulares del país seleccionado. Tiene botón de minimizar (`−`/`+`).
- **CONSOLE** (panel derecho): log de eventos en tiempo real con niveles INFO / SUCCESS / WARNING / ERROR / DEBUG. Tiene botón de minimizar.
- **DATA_DECRYPTOR** (panel inferior derecho): muestra el resumen de la noticia seleccionada con enlace a la fuente original.

---

## 📦 Dependencias Python

```
Flask
requests
beautifulsoup4
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
