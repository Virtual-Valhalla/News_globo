--------------------------------------------------------------------------------
🌍 NEWS_GLOBO | Terminal V.1 Geo-Scanner
News_globo es una plataforma de visualización geoespacial con estética cyberpunk para el monitoreo de noticias globales en tiempo real
. El sistema utiliza un motor 3D interactivo para proyectar datos informativos sobre un globo terrestre dinámico
.
🛠️ Stack Tecnológico
Frontend: HTML5, CSS3 (Neon-custom), JavaScript (Globe.gl, Three.js)
.
Backend: Flask (Python) actuando como Proxy API
.
Data Layer: NewsAPI.org & GeoJSON de fronteras globales
.
## 🔧 Requisitos Previos

Antes de instalar, asegúrate de tener:

- **Python 3.8+** instalado en tu sistema
- **pip** (gestor de paquetes de Python)
- **Git** para clonar el repositorio
-  
-  

---
## 📦 Instalación

```

```

```

```

---
## 🚀 Uso

```

```

La aplicación se ejecutará en ` `

.
📋 Arquitectura y Flujo de Datos
Interacción: Selección de países mediante clics con rotación automática y control de cámara (RESET_CAMERA)
.
UI Terminal: Interfaz retro-futurista
.


--------------------------------------------------------------------------------
## 📁 Estructura del Proyecto

```

```

### Descripción de Archivos

- **app.py** - Servidor Flask que:
  - Sirve la página HTML principal
  - Maneja solicitudes de noticias por país
  - Integra la API de NewsAPI

- **index.html** - Aplicación web que contiene:
  - Globo 3D interactivo (Globe.gl)
  - Terminal principal con noticias
  - Consola de lectura para artículos
  - Estilos cyberpunk personalizados

- **countries.geojson** - GeoJSON con límites de 195+ países/territorios
  - 


- ** ** -  
  - 

---

## 👨‍💻 Autor

**Virtual-Valhalla** - Desarrollador de aplicaciones web interactivas

- GitHub: [@Virtual-Valhalla](https://github.com/Virtual-Valhalla)

---

## 🔗 Enlaces Útiles

- [Globe.gl Documentation](https://globe.gl/)
- [NewsAPI Documentation](https://newsapi.org/docs)
- [Three.js](https://threejs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GeoJSON Specification](https://geojson.org/)

---


✨ *Made with ❤️ and cyberpunk aesthetics* ✨

