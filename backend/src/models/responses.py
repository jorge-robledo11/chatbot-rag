"""
Modelos de respuesta (response) para la API.

Define la estructura de los datos que el servidor envía de vuelta al cliente.
Estos modelos garantizan que las respuestas sean consistentes, predecibles y seguras,
utilizando herencia para mantener el código limpio y sin redundancias.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from backend.src.models.common import BasicSource, ChatMessage
from backend.src.utils.time_utils import get_colombia_time


class BaseQueryResponse(BaseModel):
    """
    Respuesta base para las consultas del chatbot.

    - response: La respuesta generada por el asistente.
    - confidence_score: Nivel de confianza en la respuesta.
    - session_id: ID de la sesión de chat.
    - timestamp: Timestamp de la respuesta.
    """

    response: str = Field(..., description='La respuesta generada por el asistente.')
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description='Nivel de confianza en la respuesta.'
    )
    session_id: str = Field(..., description='ID de la sesión de chat.')
    timestamp: datetime = Field(
        default_factory=get_colombia_time, description='Timestamp de la respuesta.'
    )
    sources: list[BasicSource] = Field(
        default_factory=list, description='Fuentes de documentos utilizadas.'
    )
    escalation_recommended: bool = Field(
        default=False, description='Indica si se recomienda escalar a un agente humano.'
    )
    full_chat_history: list[ChatMessage] = Field(
        default_factory=list, description='El historial completo y actualizado.'
    )


class UserResponse(BaseModel):
    """
    Respuesta simplificada para datos de usuario.

    - user_id: Identificador único del usuario
    - email: Email del usuario
    - created_at: Fecha de creación del usuario
    - updated_at: Fecha de última actualización
    """

    user_id: str = Field(..., description='Identificador único del usuario')
    email: str = Field(..., description='Email del usuario')
    created_at: datetime = Field(..., description='Fecha de creación del usuario')
    updated_at: datetime = Field(..., description='Fecha de última actualización')


class SessionResponse(BaseModel):
    """
    Respuesta con información de sesión simplificada.

    - session_id: Identificador único de la sesión
    - user_id: Identificador del usuario
    - status: Estado actual de la sesión
    - created_at: Fecha de creación
    - updated_at: Fecha de última actualización
    - history_count: Número total de mensajes en la sesión
    """

    session_id: str = Field(..., description='Identificador único de la sesión')
    user_id: str = Field(..., description='Identificador del usuario')
    status: str = Field(..., description='Estado actual de la sesión')
    created_at: datetime = Field(..., description='Fecha de creación')
    updated_at: datetime = Field(..., description='Fecha de última actualización')
    history_count: int = Field(
        default=0, ge=0, description='Número total de mensajes en la sesión'
    )
