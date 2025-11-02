"""
Configuración de la documentación OpenAPI para la aplicación FastAPI.

Define un método para sobrescribir la generación del esquema OpenAPI y ajusta
la base del servidor para compatibilidad en diferentes entornos.
"""

from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from loguru import logger


def documentation_config(app: FastAPI) -> None:
    """
    Configura la documentación de la API.

    Args:
        app (FastAPI): Instancia de FastAPI a la que se aplicará la configuración.

    Raises:
        Exception: Si ocurre un error al generar el esquema OpenAPI.
    """

    def custom_openapi() -> dict[str, Any]:
        """
        Sobrescribe app.openapi para forzar el servidor base al root_path.

        Funciona tanto local como en Azure Functions. Ajusta la URL de base del
        servidor a cadena vacía para que el UI use rutas relativas y evite
        prefijos duplicados.

        Returns:
            dict[str, Any]: Esquema OpenAPI configurado.

        Raises:
            Exception: Si ocurre un error al construir el esquema OpenAPI.
        """
        try:
            if app.openapi_schema:
                logger.debug('Reutilizando esquema OpenAPI existente.')
                return app.openapi_schema

            logger.debug('Generando esquema OpenAPI...')
            schema: dict[str, Any] = get_openapi(
                title=app.title,
                version=app.version,
                routes=app.routes,
            )

            base: str = app.root_path or ''
            schema['servers'] = [{'url': base}]
            logger.info(f"OpenAPI.servers configurado a url='{base}'.")

            app.openapi_schema = schema
            return schema
        except Exception as e:
            logger.exception(f'Error al generar el esquema OpenAPI: {e}')
            raise

    app.openapi = custom_openapi
    logger.success(
        "Función custom_openapi instalada en app.openapi con base relativa '%s'.",
        app.root_path or '',
    )
