"""
Implementación de la interfaz SearchAIInterface para Azure AI Search.

Esta clase encapsula la lógica para realizar búsquedas híbridas (texto y vectores)
en el índice de búsqueda de Azure AI Search, así como la gestión de documentos
y metadatos. Incluye funcionalidades para crear y mantener el índice, gestionar
documentos, y realizar búsquedas vectoriales.
"""

import json
import os
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery
from loguru import logger

from backend.config import get_settings
from backend.src.interfaces.openai_interface import OpenAIInterface
from backend.src.interfaces.searchai_interface import SearchAIInterface


class SearchAI(SearchAIInterface):
    """
    Implementación de la interfaz SearchAIInterface para Azure AI Search.
    """

    def __init__(
        self,
        index_client: SearchIndexClient,
        openai_service: OpenAIInterface,
        index_name: str,
    ) -> None:
        """
        Inicializa una instancia de SearchAI.
        """
        self.index_client = index_client
        self.openai_service = openai_service
        self.index_name = index_name
        self.search_client = SearchClient(
            index_client._endpoint,
            index_name,
            index_client._credential,
        )
        logger.debug(
            f"Clientes de Search AI para índice '{index_name}' asignados."
        )

    @classmethod
    async def create(
        cls,
        openai_service: OpenAIInterface,
        index_name: str,
    ) -> 'SearchAI':
        """
        Crea una instancia de SearchAI para un índice específico.
        """
        settings = get_settings().search_ai
        endpoint = settings.endpoint
        api_key = settings.api_key
        if not api_key or not endpoint:
            logger.error('❌🔑 AZURE_SEARCH_AI_ENDPOINT y API_KEY son obligatorios.')
            raise ValueError('Configuración de Azure Search incompleta.')
        credential = AzureKeyCredential(api_key)
        index_client = SearchIndexClient(endpoint, credential)
        logger.success(
            f"🔗✅ Clientes de Azure Search AI inicializados para índice '{index_name}'."
        )
        return cls(index_client, openai_service, index_name)

    async def create_index_if_not_exists(self) -> None:
        """
        Crea o actualiza idempotentemente el índice.
        Si el nombre contiene 'pdf' → esquema PDF; en otro caso → esquema Web.
        """
        index_name = self.index_name
        logger.info(f"⚙️📝 Creando/actualizando índice híbrido: '{index_name}'…")

        # Configuración vectorial (común)
        vector_search = VectorSearch(
            algorithms=[HnswAlgorithmConfiguration(
                name='hnsw-config', kind='hnsw', parameters={'metric': 'cosine'}
            )],
            profiles=[VectorSearchProfile(
                name='hnsw-profile', algorithm_configuration_name='hnsw-config'
            )],
        )

        name_lc = (index_name or '').lower()

        if 'pdf' in name_lc:
            # --------- Esquema PDF (tu esquema original) ----------
            fields = [
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True
                ),
                SimpleField(
                    name="parent_document_id",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    facetable=True
                ),
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    analyzer_name="es.microsoft"
                ),
                SearchableField(
                    name="source_file",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    sortable=True
                ),
                SimpleField(
                    name="source_file_hash",
                    type=SearchFieldDataType.String,
                    filterable=True
                ),
                SimpleField(
                    name="chunk_number",
                    type=SearchFieldDataType.Int32,
                    filterable=True,
                    sortable=True
                ),
                SimpleField(  # colección de strings
                    name="image_descriptions",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                    filterable=False,
                    sortable=False,
                    facetable=False,
                    searchable=True,
                    analyzer_name="es.microsoft"
                ),
                SimpleField(  # colección de strings
                    name="image_urls",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                    filterable=False,
                    sortable=False,
                    facetable=False,
                    searchable=False
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="hnsw-profile"
                ),
            ]
        else:
            # --------- Esquema Web ----------
            fields = [
                SimpleField(
                    name="id",
                    type=SearchFieldDataType.String,
                    key=True,
                    filterable=True
                ),
                SearchableField(
                    name="title",
                    type=SearchFieldDataType.String,
                    analyzer_name="es.microsoft"
                ),
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    analyzer_name="es.microsoft"
                ),
                SimpleField(
                    name="source",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    facetable=True,
                    sortable=True
                ),
                SimpleField(
                    name="source_url",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    sortable=True
                ),
                SearchField(
                    name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="hnsw-profile"
                ),
            ]

        index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
        await self.index_client.create_or_update_index(index)
        logger.success(f"🟢✅ Índice '{index_name}' creado/actualizado correctamente.")

    async def hybrid_search(self, query: str, top_k: int) -> list[dict]:
        logger.info(f"🔎🤖 Búsqueda híbrida: '{query[:50]}...' (top_k={top_k})")
        query_vector = await self.openai_service.get_text_embedding(query)
        vector_queries = [
            VectorizedQuery(vector=query_vector, k_nearest_neighbors=top_k, fields='content_vector')
        ] if query_vector else None

        name_lc = (self.index_name or '').lower()
        if 'pdf' in name_lc:
            select_fields = [
                'id', 'parent_document_id', 'content', 'source_file', 'chunk_number',
                'image_urls', 'image_descriptions'
            ]
        else:
            select_fields = [
                'id', 'title', 'content', 'source', 'source_url'
            ]

        results = []
        try:
            async for r in await self.search_client.search(
                search_text=query,
                vector_queries=vector_queries,
                top=top_k,
                select=select_fields,
            ):
                results.append(r)
            logger.success(f'🔍✅ Se devolvieron {len(results)} resultados.')
        except Exception as e:
            logger.error(f'❌ Error en búsqueda: {e}', exc_info=True)
        return results

    async def upload_documents_batch(self, documents: list[dict]) -> None:
        """
        Sube un lote de documentos al índice y guarda un dump en index.json en la raíz.
        """
        logger.info(f'⬆️📦 Subiendo {len(documents)} documentos...')

        # Dump de los documentos a index.json
        try:
            dump_path = os.path.join(os.getcwd(), 'index.json')
            with open(dump_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            logger.info(f'💾✅ Documentos volcados en {dump_path}')
        except Exception as e:
            logger.warning(f'⚠️ No se pudo escribir el dump de documentos: {e}')

        try:
            await self.search_client.upload_documents(documents=documents)
            logger.success('⬆️✅ Lote subido correctamente.')
        except HttpResponseError as e:
            logger.error(
                f'❌ Error subiendo lote: {e}\n'
                f'Detalles HTTP: status_code={e.status_code}, error={e.message}'
            )
            raise
        except Exception as e:
            logger.error(f'❌ Excepción inesperada al subir lote: {e}', exc_info=True)
            raise

    async def close(self) -> None:
        logger.info('🔒 Cerrando clientes Search AI y OpenAI...')
        try:
            await self.search_client.close()
            await self.index_client.close()
            if self.openai_service:
                await self.openai_service.close()
            logger.success('🔒✅ Clientes cerrados.')
        except Exception as e:
            logger.error(f'❌ Error cerrando clientes: {e}', exc_info=True)
            raise
