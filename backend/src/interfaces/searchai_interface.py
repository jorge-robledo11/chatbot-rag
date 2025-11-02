"""
Interfaz para operaciones del servicio de búsqueda IA.

Este módulo define el contrato para funcionalidad de búsqueda inteligente.
"""

from typing import Protocol, runtime_checkable

from langchain_core.tools import BaseTool


@runtime_checkable
class SearchAIInterface(Protocol):
    """
    Define la interfaz para interactuar con un servicio de búsqueda inteligente.

    Proporciona métodos para la gestión de índices, búsqueda híbrida,
    operaciones con documentos y la creación de herramientas de búsqueda.
    """

    async def create_index_if_not_exists(self) -> None:
        """Crear índice de búsqueda si no existe ya."""
        ...

    async def hybrid_search(self, query: str, top_k: int) -> list[dict]:
        """
        Realizar búsqueda híbrida combinando múltiples estrategias de búsqueda.

        Args:
            query: Cadena de consulta de búsqueda.
            top_k: Número de resultados principales a devolver.

        Returns:
            Lista de resultados de búsqueda con metadatos.
        """
        ...

    async def get_documents_metadata(self, fields: list[str]) -> list[dict]:
        """
        Recuperar metadatos para documentos en el índice.

        Args:
            fields: Lista de campos de metadatos a recuperar.

        Returns:
            Lista de diccionarios de metadatos de documentos.
        """
        ...

    async def upload_documents_batch(self, documents: list[dict]) -> None:
        """
        Subir un lote de documentos al índice de búsqueda.

        Args:
            documents: Lista de diccionarios de documentos a subir.
        """
        ...

    async def close(self) -> None:
        """Cerrar el cliente de búsqueda y limpiar recursos."""
        ...

    async def create_pdf_search_tool(self) -> BaseTool:
        """
        Crear una herramienta para buscar documentos PDF.

        Returns:
            Herramienta de búsqueda configurada para documentos PDF.
        """
        ...
