"""
Módulo de políticas de seguridad y middleware para FastAPI.

Define un middleware que aplica políticas de seguridad y registra trazas detalladas,
así como una función factory para añadirlo a la aplicación.
"""

from collections.abc import Awaitable
from time import perf_counter

from fastapi import FastAPI, Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityPoliciesMiddleware(BaseHTTPMiddleware):
    """
    Aplica políticas de seguridad y registra trazas detalladas.

    - Elimina encabezados de políticas de seguridad obsoletos/redundantes.
    - Registra la llegada de la petición.
    - Mide y registra el tiempo de procesamiento.
    """

    def __init__(
        self,
        app: FastAPI,
        policies_to_remove: list[str] | None = None,
    ) -> None:
        """
        Inicializa el middleware de políticas de seguridad.

        Args:
            app (FastAPI): Aplicación FastAPI.
            policies_to_remove (list[str] | None): Lista de encabezados a eliminar.
        """
        super().__init__(app)
        default_policies = ['Permissions-Policy', 'Feature-Policy']
        self.policies_to_remove = policies_to_remove or default_policies
        self.policies_to_remove_lower = [p.lower() for p in self.policies_to_remove]

    async def dispatch(
        self,
        request: Request,
        call_next: Awaitable[Response],
    ) -> Response:
        """
        Procesa cada petición, aplica las políticas y registra trazas.

        Args:
            request (Request): Solicitud entrante.
            call_next (Awaitable[Response]): Siguiente callable de la cadena.

        Returns:
            Response: Respuesta procesada.
        """
        start_time = perf_counter()
        logger.info(f'▶️ Solicitud recibida: {request.method} {request.url.path}')

        response = await call_next(request)

        process_time = (perf_counter() - start_time) * 1000
        formatted_time = f'{process_time:.2f}ms'

        logger.info(
            f'◀️ Respuesta enviada: {response.status_code} (tardó {formatted_time})'
        )

        for header_key in list(response.headers.keys()):
            if header_key.lower() in self.policies_to_remove_lower:
                response.headers.pop(header_key, None)
                logger.trace(f'    - Eliminado encabezado: {header_key}')
        return response


def add_security_middleware(app: FastAPI) -> None:
    """
    Factory para crear y añadir el middleware de seguridad a la aplicación.

    Este enfoque centraliza la configuración y la instanciación del middleware,
    desacoplando la configuración principal de la app de los detalles de
    implementación del middleware.

    Args:
        app (FastAPI): Aplicación FastAPI a la que se añadirá el middleware.
    """
    logger.info('🏭 Applying security middleware...')

    policies_to_remove = ['Permissions-Policy', 'Feature-Policy']
    app.add_middleware(
        SecurityPoliciesMiddleware,
        policies_to_remove=policies_to_remove,
    )
    logger.info('✅ Políticas de seguridad aplicadas.')
