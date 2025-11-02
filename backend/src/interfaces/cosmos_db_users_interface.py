"""
Interfaz para operaciones de usuarios en Cosmos DB.

Este módulo define el contrato para operaciones de persistencia de usuarios.
"""

from typing import Protocol, runtime_checkable

from backend.src.models.common import User


@runtime_checkable
class CosmosDBUsersInterface(Protocol):
    """
    Define la interfaz para las operaciones de persistencia de usuarios en Cosmos DB.

    Abstrae de métodos para crear y recuperar información de usuarios,
    abstrae la capa de datos de usuario y permite la gestión flexible de credenciales.
    """

    async def create_user(self, email: str, password: str) -> User:
        """
        Crear un nuevo usuario con email y contraseña.

        Args:
            email: Dirección de email del usuario.
            password: Contraseña del usuario (debería estar hasheada).

        Returns:
            Objeto de usuario creado.
        """
        ...

    async def get_user_by_id(self, user_id: str) -> User | None:
        """
        Recuperar un usuario por su ID.

        Args:
            user_id: Identificador único del usuario.

        Returns:
            Objeto de usuario si se encuentra, None en caso contrario.
        """
        ...

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Recuperar un usuario por su dirección de email.

        Args:
            email: Dirección de email a buscar.

        Returns:
            Objeto de usuario si se encuentra, None en caso contrario.
        """
        ...

    async def close(self) -> None:
        """Cerrar la conexión a la base de datos y limpiar recursos."""
        ...
