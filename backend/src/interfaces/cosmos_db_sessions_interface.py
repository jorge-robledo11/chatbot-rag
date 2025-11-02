"""
Interfaz para operaciones de sesiones en Cosmos DB.

Este módulo define el contrato para persistencia de sesiones de chat.
"""

from typing import Protocol, runtime_checkable

from backend.src.models.common import ChatMessage, Session, SessionStatus


@runtime_checkable
class CosmosDBSessionsInterface(Protocol):
    """
    Define la interfaz para las operaciones de persistencia de sesiones de chat en Cosmos DB.

    Abstrae el acceso a los datos de sesión (creación, recuperación, adición de mensajes,
    actualización de estado y limpieza de historial), facilitando la gestión de la
    conversación y la independencia de la implementación de la base de datos.
    """

    async def create_session(self, user_id: str) -> Session:
        """
        Crear una nueva sesión de chat.

        Args:
            user_id: Identificador del usuario que crea la sesión.

        Returns:
            Objeto de sesión creado.
        """
        ...

    async def get_session(self, session_id: str) -> Session | None:
        """
        Recuperar una sesión por su ID.

        Args:
            session_id: Identificador único de la sesión.

        Returns:
            Objeto de sesión si se encuentra, None en caso contrario.
        """
        ...

    async def add_message_to_history(
        self, session_id: str, message: ChatMessage
    ) -> Session:
        """
        Añadir un mensaje al historial de la sesión.

        Args:
            session_id: ID de la sesión a actualizar.
            message: Mensaje de chat a añadir.

        Returns:
            Sesión actualizada con el nuevo mensaje.
        """
        ...

    async def update_session_status(
        self, session_id: str, status: SessionStatus
    ) -> Session:
        """
        Actualizar el estado de una sesión.

        Args:
            session_id: ID de la sesión a actualizar.
            status: Nuevo estado para la sesión.

        Returns:
            Objeto de sesión actualizado.
        """
        ...

    async def clear_history(self, session_id: str) -> Session:
        """
        Limpiar el historial de mensajes de una sesión.

        Args:
            session_id: ID de la sesión a limpiar.

        Returns:
            Sesión con historial limpiado.
        """
        ...

    async def close(self) -> None:
        """Cerrar la conexión a la base de datos y limpiar recursos."""
        ...
