"""
Punto de entrada de la aplicación FastAPI.

Configura la aplicación FastAPI, incluyendo:
- Logging
- Documentación
- Políticas de seguridad
- CORS
- Routers
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.src.core.lifespan_manager import lifespan
from backend.src.core.logging_config import endpoints_logging, setup_logging
from backend.src.core.openapi import documentation_config
from backend.src.core.policies import add_security_middleware
from backend.src.routers import chat, meta, sessions, users

# ------------------------------------------------------------------------------------------
#                  🚀 API AJOVER CHATBOT: ENTRYPOINT PRINCIPAL DE FASTAPI
# ------------------------------------------------------------------------------------------
setup_logging()
logger.info('Inicializando configuración de logging.')
IS_AZURE_FUNCTIONS = os.getenv('FUNCTIONS_WORKER_RUNTIME')
logger.debug(f'ENTORNO AZURE FUNCTIONS: {IS_AZURE_FUNCTIONS or "No definido"}')

# Punto de entrada de la aplicación FastAPI
app = FastAPI(
    title='Ajover Chatbot API',
    description='API para interactuar con el pipeline RAG, gestionar sesiones y usuarios.',
    version='1.0.0',
    lifespan=lifespan if not IS_AZURE_FUNCTIONS else None,
    docs_url=None,  # Deshabilitamos los docs por defecto para usar los nuestros
    redoc_url=None,
    swagger_ui_parameters={
        'displayRequestDuration': False,
        'defaultModelsExpandDepth': -1,
        'syntaxHighlight': False,
    },
)
logger.success(
    f"Instancia de FastAPI creada: title='{app.title}', version='{app.version}'."
)

# ------------------------------------------------------------------------------------------
#                           📜 Configurar logging de endpoints
# ------------------------------------------------------------------------------------------
logger.info('Configurando logging de endpoints.')
endpoints_logging(app)
logger.success('Configuración de logging de endpoints completada.')

# ------------------------------------------------------------------------------------------
#                               📜 Configurar documentación
# ------------------------------------------------------------------------------------------
logger.info('Configurando documentación.')
documentation_config(app)
logger.success('Configuración de documentación completada.')

# ------------------------------------------------------------------------------------------
#                           📜 Configurar políticas de seguridad
# ------------------------------------------------------------------------------------------
logger.info('Configurando políticas de seguridad.')
add_security_middleware(app)
logger.success('Configuración de políticas de seguridad completada.')

# ------------------------------------------------------------------------------------------
#                    🌎 Configurar CORS (Cross-Origin Resource Sharing)
# ------------------------------------------------------------------------------------------
logger.info('Registrando middleware CORS.')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],  # Permite todos los métodos
    allow_headers=['*'],  # Permite todos los headers
)
logger.success('Middleware CORS registrado.')

# ------------------------------------------------------------------------------------------
#                  🔌 REGISTRO DE ROUTERS (ENDPOINTS DE LA API)
# ------------------------------------------------------------------------------------------
logger.info('Incluyendo routers.')
app.include_router(meta.router)
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(users.router)
logger.success(
    f'🔌 ROUTERS REGISTRADOS CORRECTAMENTE. Endpoints disponibles: {app.routes}'
)

# ------------------------------------------------------------------------------------------
#                       👍 Aplicación lista para arrancar
# ------------------------------------------------------------------------------------------
logger.info('Aplicación FastAPI lista. Esperando peticiones...')
