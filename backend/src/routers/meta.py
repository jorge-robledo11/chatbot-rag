"""
Módulo para endpoints meta de la API.

Este módulo define rutas de soporte como la raíz de la API, documentación
interactiva y verificación de salud del servicio.
"""

from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from loguru import logger

router = APIRouter()


@router.get('/')
async def api_root() -> dict:
    """
    Endpoint principal del Chatbot Ajover API.

    Returns:
        dict: Información sobre el servicio, endpoints y estado.

    Raises:
        HTTPException: Si ocurre un error interno.
    """
    try:
        logger.info('→ Llamada a api_root')
        return {
            'service': 'Ajover Chatbot API',
            'version': '1.0.0',
            'status': 'running',
            'description': 'API completa para chatbot con RAG pipeline y gestión de usuarios',
            'navigation': {'interactive_docs': '/docs', 'health_status': '/health'},
            'endpoints': {
                'chat': {
                    'base': '/chat',
                    'query': '/chat/query',
                    'description': 'Interacción con el chatbot',
                },
                'sessions': {
                    'base': '/sessions',
                    'create': 'POST /sessions',
                    'get': 'GET /sessions/{session_id}',
                    'description': 'Gestión de sesiones de chat',
                },
                'users': {
                    'base': '/users',
                    'register': 'POST /users',
                    'get': 'GET /users/{user_id}',
                    'description': 'Gestión de usuarios',
                },
            },
            'powered_by': [
                'Azure OpenAI',
                'Azure Cognitive Search',
                'FastAPI',
                'Azure Functions',
            ],
        }
    except Exception as e:
        logger.exception(f'❌ Error en api_root: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error interno al obtener la raíz de la API: {e}',
        ) from e


@router.get(
    '/docs',
    response_class=HTMLResponse,
    include_in_schema=False,
    tags=['Documentation'],
    summary='Documentación interactiva de la API',
    description='Sirve la documentación interactiva y moderna de la API usando Scalar.',
)

async def get_scalar_docs() -> HTMLResponse:
    """
    Sirve la documentación interactiva y moderna de la API usando Scalar.

    Returns:
        HTMLResponse: Contenido HTML para la interfaz de documentación.

    Raises:
        HTTPException: Si ocurre un error al cargar la documentación.
    """
    try:
        logger.info('→ Llamada a get_scalar_docs')
        html = """
        <!doctype html>
        <html>
          <head>
            <title>Ajover API Docs - Scalar</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <meta http-equiv="Permissions-Policy" content="none">
            <base href="/" />
            <style>body { margin: 0; }</style>
          </head>
          <body>
            <script id="api-reference"
                    data-url="./openapi.json">
            </script>
            <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
          </body>
        </html>
        """
        return HTMLResponse(content=html, media_type='text/html')
    except Exception as e:
        logger.exception(f'❌ Error al servir la documentación Scalar: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error interno al cargar la documentación: {e}',
        ) from e


@router.get('/health', tags=['Monitoring'])
async def health_check() -> Response:
    """
    Endpoint simple para verificar que la API está en funcionamiento.

    Returns:
        Response: Respuesta con código 200 si el servicio está saludable.

    Raises:
        HTTPException: Si ocurre un error interno.
    """
    try:
        logger.info('→ Llamada a health_check')
        return Response(status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(f'❌ Error en health_check: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error interno en el health check: {e}',
        ) from e
