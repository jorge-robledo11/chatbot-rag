"""
Implementación de Azure Blob Storage para gestión de archivos y documentos.

Este módulo proporciona una implementación asíncrona de BlobStorageInterface
para interactuar con Azure Blob Storage, incluyendo operaciones de subida,
descarga y listado de blobs.
"""

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient
from loguru import logger

from backend.config import get_settings
from backend.config.settings import BlobStorageSettings
from backend.src.interfaces.blob_storage_interface import BlobStorageInterface

class BlobStorage(BlobStorageInterface):
    """
    Implementación asíncrona para Azure Blob Storage.

    Esta clase gestiona las operaciones de blob (subida, descarga, listado)
    utilizando el SDK asíncrono de Azure y configuraciones a través de
    variables de entorno.
    """

    def __init__(
        self,
        client: BlobServiceClient,
        container_name: str,
    ) -> None:
        """
        Inicializa una nueva instancia de BlobStorage.
        """
        logger.debug(f"Inicializando BlobStorage con contenedor: '{container_name}'.")
        self.client = client
        self.container_name = container_name

    @classmethod
    async def create(cls, settings: BlobStorageSettings | None = None) -> 'BlobStorage':
        """
        Método de fábrica asíncrono para crear y configurar una instancia de BlobStorage.
        """
        logger.debug('Iniciando método de fábrica BlobStorage.create().')
        if settings is None:
            settings = get_settings().blob_storage
        
        if not settings.connection_string:
            logger.error(
                '❌ No se pudo determinar el connection string para Azure Blob Storage. '
                'Verifique sus variables de entorno.'
            )
            raise ValueError('❌ No se pudo determinar el connection string para Azure Blob Storage.')

        client = BlobServiceClient.from_connection_string(settings.connection_string)
        container_name: str = settings.container_name

        try:
            container_client = client.get_container_client(container_name)
            await container_client.create_container()
            logger.success(f"🆕✅ Contenedor '{container_name}' creado exitosamente.")
        except ResourceExistsError:
            logger.info(f"📦✅ Contenedor '{container_name}' ya existe, se usará el existente.")
        except Exception as e:
            logger.error(f"❌ Error al crear o verificar el contenedor '{container_name}': {e}")
            raise

        logger.success(f"🔗✅ BlobServiceClient inicializado para el contenedor '{container_name}'.")
        return cls(client, container_name)

    async def upload_bytes(
        self,
        data: bytes,
        blob_name: str,
        content_type: str,
    ) -> str:
        """
        Sube un conjunto de bytes al contenedor como un blob.
        """
        blob_client = self.client.get_blob_client(container=self.container_name, blob=blob_name)
        content_settings = ContentSettings(content_type=content_type)
        try:
            await blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
            logger.success(f"✅📁 Blob '{blob_name}' subido correctamente.")
            return blob_client.url
        except Exception as e:
            logger.error(f"❌ Error al subir el blob '{blob_name}': {e}")
            raise

    async def upload_image(self, img_bytes: bytes, blob_name: str) -> str:
        """
        Sube bytes de imagen al almacenamiento de blobs.
        """
        return await self.upload_bytes(img_bytes, blob_name, 'image/jpeg')

    async def download_bytes(self, blob_name: str) -> bytes:
        """
        Descarga los datos binarios de un blob específico del contenedor.
        """
        logger.debug(f"⬇️📥 Solicitando descarga del blob '{blob_name}'.")
        blob_client = self.client.get_blob_client(container=self.container_name, blob=blob_name)
        try:
            downloader = await blob_client.download_blob()
            data: bytes = await downloader.readall()
            logger.success(f"✅📥 Blob '{blob_name}' descargado correctamente. Tamaño: {len(data)} bytes.")
            return data
        except Exception as e:
            logger.error(f"❌ Error al descargar el blob '{blob_name}': {e}")
            raise

    async def list_blobs(self, prefix: str | None = None) -> list[dict]:
        """
        Lista todos los blobs con filtro opcional de prefijo.

        Args:
            prefix: Prefijo opcional para filtrar blobs.

        Returns:
            Lista de diccionarios, cada uno representando las propiedades de un blob (ej. {'name': ...}).
        """
        logger.debug(f"📋 Listando blobs con prefijo: '{prefix or 'ninguno'}'")
        container_client = self.client.get_container_client(self.container_name)
        try:
            blobs_list = []
            async for blob in container_client.list_blobs(name_starts_with=prefix):
                blobs_list.append({'name': blob.name})
            logger.success(f'📋✅ Encontrados {len(blobs_list)} blobs.')
            return blobs_list
        except Exception as e:
            logger.error(f'❌ Error listando blobs: {e}')
            raise

    async def close(self) -> None:
        """
        Cierra el cliente de Blob Storage, liberando los recursos de conexión.
        """
        logger.debug(f"🔒 Solicitando cierre del cliente de blob storage para el contenedor '{self.container_name}'.")
        try:
            await self.client.close()
            logger.success('🔒✅ Cliente de blob storage cerrado correctamente.')
        except Exception as e:
            logger.error(f'❌ Error al cerrar el cliente de blob storage: {e}')
            raise
