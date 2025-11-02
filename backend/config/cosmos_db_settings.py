"""
Configuración para la conexión a Azure Cosmos DB.

Permite configurar la conexión a Azure Cosmos DB, incluyendo la cadena de conexión,
el nombre de la base de datos, las colecciones de sesiones y usuarios, y el tiempo de vida
(TTL) de los documentos.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CosmosDBSettings(BaseSettings):
    """
    Configuración de la conexión a Azure Cosmos DB.

    - connection_string: Cadena de conexión a Azure Cosmos DB
    - database_name: Nombre de la base de datos de Azure Cosmos DB
    - collection_sessions: Nombre de la colección de sesiones de Azure Cosmos DB
    - collection_users: Nombre de la colección de usuarios de Azure Cosmos DB
    """

    model_config = SettingsConfigDict(extra='ignore', case_sensitive=False)
    connection_string: str = Field(validation_alias='COSMOS_DB_CONNECTION_STRING')
    database_name: str = Field(validation_alias='COSMOS_DB_DATABASE_NAME')
    collection_sessions: str = Field(validation_alias='COSMOS_DB_COLLECTION_SESSIONS')
    collection_users: str = Field(validation_alias='COSMOS_DB_COLLECTION_USERS')
    ttl_seconds: int | None = Field(
        default=86400, validation_alias='COSMOS_DB_TTL_SECONDS'
    )
