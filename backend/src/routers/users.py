"""
Módulo para la gestión de usuarios.

Este módulo define rutas de API para registrar y recuperar usuarios,
utilizando Cosmos DB como backend.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger

from backend.src.core.dependencies import get_user_manager
from backend.src.interfaces.cosmos_db_users_interface import CosmosDBUsersInterface
from backend.src.models.requests import UserCreateRequest
from backend.src.models.responses import UserResponse

router = APIRouter(prefix='/users', tags=['Users'])


@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    request: UserCreateRequest,
    user_manager: Annotated[CosmosDBUsersInterface, Depends(get_user_manager)],
) -> UserResponse:
    """
    Crea un nuevo usuario en el sistema.

    Args:
        request (UserCreateRequest): Datos para crear el usuario.
        user_manager (CosmosDBUsersInterface): Gestor de usuarios inyectado.

    Returns:
        UserResponse: El usuario creado.

    Raises:
        HTTPException: Si el email ya existe (400) o error interno (500).
    """
    logger.info(f'Intentando registrar usuario con email: {request.email}')
    try:
        user = await user_manager.create_user(
            email=request.email,
            password=request.password,
        )
        logger.success(f'Usuario creado exitosamente: {user.id}')
        return user
    except ValueError as e:
        logger.warning(f'Registro fallido para {request.email}: {e}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.exception(f'Error inesperado al crear usuario: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocurrió un error inesperado al registrar el usuario: {e}',
        ) from e


@router.get('/{user_id}', response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    user_manager: Annotated[CosmosDBUsersInterface, Depends(get_user_manager)],
) -> UserResponse:
    """
    Obtiene un usuario por su ID.

    Args:
        user_id (str): ID del usuario a recuperar.
        user_manager (CosmosDBUsersInterface): Gestor de usuarios inyectado.

    Returns:
        UserResponse: El usuario recuperado.

    Raises:
        HTTPException: Si el usuario no existe (404) o error interno (500).
    """
    logger.info(f'Buscando usuario por ID: {user_id}')
    try:
        user = await user_manager.get_user_by_id(user_id)
        if not user:
            logger.warning(f'Usuario no encontrado: {user_id}')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Usuario no encontrado: {user_id}',
            )
        return user
    except Exception as e:
        logger.exception(f'Error inesperado al consultar usuario {user_id}: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ocurrió un error inesperado al buscar el usuario: {e}',
        ) from e
