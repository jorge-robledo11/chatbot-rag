"""
Módulo centralizado para gestión de toda la infraestructura del proyecto.

- AsyncOpenAI
- SearchAI (async) [PDF y Web independientes]
- BlobStorage (async)
- CosmosDBSessions (async)
- CosmosDBUsers (async)
- RAGService (async)
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar, cast

from loguru import logger

from backend.config.settings import get_settings
from backend.src.infrastructure.blob_storage import BlobStorage
from backend.src.infrastructure.cosmos_db_sessions import CosmosDBSessions
from backend.src.infrastructure.cosmos_db_users import CosmosDBUsers
from backend.src.infrastructure.openai import OpenAI
from backend.src.infrastructure.searchai import SearchAI
from backend.src.services.rag_service import RAGService

T = TypeVar('T')


class Infrastructure:
    """
    Contenedor singleton para la infraestructura.

    Proporciona acceso centralizado a todos los servicios asíncronos.
    """

    _instance: 'Infrastructure | None' = None

    def __new__(cls) -> 'Infrastructure':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, '_initialized'):
            return

        self.settings = get_settings()

        # Placeholders
        self._openai: OpenAI | None = None

        # 🔀 SearchAI separados por tipo de índice
        self._searchai_pdf: SearchAI | None = None
        self._searchai_web: SearchAI | None = None

        self._blob_storage: BlobStorage | None = None
        self._cosmos_db_session: CosmosDBSessions | None = None
        self._cosmos_db_user: CosmosDBUsers | None = None
        self._rag_service: RAGService | None = None

        # Locks
        self._lock_openai = asyncio.Lock()

        # Locks independientes para PDF y Web
        self._lock_searchai_pdf = asyncio.Lock()
        self._lock_searchai_web = asyncio.Lock()

        self._lock_blob_storage = asyncio.Lock()
        self._lock_cosmos_db_session = asyncio.Lock()
        self._lock_cosmos_db_user = asyncio.Lock()
        self._lock_rag_service = asyncio.Lock()

        self._initialized = True

    async def _get_service(
        self,
        attr: str,
        lock: asyncio.Lock,
        creator: Callable[[], Awaitable[T]],
    ) -> T:
        svc = cast(T | None, getattr(self, attr, None))
        if svc is None:
            async with lock:
                svc = cast(T | None, getattr(self, attr))
                if svc is None:
                    svc = await creator()
                    setattr(self, attr, svc)
        assert svc is not None
        return svc

    async def get_openai(self) -> OpenAI:
        return await self._get_service(
            '_openai',
            self._lock_openai,
            lambda: OpenAI.create(self.settings.openai),
        )

    async def get_searchai(self, index_type: str = 'pdf') -> SearchAI:
        """
        Devuelve SearchAI singleton para el índice indicado.

        Args:
            index_type: 'pdf' o 'web'.

        Returns:
            SearchAI: Instancia de SearchAI para el índice solicitado.
        """
        index_name = (
            self.settings.search_ai.pdf_index
            if index_type == 'pdf'
            else self.settings.search_ai.web_index
        )

        attr = '_searchai_pdf' if index_type == 'pdf' else '_searchai_web'
        lock = self._lock_searchai_pdf if index_type == 'pdf' else self._lock_searchai_web

        async def create_searchai() -> SearchAI:
            openai_instance = await self.get_openai()
            sa = await SearchAI.create(
                openai_service=openai_instance,
                index_name=index_name,
            )
            logger.success(f"🔗✅ SearchAI inicializado para índice '{index_name}' ({index_type}).")
            return sa

        return await self._get_service(attr, lock, create_searchai)

    # Helpers opcionales por claridad
    async def get_pdf_searchai(self) -> SearchAI:
        return await self.get_searchai('pdf')

    async def get_web_searchai(self) -> SearchAI:
        return await self.get_searchai('web')

    async def get_blob_storage(self) -> BlobStorage:
        return await self._get_service(
            '_blob_storage',
            self._lock_blob_storage,
            lambda: BlobStorage.create(self.settings.blob_storage),
        )

    async def get_cosmos_db_session(self) -> CosmosDBSessions:
        return await self._get_service(
            '_cosmos_db_session',
            self._lock_cosmos_db_session,
            lambda: CosmosDBSessions.create(self.settings.cosmos_db),
        )

    async def get_cosmos_db_user(self) -> CosmosDBUsers:
        return await self._get_service(
            '_cosmos_db_user',
            self._lock_cosmos_db_user,
            lambda: CosmosDBUsers.create(self.settings.cosmos_db),
        )

    async def get_rag_service(self) -> RAGService:
        """
        Crea el RAGService utilizando, por defecto, el índice de PDFs.
        (Las tools específicas pueden solicitar el cliente web con get_web_searchai()).
        """
        async def create_rag_service() -> RAGService:
            search_service = await self.get_pdf_searchai()
            openai_service = await self.get_openai()
            return RAGService(
                search_service=search_service,
                openai_service=openai_service,
                settings=self.settings.rag,
            )

        return await self._get_service(
            '_rag_service',
            self._lock_rag_service,
            create_rag_service,
        )

    async def shutdown(self) -> None:
        logger.info('🔒 Cerrando todos los recursos de Infrastructure...')

        try:
            if self._searchai_pdf:
                await self._searchai_pdf.close()
                logger.info('🔒 SearchAI (PDF) cerrado.')
        except Exception as e:
            logger.error(f'❌ Error cerrando SearchAI (PDF): {e}')

        try:
            if self._searchai_web:
                await self._searchai_web.close()
                logger.info('🔒 SearchAI (Web) cerrado.')
        except Exception as e:
            logger.error(f'❌ Error cerrando SearchAI (Web): {e}')

        try:
            if self._openai:
                await self._openai.close()
                logger.info('🔒 OpenAI cerrado.')
        except Exception as e:
            logger.error(f'❌ Error cerrando OpenAI: {e}')

        try:
            if self._blob_storage:
                await self._blob_storage.close()
                logger.info('🔒 BlobStorage cerrado.')
        except Exception as e:
            logger.error(f'❌ Error cerrando BlobStorage: {e}')

        try:
            if self._cosmos_db_session:
                await self._cosmos_db_session.close()
                logger.info('🔒 CosmosDBSessions cerrado.')
        except Exception as e:
            logger.error(f'❌ Error cerrando CosmosDBSessions: {e}')

        try:
            if self._cosmos_db_user:
                await self._cosmos_db_user.close()
                logger.info('🔒 CosmosDBUsers cerrado.')
        except Exception as e:
            logger.error(f'❌ Error cerrando CosmosDBUsers: {e}')

        logger.success('🔒 Todos los servicios cerrados correctamente.')


_infra_instance: Infrastructure | None = None


def get_infrastructure() -> Infrastructure:
    global _infra_instance
    if _infra_instance is None:
        _infra_instance = Infrastructure()
    return _infra_instance
