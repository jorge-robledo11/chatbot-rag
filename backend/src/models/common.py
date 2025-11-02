"""
Modelos comunes simplificados para el sistema de chat.

Este módulo elimina la complejidad de tipos de usuario
y mantiene solo los modelos esenciales.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class UserType(StrEnum):
    """
    Enumera los tipos de usuario disponibles en el sistema.

    - EXTERNAL: Usuarios externos del cliente
    - INTERNAL: Usuarios internos de la empresa
    - ADMIN: Administradores del sistema
    """

    EXTERNAL = 'external'
    INTERNAL = 'internal'
    ADMIN = 'admin'


class QueryType(StrEnum):
    """
    Tipos de consulta disponibles en el sistema.

    - PDF: Consultas pdf
    - WEB: Consultas web
    """
    
    PDF = 'pdf'
    WEB = 'web'


class Priority(StrEnum):
    """
    Niveles de prioridad para procesamiento.

    - LOW: Baja prioridad
    - NORMAL: Prioridad normal
    - HIGH: Alta prioridad
    """

    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'


class SessionStatus(StrEnum):
    """
    Estados posibles de una sesión.

    - ACTIVE: Sesión activa
    - INACTIVE: Sesión inactiva
    - ENDED: Sesión finalizada
    """

    ACTIVE = 'active'
    INACTIVE = 'inactive'
    ENDED = 'ended'


class MessageRole(StrEnum):
    """
    Roles de mensajes en el chat.

    - USER: Usuario
    - ASSISTANT: Asistente
    - SYSTEM: Sistema
    """

    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'


class ChatMessage(BaseModel):
    """
    Mensaje individual en una conversación de chat.

    - role: Rol del mensaje
    - content: Contenido del mensaje
    - timestamp: Momento en que se creó el mensaje
    """

    role: MessageRole | None = Field(None, description='Rol del mensaje')
    content: str | None = Field(None, description='Contenido del mensaje')
    timestamp: datetime | None = Field(
        default_factory=datetime.now,
        description='Momento en que se creó el mensaje',
    )


class BasicSource(BaseModel):
    """
    Fuente básica de información para respuestas RAG.

    - document_id: ID único del documento
    - title: Título o nombre del documento
    - excerpt: Extracto relevante del contenido
    - source_type: Tipo de fuente
    - source_file: Nombre del archivo fuente
    """

    document_id: str | None = Field(None, description='ID único del documento')
    title: str | None = Field(None, description='Título o nombre del documento')
    excerpt: str | None = Field(None, description='Extracto relevante del contenido')
    source_type: str | None = Field(None, description='Tipo de fuente')
    source_file: str | None = Field(None, description='Nombre del archivo fuente')


class User(BaseModel):
    """
    Modelo simplificado de usuario.

    - user_id: Identificador único del usuario
    - email: Email del usuario
    - hashed_password: Contraseña hasheada
    - created_at: Fecha de creación
    - updated_at: Fecha de última actualización
    """

    user_id: str | None = Field(None, description='Identificador único del usuario')
    email: str | None = Field(None, description='Email del usuario')
    hashed_password: str | None = Field(None, description='Contraseña hasheada')
    created_at: datetime | None = Field(
        default_factory=datetime.now,
        description='Fecha de creación',
    )
    updated_at: datetime | None = Field(
        default_factory=datetime.now,
        description='Fecha de última actualización',
    )


class Session(BaseModel):
    """
    Modelo simplificado de sesión.

    - session_id: Identificador único
    - user_id: ID del usuario
    - status: Estado de la sesión
    - chat_history: Historial de mensajes
    - created_at: Fecha de creación
    - updated_at: Fecha de última actualización
    """

    session_id: str | None = Field(None, description='Identificador único')
    user_id: str | None = Field(None, description='ID del usuario')
    status: SessionStatus | None = Field(
        default=SessionStatus.ACTIVE,
        description='Estado de la sesión',
    )
    chat_history: list[ChatMessage] | list = Field(
        default_factory=list,
        description='Historial de mensajes',
    )
    created_at: datetime | None = Field(
        default_factory=datetime.now,
        description='Fecha de creación',
    )
    updated_at: datetime | None = Field(
        default_factory=datetime.now,
        description='Fecha de última actualización',
    )
