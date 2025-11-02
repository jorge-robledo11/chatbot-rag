"""
Configuración principal del proyecto Ajover.

Incluye todas las configuraciones de servicios y recursos.
"""

import sys

from azure.identity import DefaultAzureCredential
from loguru import logger
from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .blob_storage_settings import BlobStorageSettings
from .cosmos_db_settings import CosmosDBSettings
from .identity_settings import IdentitySettings
from .logging_settings import LoguruSettings
from .openai_settings import OpenAISettings
from .rag_settings import RAGSettings
from .searchai_settings import SearchAISettings


class Settings(BaseSettings):
    """
    Configuración principal que engloba todos los servicios de Azure.

    - openai: Configuración de la conexión a Azure OpenAI
    - search_ai: Configuración de la conexión a Azure Search AI
    - blob_storage: Configuración de la conexión a Azure Blob Storage
    - identity: Configuración de la conexión a Azure
    - cosmos_db: Configuración de la conexión a Azure Cosmos DB
    - rag: Configuración de la conexión a Azure RAG
    - logging: Configuración de la conexión a Loguru
    """

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra='ignore',
        env_nested_delimiter='__',
    )

    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    search_ai: SearchAISettings = Field(default_factory=SearchAISettings)
    blob_storage: BlobStorageSettings = Field(default_factory=BlobStorageSettings)
    identity: IdentitySettings = Field(default_factory=IdentitySettings)
    cosmos_db: CosmosDBSettings = Field(default_factory=CosmosDBSettings)
    rag: RAGSettings = Field(default_factory=RAGSettings)
    logging: LoguruSettings = Field(default_factory=LoguruSettings)

    _cached_credential: DefaultAzureCredential | None = None

    def get_credential(self) -> DefaultAzureCredential:
        """
        Obtiene la credencial de Azure.

        Returns:
            DefaultAzureCredential: La credencial de Azure.
        """
        if self._cached_credential is None:
            self._cached_credential = DefaultAzureCredential()
        return self._cached_credential

    @model_validator(mode='after')
    def log_successful_load(self) -> 'Settings':
        """
        Loguea un mensaje de éxito cuando todas las configuraciones han sido cargadas y validadas con éxito.

        Returns:
            Settings: La instancia de configuración cargada y validada.
        """
        logger.success(
            '✅ Todas las configuraciones han sido cargadas y validadas con éxito.'
        )
        return self


_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """
    Función singleton para obtener la configuración global.

    Returns:
        Settings: La instancia de configuración cargada y validada.
    """
    global _settings_instance
    if _settings_instance is None:
        try:
            _settings_instance = Settings()
        except ValidationError as e:
            logger.critical(
                '❌ Error Crítico: Faltan variables de entorno o la configuración es inválida.'
            )
            logger.critical(f'Detalles del error de validación:\n{e}')
            sys.exit(1)
    return _settings_instance
