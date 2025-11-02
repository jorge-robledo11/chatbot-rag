"""
Azure Functions App para el chatbot Ajover.

Este módulo configura una Azure Function que actúa como proxy hacia una aplicación FastAPI,
permitiendo el despliegue serverless del chatbot con inicialización de agentes y warm-up.
"""

import asyncio

import nest_asyncio
from azure.functions import (
    AsgiMiddleware,
    AuthLevel,
    FunctionApp,
    HttpRequest,
    HttpResponse,
)
from loguru import logger

from backend.src.app import app as fastapi_instance
from backend.src.core.logging_config import PropagateHandler, setup_logging
from backend.src.orchestrator.settings.agent_factory import initialize_agent

setup_logging(handlers=[PropagateHandler()])
nest_asyncio.apply()

logger.info('🚀 Inicializando agente en el arranque de FunctionApp...')
asyncio.run(initialize_agent())
logger.info('🤖 Agente inicializado correctamente.')
fn_app = FunctionApp()
logger.info('🚀 FunctionApp cargada correctamente.')


@fn_app.warm_up_trigger('warmup')
def warmup(warmup) -> None:
    """
    Función de calentamiento para precargar dependencias y reducir arranques en frío.

    Args:
        warmup (Context): Objeto de warm-up trigger proporcionado por Azure Functions.
    """
    logger.info('🔥 Warm-up trigger ejecutado.')


@fn_app.route(
    route='{*route:regex(^(?!(?:admin/|api/|logstream)).*$)}',
    auth_level=AuthLevel.ANONYMOUS,
)


async def http_function(req: HttpRequest) -> HttpResponse:
    """
    Maneja las peticiones HTTP y las redirige a FastAPI.

    Esta función actúa como proxy entre Azure Functions y la aplicación FastAPI,
    permitiendo que el chatbot funcione en un entorno serverless.

    Args:
        req (HttpRequest): Objeto de petición HTTP de Azure Functions.

    Returns:
        HttpResponse: Respuesta HTTP procesada por FastAPI a través del middleware ASGI.
    """
    logger.info('🚀 Handler personalizado cargado')
    logger.info(f'⚡️ HTTP Trigger: {req.method} {req.url}')
    return await AsgiMiddleware(fastapi_instance).handle_async(req)
