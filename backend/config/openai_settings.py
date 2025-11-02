"""
Configuración para la conexión a Azure OpenAI.

Permite configurar la conexión a Azure OpenAI, incluyendo la clave de API,
la URL de la API, la versión de la API, los nombres de los modelos de chat y
embedding, y la temperatura para la generación de texto.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAISettings(BaseSettings):
    """
    Configuración de la conexión a Azure OpenAI.

    - api_key: Clave de API de Azure OpenAI
    - endpoint: URL de la API de Azure OpenAI
    - api_version: Versión de la API de Azure OpenAI
    - chat_deployment_name: Nombre del modelo de chat de Azure OpenAI
    - embedding_deployment_name: Nombre del modelo de embedding de Azure OpenAI
    - temperature: Temperatura para la generación de texto
    """

    model_config = SettingsConfigDict(extra='ignore', case_sensitive=False)
    api_key: str = Field(validation_alias='AZURE_OPENAI_API_KEY')
    endpoint: str = Field(validation_alias='AZURE_OPENAI_ENDPOINT')
    api_version: str = Field(validation_alias='AZURE_OPENAI_API_VERSION')
    chat_deployment_name: str = Field(
        validation_alias='AZURE_OPENAI_CHAT_DEPLOYMENT_NAME'
    )
    embedding_deployment_name: str = Field(
        validation_alias='AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME'
    )
    temperature: float = Field(
        default=0.0, validation_alias='AZURE_OPENAI_TEMPERATURE', ge=0.0, le=2.0
    )
