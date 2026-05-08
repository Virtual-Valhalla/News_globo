### 4. `cost_optimization.md` - Configuración Anti-Costes IA

Este es el archivo adicional que solicitaste para blindar tu presupuesto en Replit.

# 📉 REPLIT_OPTIMIZATION | Guía de Ahorro y Desactivación de IA

Para minimizar o eliminar el gasto de "Cycles" (créditos) en Replit, aplica estas configuraciones de nivel Senior.

### 1. Desactivar el Autocompletado y Sugerencias de IA
Ve a **User Settings** (icono de engranaje) > **Code Editing** y desactiva:
* **AI Code Completion:** Evita que Ghostwriter consuma créditos por cada línea escrita.
* **AI Suggestion Panel:** Elimina los paneles de ayuda contextual que pueden generar cargos accidentales.

### 2. Uso Inteligente de Modos (Si decides usar IA)
Si necesitas usar el Agente para una tarea puntual, cámbialo en el selector de la esquina inferior derecha:
* **Economy Mode:** Cuesta **1/3** que el modo Power. Úsalo para refactorizaciones simples.
* **Evita el modo Turbo:** Es 2.5x más rápido pero puede costar hasta **6x más** por cada petición.

### 3. Guardrails en el Proyecto
Asegúrate de que el archivo `.replit` tenga configurado:
```toml
guessImports = false
```

Esto evita que Replit escanee tus archivos automáticamente para intentar resolver dependencias, un proceso que a menudo dispara tareas de IA facturables.

### 4. Límites de Gasto Hard-Cap
Configura un límite de gasto en `replit.com/usage`. Establece el **Hard Limit** en el mínimo posible para que el Repl se detenga automáticamente si hay un bucle infinito de gasto por parte del Agente.
```
