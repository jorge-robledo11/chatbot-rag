"""
Configuración para la conexión a Azure Blob Storage.

Permite configurar la conexión a Azure Blob Storage, incluyendo la cadena de conexión,
la URL de la cuenta, el nombre del contenedor, los prefijos de las carpetas de origen
e imágenes, y el tiempo de vida (TTL) de los documentos.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BlobStorageSettings(BaseSettings):
    """
    Configuración de la conexión a Azure Blob Storage.

    - connection_string: Cadena de conexión a Azure Blob Storage
    - account_url: URL de la cuenta de Azure Blob Storage
    - container_name: Nombre del contenedor de Azure Blob Storage
    - source_prefix: Prefijo de la carpeta de origen en Azure Blob Storage
    - images_prefix: Prefijo de la carpeta de imágenes en Azure Blob Storage
    """

    model_config = SettingsConfigDict(extra='ignore', case_sensitive=False)
    connection_string: str | None = Field(
        validation_alias='BLOB_STORAGE_CONNECTION_STRING'
    )
    account_url: str | None = Field(validation_alias='BLOB_STORAGE_URL')
    container_name: str = Field(validation_alias='BLOB_STORAGE_CONTAINER_NAME')
    source_prefix: str = Field(validation_alias='BLOB_STORAGE_SOURCE_PREFIX')
    images_prefix: str = Field(validation_alias='BLOB_STORAGE_IMAGES_PREFIX')
