"""
Configuración para la conexión a Azure Search AI.

Permite configurar la conexión a Azure Search AI, incluyendo la URL de la API,
la clave de API, y los nombres de los índices de PDF y web.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SearchAISettings(BaseSettings):
    """
    Configuración de la conexión a Azure Search AI.

    - endpoint: URL de la API de Azure Search AI
    - api_key: Clave de API de Azure Search AI
    - pdf_index: Nombre del índice de PDF de Azure Search AI
    - web_index: Nombre del índice de web de Azure Search AI
    """

    model_config = SettingsConfigDict(extra='ignore', case_sensitive=False)
    endpoint: str = Field(validation_alias='AZURE_SEARCH_AI_ENDPOINT')
    api_key: str = Field(validation_alias='AZURE_SEARCH_AI_API_KEY')
    pdf_index: str = Field(validation_alias='AZURE_SEARCH_AI_PDF_INDEX')
    web_index: str = Field(validation_alias='AZURE_SEARCH_AI_WEB_INDEX')

