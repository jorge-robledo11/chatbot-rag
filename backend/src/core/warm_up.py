"""
Inicialización de recursos globales (warm-up) para la aplicación FastAPI.

Proporciona funciones para inicializar recursos externos y asegurar que
estén listos tanto en entornos locales como en Azure Functions.
"""

import asyncio

from fastapi import FastAPI, Request
from loguru import logger

from backend.src.infrastructure.infrastructure import get_infrastructure
from backend.src.orchestrator.settings.agent_factory import (
    get_agent_singleton,
    initialize_agent,
)


async def warm_up_app(app: FastAPI) -> None:
    """
    Inicializa una sola vez todos los recursos externos y los guarda en `app.state`.

    Puede llamarse:
        • desde `lifespan()` (uvicorn/dev)
        • desde `ensure_warm_state()` (Azure Functions/tests).

    Args:
        app (FastAPI): Instancia de FastAPI donde se guardarán los recursos.

    Raises:
        RuntimeError: Si ocurre un error durante la inicialización de recursos.
    """
    if getattr(app.state, '_warm_ready', False):
        logger.info('Warm-up ya realizado. Saltando inicialización.')
        return

    infra = get_infrastructure()

    try:
        logger.info('🤖 Warm-up: inicializando agente…')
        await initialize_agent()
        app.state.agent = get_agent_singleton()
    except Exception as exc:
        logger.exception('Error al inicializar el agente IA durante el warm-up.')
        raise RuntimeError('Falló la inicialización del agente IA.') from exc

    try:
        logger.info('🔌 Warm-up: creando conexiones externas…')
        (
            session_mgr,
            user_mgr,
            searchai_pdf,
            searchai_web,
            openai_client,
            rag_service,
            blob_storage,
        ) = await asyncio.gather(
            infra.get_cosmos_db_session(),
            infra.get_cosmos_db_user(),
            infra.get_searchai(index_type='pdf'),
            infra.get_searchai(index_type='web'),
            infra.get_openai(),
            infra.get_rag_service(),
            infra.get_blob_storage(),
        )

        app.state.session_mgr = session_mgr
        app.state.user_mgr = user_mgr
        app.state.searchai_pdf = searchai_pdf
        app.state.searchai_web = searchai_web
        app.state.openai_client = openai_client
        app.state.rag_service = rag_service
        app.state.blob_storage = blob_storage

    except Exception as exc:
        logger.exception('Error al crear clientes externos durante el warm-up.')
        raise RuntimeError('Falló la inicialización de los recursos externos.') from exc

    app.state._warm_ready = True
    logger.success('✅ Warm-up completo.')


async def ensure_warm_state(request: Request) -> None:
    """
    Fallback perezoso para inicialización de recursos en Azure Functions.

    Si el servidor (Azure Functions) nunca ejecutó el evento `startup`,
    se invocará la primera vez que llegue un request.

    Args:
        request (Request): Petición de FastAPI que contiene el estado de la app.

    Raises:
        RuntimeError: Si ocurre un error durante la inicialización en el primer request.
    """
    if getattr(request.app.state, '_warm_ready', False):
        logger.debug(
            'Warm-up ya realizado en Azure Functions. No es necesario repetirlo.'
        )
        return

    logger.warning('⚠️  Startup no corrió → ejecutando lazy warm-up')
    try:
        await warm_up_app(request.app)
    except Exception as exc:
        logger.exception('Error durante el lazy warm-up en Azure Functions.')
        raise RuntimeError('Falló el lazy warm-up en Azure Functions.') from exc
    logger.success('✅ Lazy warm-up completado.')
