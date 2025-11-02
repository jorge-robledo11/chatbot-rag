"""
Configuración centralizada de logging para la aplicación.

Incluye integración entre Loguru y el sistema estándar de logging de Python,
así como el registro de manejadores globales de excepciones para FastAPI.
"""

import logging
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from backend.config import get_settings
from backend.config.logging_settings import LoguruSettings


class PropagateHandler(logging.Handler):
    """
    Toma los logs de Loguru y los propaga al sistema de logging estándar de Python.

    Útil para entornos que solo capturan logs de logging (p.ej. Azure Functions).
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Propaga un registro de log al logger estándar de Python.

        Args:
            record (logging.LogRecord): Registro de log a propagar.

        Raises:
            Exception: Si ocurre un error al propagar el log.
        """
        try:
            logging.getLogger(record.name).handle(record)
        except Exception as exc:
            logger.critical(f'❌ Error propagando el log de {record.name}: {exc}')
            raise


def setup_logging(handlers: list[logging.Handler] | None = None) -> None:
    """
    Configura Loguru para toda la aplicación.

    Args:
        handlers (list[logging.Handler] | None): Lista opcional de handlers adicionales.

    Raises:
        Exception: Si ocurre un error crítico durante la configuración de logging.
    """
    try:
        settings: LoguruSettings = get_settings().logging
        handlers = handlers or []
        
        project_root = Path(__file__).parents[2].resolve()
        logs_dir = project_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        log_file_path = logs_dir / "app.log"

        logger.remove()
        logger.add(
            sys.stderr,
            level=settings.level.upper(),
            colorize=settings.colorize,
            format=settings.console_format,
        )
        logger.add(
            str(log_file_path),
            level=settings.file_level.upper(),
            rotation=settings.rotation,
            retention=settings.retention,
            enqueue=True,
            backtrace=True,
            diagnose=True,
            format=settings.file_format,
        )
        for h in handlers:
            logger.add(h, format='{message}')
        logger.info('✅ Logger de Loguru configurado.')
    except Exception as exc:
        logger.critical(f'❌ Error crítico durante la configuración de logging: {exc}')
        raise


def endpoints_logging(app: FastAPI) -> None:
    """
    Registra el PropagateHandler y un handler global de excepciones en FastAPI.

    Args:
        app (FastAPI): Instancia de la aplicación FastAPI.

    Raises:
        Exception: Si ocurre un error crítico durante la configuración del logger de endpoints.
    """
    try:
        setup_logging(handlers=[PropagateHandler()])

        async def log_exceptions(request: Request, exc: Exception) -> JSONResponse:
            try:
                logger.exception(f'❌ Error en petición {request.method} {request.url}')
            except Exception as exc_logger:
                logger.critical(
                    f'❌ Error al loguear excepción en handler global: {exc_logger}'
                )
                raise
            return JSONResponse(
                status_code=500,
                content={'detail': 'Internal Server Error'},
            )

        app.add_exception_handler(Exception, log_exceptions)
        logger.info('🔧 App logger configurado con PropagateHandler.')
    except Exception as exc:
        logger.critical(
            f'❌ Error crítico durante la configuración de endpoints logging: {exc}'
        )
        raise
