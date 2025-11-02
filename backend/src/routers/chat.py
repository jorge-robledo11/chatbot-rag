"""
Módulo que define el endpoint principal del chatbot.

Este archivo contiene la ruta de la API para procesar las consultas de los
usuarios, gestionar las sesiones y orquestar las llamadas al agente de IA
subyacente.
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from backend.src.core.dependencies import get_agent, get_session_manager
from backend.src.interfaces.cosmos_db_sessions_interface import (
    CosmosDBSessionsInterface,
)
from backend.src.models.common import Session
from backend.src.models.requests import BaseQueryRequest
from backend.src.models.responses import BaseQueryResponse
from backend.src.orchestrator.settings.agent_factory import invoke_agent
from backend.src.orchestrator.settings.agent_settings import AjoverAgent

router = APIRouter(prefix='/chat', tags=['Chat'])


@router.post('/query', response_model=BaseQueryResponse)
async def process_user_query(
    request: BaseQueryRequest,
    agent: Annotated[AjoverAgent, Depends(get_agent)],
    session_manager: Annotated[
        CosmosDBSessionsInterface, Depends(get_session_manager)
    ],
) -> BaseQueryResponse:
    """
    Procesa una consulta del usuario, gestionando la sesión y la invocación del agente.

    Este endpoint autogestiona el ciclo de vida de la sesión. Si no se
    proporciona un `session_id`, o si el proporcionado no es válido, se crea
    automáticamente una nueva sesión.

    Args:
        request (BaseQueryRequest): La solicitud del usuario.
        agent (AjoverAgent): Dependencia inyectada del agente de IA.
        session_manager (CosmosDBSessionsInterface): Dependencia inyectada
            del gestor de sesiones.

    Raises:
        HTTPException: Para errores de validación (400), infraestructura (500),
            o fallos en el pipeline de IA (502).

    Returns:
        BaseQueryResponse: La respuesta completa, incluyendo el historial de chat.
    """
    logger.info('📩 Recibida nueva consulta al chat.')
    logger.debug(
        f'Payload recibido: session_id={request.session_id!r}, query={request.query!r}'
    )

    if not request.query or not request.query.strip():
        logger.warning('La consulta del usuario está vacía.')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Debes proporcionar una consulta.',
        )

    try:
        session: Session | None = None
        if request.session_id:
            logger.debug(f'Buscando sesión existente: {request.session_id}')
            session = await session_manager.get_session(request.session_id)

        if not session:
            logger.info('Sesión no encontrada o no proporcionada. Creando nueva...')
            session = await session_manager.create_session(user_id='anonymous_user')
            logger.success(f'✨ Nueva sesión creada: {session.session_id}')

    except Exception as e:
        logger.exception('❌ Error fatal gestionando la sesión de usuario.')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error al gestionar la sesión: {e}',
        ) from e

    try:
        logger.debug(f'Invocando agente para sesión: {session.session_id}')
        ai_result = await invoke_agent(
            agent=agent,
            user_query=request.query,
            session_id=session.session_id,
        )

        logger.trace(f'Resultado del agente: {ai_result}')
        final_session = await session_manager.get_session(session.session_id)

    except Exception as e:
        logger.exception('❌ Error en el pipeline de IA o al recuperar el historial.')
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'Error en la comunicación con el agente AI: {e}',
        ) from e

    try:
        response = BaseQueryResponse(
            response=ai_result.get('answer', 'No se pudo generar una respuesta.'),
            session_id=session.session_id,
            full_chat_history=final_session.chat_history if final_session else [],
            sources=ai_result.get('sources', []),
            confidence_score=ai_result.get('confidence_score', 1.0),
            escalation_recommended=ai_result.get('escalation_recommended', False),
        )
        logger.success(
            f'✅ Respuesta construida exitosamente para la sesión {session.session_id}'
        )
        return response
        
    except Exception as e:
        logger.exception('❌ Error crítico al construir la respuesta final.')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error al construir la respuesta: {e}',
        ) from e
