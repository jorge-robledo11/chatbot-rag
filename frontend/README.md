# 💻 Frontend - Chat Interface Vue.js

> **Interfaz web moderna y responsiva para interactuar con el agente LangGraph**

## 📋 Descripción

Frontend desarrollado en Vue.js 3 que proporciona una interfaz de chat intuitiva para comunicarse con el agente conversacional LangGraph. Incluye funcionalidades de envío de mensajes, archivos adjuntos, votación de respuestas y diseño responsive.

## 🎯 Características

- **💬 Chat en tiempo real**: Interfaz conversacional fluida y responsiva
- **📎 Archivos adjuntos**: Soporte para envío de documentos e imágenes
- **👍 Sistema de votación**: Califica las respuestas del agente (like/dislike)
- **📱 Responsive**: Adaptable a dispositivos móviles y desktop
- **🎨 UI moderna**: Diseño clean con CSS personalizado
- **⚡ Estado compartido**: Gestión eficiente del estado de la aplicación

## 🏗️ Arquitectura

```
frontend/
├── 📁 components/          # Componentes Vue reutilizables
│   ├── Header.vue         # Cabecera de la aplicación
│   ├── ContentChat.vue    # Área de mensajes del chat
│   ├── InputChat.vue      # Campo de entrada y envío
│   └── utils/            # Utilidades compartidas
├── 📁 views/              # Vistas principales
├── 📁 assets/             # Recursos estáticos
├── App.vue               # Componente raíz
├── main.js               # Punto de entrada
├── api.js                # Cliente API para backend
├── state.js              # Estado compartido
└── style.css             # Estilos CSS globales
```

## 🚀 Inicio Rápido

### Prerrequisitos

- **Node.js 16+** 
- **npm** o **yarn**
- **Backend LangGraph** ejecutándose (puerto 8000)

### Instalación

```bash
# Navegar al directorio
cd frontend

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# Build para producción
npm run build
```

### Configuración

El frontend se conecta automáticamente al backend LangGraph. Para cambiar la URL del backend, edita `api.js`:

```javascript
// api.js
const apiClientCommon = axios.create({
  baseURL: 'http://localhost:8000/api/chat', // Cambiar aquí
  headers: {
    'Content-Type': 'application/json',
  },
});
```

## 🔧 Tecnologías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Vue.js** | 3.x | Framework principal |
| **Vite** | 4.x+ | Build tool y dev server |
| **Axios** | 1.x | Cliente HTTP para API |
| **CSS3** | - | Estilos y responsive design |
| **JavaScript ES6+** | - | Lógica de aplicación |

## 📡 API Integration

El frontend se comunica con el backend a través de los siguientes endpoints:

### 1. Enviar Mensaje
```javascript
POST /api/chat/message
{
  "message": "Texto del mensaje",
  "thread_id": "id_usuario_unico"
}
```

### 2. Enviar Adjunto
```javascript
POST /api/chat/attachment (multipart/form-data)
- file: archivo adjunto
- thread_id: id del usuario
```

### 3. Votar Respuesta
```javascript
POST /api/chat/vote
{
  "id": "mensaje_id",
  "thread_id": "id_usuario",
  "rate": 1 // 1 para like, -1 para dislike
}
```

## 🎨 Componentes Principales

### Header.vue
- **Función**: Cabecera de la aplicación con título y branding
- **Props**: Ninguna
- **Características**: Logo, título, estado de conexión

### ContentChat.vue  
- **Función**: Área principal donde se muestran los mensajes
- **Props**: `messages` (array de mensajes)
- **Características**: 
  - Scroll automático
  - Diferenciación visual usuario/bot
  - Soporte para archivos adjuntos
  - Botones de votación

### InputChat.vue
- **Función**: Campo de entrada para mensajes y adjuntos
- **Props**: Ninguna
- **Características**:
  - Input multilínea
  - Botón de envío
  - Selector de archivos
  - Validación de entrada

## 🎯 Casos de Uso

### 1. Chat Básico
Usuario envía mensaje de texto → Bot responde → Usuario puede votar

### 2. Envío de Documentos
Usuario adjunta archivo → Sistema procesa → Bot analiza contenido

### 3. Sesión Persistente
- ID único por usuario (`thread_id`)
- Historial de conversación mantenido
- Estado guardado localmente

## ⚙️ Configuración Avanzada

### Variables de Entorno (opcional)

Crea un archivo `.env` para configuraciones específicas:

```bash
# .env
VITE_API_BASE_URL=http://localhost:8000/api/chat
VITE_WS_URL=ws://localhost:8000/ws
```

### Personalización de Estilos

Edita `style.css` para personalizar:
- Colores del tema
- Tipografía
- Espaciados
- Animaciones

### Estado Compartido

El archivo `state.js` maneja:
```javascript
export const sharedState = {
  user_id: 'usuario_unico_id',
  session_active: true,
  // Más estado según necesidad
}
```

## 🐛 Troubleshooting

### Error de CORS
Si tienes problemas de CORS, asegúrate de que el backend permita requests desde el frontend:
```python
# backend main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto de Vite
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error de Conectividad
Verifica que:
1. Backend esté ejecutándose en puerto 8000
2. URL en `api.js` sea correcta
3. No haya proxy o firewall bloqueando

## 📝 Scripts Disponibles

```bash
# Desarrollo con hot reload
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview

# Linting (si está configurado)
npm run lint
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit: `git commit -m 'feat: add nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

## 📋 Checklist de Setup

- [ ] Node.js instalado (16+)
- [ ] Dependencias instaladas (`npm install`)
- [ ] Backend ejecutándose en puerto 8000
- [ ] URL de API configurada en `api.js`
- [ ] Frontend ejecutándose (`npm run dev`)
- [ ] Chat funcional con backend

## 📚 Recursos Adicionales

- [Vue.js Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [Axios Documentation](https://axios-http.com/)

---

**¡Tu interfaz de chat está lista para conectar con el agente LangGraph! 🚀** 