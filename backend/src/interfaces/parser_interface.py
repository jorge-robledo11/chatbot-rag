"""
Interfaz para operaciones de análisis de documentos.

Este módulo define el contrato para extracción de texto de documentos.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ParserInterface(Protocol):
    """
    Define la interfaz para la extracción de texto de documentos.

    Abstrae el proceso de parseo y lectura de contenido, permitiendo
    flexibilidad en las fuentes y formatos de documentos.
    """

    async def extract_chunks(self, document_bytes: bytes) -> list[str]:
        """
        Toma el contenido de un documento en bytes y lo devuelve dividido
        en una lista de chunks de texto.

        Args:
            document_bytes (bytes): Datos del documento sin procesar.

        Returns:
            list[str]: Una lista de los chunks de texto extraídos.
        """
        ...
