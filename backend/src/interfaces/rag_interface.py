"""
Interfaz para operaciones RAG (Retrieval-Augmented Generation).

Este módulo define el contrato para procesamiento de consultas RAG.
"""

from typing import Protocol, runtime_checkable

from backend.src.models.requests import BaseQueryRequest
from backend.src.models.responses import BaseQueryResponse


@runtime_checkable
class RAGInterface(Protocol):
    """
    Define la interfaz para el sistema RAG (Retrieval-Augmented Generation).

    Establece el contrato para procesar consultas enriquecidas mediante
    la recuperación de información y la generación de respuestas.
    """

    async def process_query(self, request: BaseQueryRequest) -> BaseQueryResponse:
        """
        Procesar una consulta usando metodología RAG.

        Args:
            request: Solicitud de consulta con entrada del usuario y contexto.

        Returns:
            Respuesta con respuesta generada y contexto recuperado.
        """
        ...
