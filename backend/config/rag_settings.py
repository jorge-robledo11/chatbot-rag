"""
Configuraciones específicas para el servicio RAG.

Permite configurar el servicio RAG, incluyendo el número máximo de tokens en el contexto,
el umbral de confianza para la respuesta, y el número de resultados a buscar.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGSettings(BaseSettings):
    """
    Configuraciones específicas para el servicio RAG.

    - max_context_tokens: Número máximo de tokens en el contexto
    - confidence_threshold: Umbral de confianza para la respuesta
    - search_top_k: Número de resultados a buscar
    - pdf_response_max_tokens: Tokens máximos para respuestas pdf
    - web_response_max_tokens: Tokens máximos para respuestas web
    """

    model_config = SettingsConfigDict(extra='ignore', case_sensitive=False)
    confidence_threshold: float = Field(
        default=0.6, validation_alias='RAG_CONFIDENCE_THRESHOLD'
    )
    search_top_k: int = Field(default=8, validation_alias='RAG_SEARCH_TOP_K')
    pdf_response_max_tokens: int = Field(
        default=4096, validation_alias='RAG_PDF_RESPONSE_MAX_TOKENS'
    )
    web_response_max_tokens: int = Field(
        default=2048, validation_alias='RAG_WEB_RESPONSE_MAX_TOKENS'
    )
