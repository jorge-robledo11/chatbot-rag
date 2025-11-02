"""
Gestor de usuarios basado en Cosmos DB (API Mongo).

Singleton asíncrono. Índices únicos pre-provisionados.
"""

from __future__ import annotations

import asyncio
from typing import Final

from loguru import logger
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
from pymongo.errors import CollectionInvalid

from backend.config import get_settings
from backend.config.cosmos_db_settings import CosmosDBSettings
from backend.src.interfaces.cosmos_db_users_interface import CosmosDBUsersInterface
from backend.src.models.common import User
from backend.src.utils.identity_utils import generate_deterministic_id
from backend.src.utils.security_utils import get_password_hash


async def _get_or_create_collection(
    db: AsyncIOMotorDatabase,
    name: str,
) -> AsyncIOMotorCollection:
    """
    Obtiene o crea la colección indicada.

    Args:
        db: Instancia de AsyncIOMotorDatabase.
        name: Nombre de la colección.

    Returns:
        Colección existente o recién creada.
    """
    try:
        return db.get_collection(name)
    except CollectionInvalid:
        logger.warning(f"📁 Colección '{name}' no existe, creándola…")
        await db.create_collection(name)
        return db.get_collection(name)


class CosmosDBUsers(CosmosDBUsersInterface):
    """
    Gestor de usuarios basado en Cosmos DB (API Mongo).

    Singleton asíncrono. Índices únicos pre-provisionados.
    """

    _client: AsyncIOMotorClient | None = None
    _collection: AsyncIOMotorCollection | None = None
    _instance: CosmosDBUsers | None = None
    _init_lock: Final[asyncio.Lock] = asyncio.Lock()

    @classmethod
    async def create(
        cls,
        settings: CosmosDBSettings | None = None,
    ) -> CosmosDBUsers:
        """
        Crea o devuelve la instancia singleton de CosmosDBUsers.

        Args:
            settings: Configuración de Cosmos DB; si no se proporciona, se carga de entorno.

        Returns:
            Instancia singleton de CosmosDBUsers.

        Raises:
            ValueError: Si no está configurada la cadena de conexión.
        """
        if cls._instance is not None:
            return cls._instance

        async with cls._init_lock:
            if cls._instance is not None:
                return cls._instance

            settings = settings or get_settings().cosmos_db
            connection_string = settings.connection_string
            if not connection_string:
                raise ValueError('COSMOS_DB_CONNECTION_STRING no configurada')

            cls._client = AsyncIOMotorClient(connection_string, tls=True)
            db = cls._client[settings.database_name]
            cls._collection = await _get_or_create_collection(
                db,
                settings.collection_users,
            )
            logger.success(
                f"🔗✅ CosmosDBUsers listo (DB='{settings.database_name}', Coll='{settings.collection_users}').",
                settings.database_name,
                settings.collection_users,
            )
            cls._instance = cls(cls._collection)
            return cls._instance

    def __init__(self, collection: AsyncIOMotorCollection) -> None:
        """
        Inicializa la instancia con la colección indicada.

        Args:
            collection: Colección de MongoDB a usar.
        """
        self._collection = collection

    def _col(self) -> AsyncIOMotorCollection:
        """
        Obtiene la colección inicializada.

        Returns:
            Colección de MongoDB.

        Raises:
            RuntimeError: Si la colección no ha sido inicializada.
        """
        if self._collection is None:
            raise RuntimeError('Colección no inicializada')
        return self._collection

    async def create_user(
        self,
        email: str,
        password: str,
    ) -> User:
        """
        Crea y persiste un nuevo usuario.

        Args:
            email: Correo electrónico del usuario.
            password: Contraseña en texto plano.

        Returns:
            Usuario recién creado.

        Raises:
            ValueError: Si el email ya está registrado.
        """
        user = User(
            user_id=generate_deterministic_id(email),
            email=email,
            hashed_password=get_password_hash(password),
        )
        try:
            await self._col().insert_one(
                user.model_dump(mode='json') | {'_id': user.user_id}
            )
            logger.success(f'👤 Usuario creado email={email}')
            return user
        except Exception as exc:
            logger.error(f'❌ Error al crear usuario {email}: {exc}')
            raise ValueError('El email ya está registrado') from exc

    async def get_user_by_id(self, user_id: str) -> User | None:
        """
        Recupera un usuario por su ID.

        Args:
            user_id: Identificador del usuario.

        Returns:
            Usuario encontrado o None si no existe.
        """
        if doc := await self._col().find_one({'_id': user_id}):
            return User(**doc)
        return None

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Recupera un usuario por su email.

        Args:
            email: Correo electrónico del usuario.

        Returns:
            Usuario encontrado o None si no existe.
        """
        if doc := await self._col().find_one({'email': email}):
            return User(**doc)
        return None

    @classmethod
    async def close(cls) -> None:
        """
        Cierra el cliente de Cosmos DB, liberando los recursos de conexión.

        Es una buena práctica llamar a este método cuando la instancia de CosmosDBUsers
        ya no es necesaria para asegurar una limpieza adecuada.
        """
        if cls._client:
            cls._client.close()
            cls._client = None
            logger.success('🔒 Cliente CosmosDBUsers cerrado.')
