"""
Módulo que define el ciclo de vida principal para FastAPI usando lifespan.

Controla las etapas de arranque, operación y cierre ordenado de recursos de infraestructura.
"""

import asyncio
from collections.abc import AsyncGenerator, Awaitable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from backend.src.core.logging_config import setup_logging
from backend.src.core.warm_up import warm_up_app
from backend.src.infrastructure.infrastructure import get_infrastructure


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Ciclo de vida de FastAPI.

    Args:
        app (FastAPI): Instancia de la aplicación FastAPI.

    Yields:
        None: Control vuelve a FastAPI durante el ciclo de vida.

    Raises:
        Exception: Si ocurre un error crítico durante el arranque o cierre de recursos.
    """
    try:
        setup_logging()
        logger.debug('🚀 Iniciando secuencia de arranque (lifespan)…')
        await warm_up_app(app)
    except Exception as exc:
        logger.critical(f'❌ Error crítico durante el arranque de la aplicación: {exc}')
        raise

    try:
        yield
    finally:
        logger.info('🛑 Iniciando secuencia de cierre (lifespan)…')
        infra = get_infrastructure()

        async def _safe_close(
            obj: object,
            method: str = 'close',
        ) -> Awaitable[None] | None:
            """
            Intenta cerrar un recurso asíncrono y reporta errores.

            Args:
                obj (object): Recurso a cerrar.
                method (str): Método de cierre.

            Returns:
                Awaitable[None] | None: Coroutine de cierre si existe el método.

            Raises:
                Exception: Propaga cualquier excepción que ocurra al cerrar el recurso.
            """
            if obj is not None and callable(getattr(obj, method, None)):
                try:
                    logger.info(
                        f'🔒 Cerrando recurso: {type(obj).__name__} usando método {method}'
                    )
                    return await getattr(obj, method)()
                except Exception as error:
                    logger.error(
                        f'❌ Error al cerrar {type(obj).__name__} con método {method}: {error}'
                    )
                    raise
            return None

        try:
            await asyncio.gather(
                _safe_close(getattr(app.state, 'session_mgr', None)),
                _safe_close(getattr(app.state, 'user_mgr', None)),
                _safe_close(getattr(app.state, 'openai_client', None), 'aclose')
                or _safe_close(getattr(app.state, 'openai_client', None)),
                _safe_close(getattr(app.state, 'searchai_pdf', None)),
                _safe_close(getattr(app.state, 'searchai_web', None)),
                _safe_close(getattr(app.state, 'rag_service', None)),
                _safe_close(getattr(app.state, 'blob_storage', None)),
            )
        except Exception as exc:
            logger.critical(f'❌ Error crítico durante el cierre de recursos: {exc}')
            raise

        if callable(getattr(infra, 'shutdown', None)):
            try:
                logger.info('🔒 Cerrando infraestructura global...')
                await infra.shutdown()
                logger.info('✅ Infraestructura global cerrada correctamente.')
            except Exception as exc:
                logger.critical(
                    f'❌ Error crítico al cerrar la infraestructura global: {exc}'
                )
                raise
        logger.success('✅ Secuencia de cierre finalizada.')
