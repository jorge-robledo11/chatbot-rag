"""
Módulo para la gestión de sesiones de chat.

Este módulo define rutas de API para crear, recuperar y limpiar sesiones de
conversación, utilizando Cosmos DB como backend.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from backend.src.core.dependencies import get_session_manager
from backend.src.interfaces.cosmos_db_sessions_interface import (
    CosmosDBSessionsInterface,
)
from backend.src.models.common import Session

router = APIRouter(prefix='/sessions', tags=['Sessions'])


@router.post('/', response_model=Session, status_code=status.HTTP_201_CREATED)
async def create_new_session(
    user_id: str = 'anonymous_user',
    session_manager: Annotated[
        CosmosDBSessionsInterface, Depends(get_session_manager)
    ] = None,
) -> Session:
    """
    Crea una nueva sesión de chat vacía y la devuelve.

    Args:
        user_id (str, optional): ID del usuario. Defaults to "anonymous_user".
        session_manager (CosmosDBSessionsInterface): Gestor de sesiones inyectado.

    Returns:
        Session: La sesión recién creada.

    Raises:
        HTTPException: Si ocurre un error al crear la sesión.
    """
    logger.info(f'📥 Petición de creación de sesión para user_id={user_id}')
    try:
        session = await session_manager.create_session(user_id)
        logger.success(
            f'✨ Sesión creada exitosamente: session_id={session.session_id}'
        )
        return session

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(
            f'❌ Error inesperado al crear sesión para user_id={user_id}: {e}'
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error creando la sesión: {e}',
        ) from e


@router.get('/{session_id}', response_model=Session)
async def get_session_by_id(
    session_id: str,
    session_manager: Annotated[
        CosmosDBSessionsInterface, Depends(get_session_manager)
    ] = None,
) -> Session:
    """
    Recupera el estado completo y el historial de una sesión por su ID.

    Args:
        session_id (str): ID de la sesión a recuperar.
        session_manager (CosmosDBSessionsInterface): Gestor de sesiones inyectado.

    Returns:
        Session: La sesión recuperada.

    Raises:
        HTTPException: Si la sesión no existe (404) o error interno (500).
    """
    logger.info(f'🔍 Petición para recuperar sesión: {session_id}')
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            logger.warning(f'⚠️ Sesión no encontrada: {session_id}')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'La sesión especificada no existe: {session_id}',
            )

        logger.success('✅ Sesión recuperada: {}', session_id)
        return session

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(f'❌ Error inesperado al recuperar sesión {session_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error recuperando la sesión: {e}',
        ) from e


@router.delete('/{session_id}/history', response_model=Session)
async def clear_history(
    session_id: str,
    session_manager: Annotated[CosmosDBSessionsInterface, Depends(get_session_manager)],
) -> Session:
    """
    Elimina todo el historial de una sesión existente.

    Args:
        session_id (str): ID de la sesión a limpiar.
        session_manager (CosmosDBSessionsInterface): Gestor de sesiones inyectado.

    Returns:
        Session: La sesión con el historial limpiado.

    Raises:
        HTTPException: Si la sesión no existe (404) o error interno (500).
    """
    logger.info(f'🗑️ Petición para limpiar historial de sesión: {session_id}')
    try:
        session = await session_manager.clear_history(session_id)
        if not session:
            logger.warning(f'⚠️ No se pudo limpiar, sesión no encontrada: {session_id}')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Sesión no encontrada: {session_id}',
            )

        logger.success(f'🧹 Historial limpiado correctamente para sesión: {session_id}')
        return session

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(
            f'❌ Error inesperado al limpiar historial de sesión {session_id}: {e}'
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error limpiando el historial: {e}',
        ) from e
