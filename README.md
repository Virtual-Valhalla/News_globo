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
- Una **API Key válida de [NewsAPI.org](https://newsapi.org)** (gratis)

---

## 📦 Instalación

### 1️⃣ Clonar el Repositorio
```bash
git clone https://github.com/Virtual-Valhalla/News_globo.git
cd News_globo
```

### 2️⃣ Crear Entorno Virtual
```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar API Key de NewsAPI
1. Ve a [newsapi.org](https://newsapi.org) y crea una cuenta gratis
2. Copia tu API Key
3. Abre `app.py` y reemplaza `'NEWS_API_KEY'` con tu clave:
```python
NEWS_API_KEY = 'tu_clave_aqui'
```

---
## 🚀 Uso

### Ejecutar la Aplicación
```bash
python app.py
```

La aplicación se ejecutará en `http://localhost:5000`

.
📋 Arquitectura y Flujo de Datos
Interacción: Selección de países mediante clics con rotación automática y control de cámara (RESET_CAMERA)
.
Lógica de Fallback: El sistema utiliza códigos ISO de 2 letras; si no hay datos específicos, realiza una búsqueda semántica por el nombre del territorio
.
UI Terminal: Interfaz retro-futurista con paleta neón (Cyan, Magenta, Verde) y tipografía de sistema monoespaciada
.
--------------------------------------------------------------------------------
## 📁 Estructura del Proyecto

```
News_globo/
├── app.py                    # Backend Flask con rutas y API
├── templates/
│   └── index.html           # Frontend principal (HTML + CSS + JavaScript)
├── static/
│   └── countries.geojson    # Datos geográficos de países
├── requirements.txt         # Dependencias de Python
└── README.md               # Este archivo
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

---

## 🎨 Diseño Visual

La interfaz sigue una estética **cyberpunk retro-futurista**:

- **Colores Neón**:
  - Cyan (`#00ffff`) - Información principal
  - Magenta (`#ff00ff`) - Elementos interactivos
  - Verde (`#00ff00`) - Consola de lectura
  - Negro (`#000000`) - Fondo

- **Fuente**: Courier New (estilo terminal)
- **Sombras**: Brillos neón alrededor de elementos principales
- **Animaciones**: Transiciones suaves al interactuar

---
--------------------------------------------------------------------------------


### Navegar por la Interfaz

1. **Vista Global** - Al iniciar, ves todas las noticias mundiales
2. **Seleccionar País** - Haz clic en cualquier país del globo
3. **Ver Noticias** - Se cargarán automáticamente las noticias del país seleccionado
4. **Leer Artículo** - Haz clic en una noticia para ver detalles completos
5. **Volver** - Usa el botón "RESET_CAMERA" para regresar a la vista global

---



---

## 👨‍💻 Autor

**Virtual-Valhalla** - Desarrollador de aplicaciones web interactivas

- GitHub: [@Virtual-Valhalla](https://github.com/Virtual-Valhalla)

---

## 📞 Soporte

¿Tienes dudas o sugerencias? Abre un [Issue](https://github.com/Virtual-Valhalla/News_globo/issues) en el repositorio.

---

## 🔗 Enlaces Útiles

- [Globe.gl Documentation](https://globe.gl/)
- [NewsAPI Documentation](https://newsapi.org/docs)
- [Three.js](https://threejs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [GeoJSON Specification](https://geojson.org/)

---

**Última actualización**: 2026-04-27

✨ *Made with ❤️ and cyberpunk aesthetics* ✨

📈 Roadmap & Futuras Mejoras
Para escalar esta herramienta hacia una aplicación de grado de producción, se proponen las siguientes implementaciones técnicas:
Caché de Datos: Implementar una capa de persistencia (SQLite/Redis) para almacenar noticias temporalmente y optimizar el consumo de la cuota de la API
.
WebSockets: Migrar el flujo de datos a una conexión bi-direccional para actualizaciones de noticias "Breaking News" en vivo sin recargar la interfaz.
Análisis de Sentimiento: Integrar modelos de Machine Learning para clasificar las noticias por tono (positivo, negativo o neutral) y representarlo visualmente en el globo
.
Capas Informativas (Layers): Añadir filtros conmutables para visualizar datos climáticos, de tráfico o zonas de conflicto mediante WebGL.
Optimización de GPU: Implementar Shaders de GLSL personalizados para mejorar la tasa de refresco en dispositivos móviles.

### Future Roadmap
- **Add support for additional APIs**
- **Enhance UI with more interactive features**
- **Implement machine learning for predictive analytics**

## Conclusion
This document serves as a living guide. Keep it updated to reflect the most accurate information about the project as it evolves.  
For more information, visit our [GitHub repository](https://github.com/Virtual-Valhalla/News_globo).
