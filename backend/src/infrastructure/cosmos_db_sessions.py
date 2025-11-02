"""
Gestor de sesiones basado en Cosmos DB (API Mongo).

• Singleton asíncrono
• Sin creación de índices en caliente
• La colección se crea solo si no existe.
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
from backend.config.settings import CosmosDBSettings
from backend.src.interfaces.cosmos_db_sessions_interface import (
    CosmosDBSessionsInterface,
)
from backend.src.models.common import ChatMessage, Session, SessionStatus, UserType
from backend.src.utils.identity_utils import generate_secure_session_id
from backend.src.utils.time_utils import get_colombia_time
from backend.src.utils.validation_utils import validate_session_id_format


async def _get_or_create_collection(
    db: AsyncIOMotorDatabase,
    name: str,
) -> AsyncIOMotorCollection:
    """
    Devuelve la colección; si no existe, la crea.

    Args:
        db: Instancia de AsyncIOMotorDatabase.
        name: Nombre de la colección.

    Returns:
        La colección existente o recién creada.
    """
    try:
        return db.get_collection(name)
    except CollectionInvalid:
        logger.warning("📁 Colección '%s' no existe, creándola…", name)
        await db.create_collection(name)
        return db.get_collection(name)


class CosmosDBSessions(CosmosDBSessionsInterface):
    """
    Gestor de sesiones basado en Cosmos DB (API Mongo).

    • Singleton asíncrono
    • Sin creación de índices en caliente
    • La colección se crea solo si no existe.
    """

    _client: AsyncIOMotorClient | None = None
    _collection: AsyncIOMotorCollection | None = None
    _instance: CosmosDBSessions | None = None
    _init_lock: Final[asyncio.Lock] = asyncio.Lock()

    @classmethod
    async def create(
        cls,
        settings: CosmosDBSettings | None = None,
    ) -> CosmosDBSessions:
        """
        Crea o devuelve la instancia singleton de CosmosDBSessions.

        Args:
            settings: Configuración de Cosmos DB; si no se proporciona, se carga de entorno.

        Returns:
            La instancia singleton de CosmosDBSessions.

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
                db, settings.collection_sessions
            )
            logger.success(
                f"🔗✅ CosmosDBSessions listo (DB='{settings.database_name}', "
                f"Coll='{settings.collection_sessions}')."
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
            La colección de MongoDB.

        Raises:
            RuntimeError: Si la colección no ha sido inicializada.
        """
        if self._collection is None:
            raise RuntimeError('Colección no inicializada')
        return self._collection

    async def create_session(self, user_id: str) -> Session:
        """
        Crea y persiste una nueva sesión.

        Args:
            user_id: Identificador del usuario que abre la sesión.

        Returns:
            La sesión recién creada.
        """
        sess_id = generate_secure_session_id()
        sess = Session(
            session_id=sess_id,
            user_id=user_id,
            user_type=UserType.EXTERNAL,
        )
        await self._col().insert_one(sess.model_dump(mode='json') | {'_id': sess_id})
        logger.success(f'🆕 Sesión creada id={sess_id}')
        return sess

    async def get_session(self, session_id: str) -> Session | None:
        """
        Recupera una sesión por su ID.

        Args:
            session_id: Identificador de la sesión.

        Returns:
            La sesión encontrada, o None si no existe.

        Raises:
            ValueError: Si el formato de session_id es inválido.
        """
        if not validate_session_id_format(session_id):
            raise ValueError(f'session_id inválido: {session_id}')
        if doc := await self._col().find_one({'_id': session_id}):
            return Session(**doc)
        return None

    async def add_message_to_history(
        self,
        session_id: str,
        message: ChatMessage,
    ) -> Session:
        """
        Agrega un mensaje al historial de la sesión.

        Args:
            session_id: Identificador de la sesión.
            message: Instancia de ChatMessage a añadir.

        Returns:
            La sesión actualizada tras el push del mensaje.

        Raises:
            ValueError: Si la sesión no existe.
        """
        updated = await self._col().find_one_and_update(
            {'_id': session_id},
            {
                '$push': {'chat_history': message.model_dump(mode='json')},
                '$set': {'updated_at': get_colombia_time().isoformat()},
            },
            return_document=True,
        )
        if not updated:
            raise ValueError(f"Sesión '{session_id}' no encontrada")
        return Session(**updated)

    async def update_session_status(
        self,
        session_id: str,
        status: SessionStatus,
    ) -> Session:
        """
        Actualiza el estado de una sesión.

        Args:
            session_id: Identificador de la sesión.
            status: Nuevo estado para la sesión.

        Returns:
            La sesión con el nuevo estado.

        Raises:
            ValueError: Si la sesión no existe.
        """
        updated = await self._col().find_one_and_update(
            {'_id': session_id},
            {
                '$set': {
                    'status': status.value,
                    'updated_at': get_colombia_time().isoformat(),
                },
            },
            return_document=True,
        )
        if not updated:
            raise ValueError(f"Sesión '{session_id}' no encontrada")
        return Session(**updated)

    async def clear_history(self, session_id: str) -> Session:
        """
        Elimina todo el historial de una sesión.

        Args:
            session_id: Identificador de la sesión.

        Returns:
            La sesión tras limpiar su historial.

        Raises:
            ValueError: Si la sesión no existe.
        """
        updated = await self._col().find_one_and_update(
            {'_id': session_id},
            {
                '$set': {
                    'chat_history': [],
                    'updated_at': get_colombia_time().isoformat(),
                },
            },
            return_document=True,
        )
        if not updated:
            raise ValueError(f"Sesión '{session_id}' no encontrada")
        return Session(**updated)

    @classmethod
    async def close(cls) -> None:
        """
        Cierra el cliente de Cosmos DB, liberando los recursos de conexión.

        Es una buena práctica llamar a este método cuando la instancia de CosmosDBSessions
        ya no es necesaria para asegurar una limpieza adecuada.
        """
        if cls._client:
            cls._client.close()
            cls._client = None
            logger.success('🔒 Cliente CosmosDBSessions cerrado.')
