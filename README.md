# 🌍 TERMINAL_V.1 - GEO-SCANNER | News_globo

## 📡 Descripción del Proyecto

**News_globo** es una aplicación web interactiva de estilo cyberpunk que presenta un globo terrestre 3D donde puedes explorar noticias de diferentes países. Combina visualización geográfica con acceso a noticias en tiempo real, proporcionando una experiencia única de consumo de información global.

---

## ✨ Características Principales

- 🌐 **Globo 3D Interactivo** - Navega visualmente por todo el planeta con rotación automática
- 🔍 **Escaneo de Noticias por País** - Selecciona cualquier país para ver noticias locales
- 🎨 **Diseño Cyberpunk** - Interfaz retro-futurista con colores neón (cyan, magenta, verde)
- 📰 **Integración NewsAPI** - Acceso a miles de artículos de noticias en tiempo real
- 💻 **Terminal Virtual** - Interfaz estilo terminal para una experiencia inmersiva
- 🎯 **Responsive Design** - Adaptable a diferentes tamaños de pantalla
- ⚡ **Carga Dinámica** - Noticias cargadas sin recargar la página

---

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

### Navegar por la Interfaz

1. **Vista Global** - Al iniciar, ves todas las noticias mundiales
2. **Seleccionar País** - Haz clic en cualquier país del globo
3. **Ver Noticias** - Se cargarán automáticamente las noticias del país seleccionado
4. **Leer Artículo** - Haz clic en una noticia para ver detalles completos
5. **Volver** - Usa el botón "RESET_CAMERA" para regresar a la vista global

---

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

## 🔑 Configuración de API de NewsAPI

### Planes Disponibles

- **Plan Gratuito**: 100 requests/día, perfecto para desarrollo
- **Planes Premium**: Más requests, soporte prioritario

### Cambios de País Soportados

El sistema soporta códigos ISO de 2 letras (ej: `us`, `es`, `fr`, `jp`, etc.). Si no hay noticias específicas del país, automáticamente busca noticias relacionadas con su nombre.

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

## 🐛 Solución de Problemas

### ❌ "ERROR: API Key inválida"
**Solución**: Verifica que tu API Key de NewsAPI sea correcta y esté activa en tu cuenta.

### ❌ "No se carga el globo 3D"
**Solución**: Verifica tu conexión a internet. El proyecto necesita descargar las librerías CDN de Globe.gl y Three.js.

### ❌ "No aparecen noticias"
**Solución**: Algunos países pequeños o con códigos especiales pueden no tener datos. El sistema hace fallback automático a búsqueda por nombre.

### ❌ "Puerto 5000 ya en uso"
**Solución**: Modifica el puerto en `app.py`:
```python
app.run(host="0.0.0.0", port=5001, debug=True)
```

### ❌ "Error de CORS"
**Solución**: Los CDN públicos están configurados. Si usas un dominio personalizado, asegúrate de permitir CORS en tu servidor.

---

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología |
|-----------|-----------|
| Backend | Flask (Python) |
| Frontend | HTML5 + CSS3 + JavaScript |
| Visualización 3D | Globe.gl + Three.js |
| Datos Geográficos | GeoJSON |
| API de Noticias | NewsAPI.org |
| Servidor HTTP | Flask (desarrollo) |

---

## 📝 Requisitos (requirements.txt)

```
Flask==2.3.0
requests==2.31.0
Werkzeug==2.3.0
```

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Para contribuir:

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Haz commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Ver `LICENSE` para más detalles.

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

**Última actualización**: 2026-04-25

✨ *Made with ❤️ and cyberpunk aesthetics* ✨


----------
# Project Documentation for Virtual Valhalla

## Comprehensive Project Overview
This documentation aims to provide a thorough understanding of the Virtual Valhalla project, focusing on key functionalities, architecture, and usage instructions.

### Cyberpunk Theme Description
Virtual Valhalla combines the aesthetics of a neon-drenched cyberpunk universe with advanced technology to create an immersive user experience. Users navigate through a digital landscape filled with futuristic elements, mirroring the complexities of a high-tech society.

### API Key Management
The application supports multiple API keys, enabling enhanced security and management. Users can generate, revoke, and rotate keys through a simplified interface.

### Advanced Error Handling
With built-in error detection, the system can identify and manage rate limiting, ensuring that users receive feedback regarding their request limits. This allows for smoother user interactions and improved overall system resilience.

### System Architecture
The architecture of Virtual Valhalla comprises the following components:
- **Client**: The user-facing interface that interacts with backend services.
- **Server**: A RESTful API handling requests and responses.
- **Database**: Stores user data, API keys, and logs for auditing and troubleshooting.

### Usage Instructions
To get started:
1. Clone the repository.
2. Set up your environment.
3. Configure your API keys in the `.env` file.
4. Start the server and access the client.

### Troubleshooting Guide
- **Rate Limiting Error**: Ensure that you are not exceeding the request limit set by the API. Review your request patterns.
- **Configuration Issues**: Double-check API key placements and environment variables.
- **Database Connectivity**: Make sure your database is up and running and that the connection strings are correct.

### Features Documentation
- **User Authentication**: Secure login and registration processes.
- **Data Fetching**: Robust methods to retrieve and manipulate data seamlessly.

### Endpoints Documentation
- **GET /api/data**: Retrieve data using various queries.
- **POST /api/key**: Create a new API key.
- **DELETE /api/key/{id}**: Revoke an API key.

### Technologies Used
- **Frontend**: React.js
- **Backend**: Node.js with Express
- **Database**: MongoDB

### Contribution Guidelines
We welcome contributions! Please fork this repository and submit a pull request for your proposed changes. Don't forget to include tests where applicable.

### Future Roadmap
- **Add support for additional APIs**
- **Enhance UI with more interactive features**
- **Implement machine learning for predictive analytics**

## Conclusion
This document serves as a living guide. Keep it updated to reflect the most accurate information about the project as it evolves.  
For more information, visit our [GitHub repository](https://github.com/Virtual-Valhalla/News_globo).
