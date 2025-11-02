"""
Modelos de request para el sistema RAG.

Define las estructuras de datos para solicitudes de consulta
con todos los atributos necesarios para el procesamiento RAG.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.src.models.common import ChatMessage, Priority, QueryType


class BaseQueryRequest(BaseModel):
    """
    Request completo para consultas al sistema RAG.

    - query: Consulta del usuario
    - session_id: ID de sesión opcional
    - chat_history: Historial de mensajes de la conversación
    - query_type: Tipo de consulta para personalizar el procesamiento
    - priority: Prioridad de la consulta
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description='Consulta del usuario',
    )
    session_id: str | None = Field(None, description='ID de sesión opcional')
    chat_history: list[ChatMessage] | list = Field(
        default_factory=list,
        description='Historial de mensajes de la conversación',
    )
    query_type: QueryType | None = Field(
        default=None,
        description='Tipo de consulta para personalizar el procesamiento',
    )
    priority: Priority | None = Field(
        default=Priority.NORMAL,
        description='Prioridad de la consulta',
    )


class UserCreateRequest(BaseModel):
    """
    Request para crear un nuevo usuario.

    - email: Email del usuario
    - password: Contraseña del usuario
    """

    email: str | None = Field(None, description='Email del usuario')
    password: str | None = Field(None, description='Contraseña del usuario')


class UserResponse(BaseModel):
    """
    Response seguro para los datos de un usuario.

    - user_id: ID del usuario
    - email: Email del usuario
    - is_active: Estado del usuario
    - created_at: Fecha de creación del usuario
    """

    user_id: str | None = Field(None, description='ID del usuario')
    email: str | None = Field(None, description='Email del usuario')
    is_active: bool | None = Field(None, description='Estado del usuario')
    created_at: datetime | None = Field(
        None, description='Fecha de creación del usuario'
    )
    model_config = ConfigDict(from_attributes=True)
