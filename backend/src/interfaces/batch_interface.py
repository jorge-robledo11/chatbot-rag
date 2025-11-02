"""
Interfaz para operaciones de procesamiento por lotes y carga de datos.

Este módulo define el contrato para operaciones eficientes de procesamiento
masivo de elementos.
"""

from typing import Protocol, runtime_checkable

from backend.src.models.documents import BlobData


@runtime_checkable
class BatchInterface(Protocol):
    """
    Define la interfaz para el procesamiento y carga de lotes de datos.

    Abstrae la lógica de orquestación para procesar múltiples elementos de forma
    eficiente y cargarlos a un destino, optimizando operaciones masivas.
    """

    async def process_and_upload_batch(self, blobs_to_process: list[BlobData]) -> None:
        """
        Procesar y subir un lote de blobs de manera eficiente.

        Args:
            blobs_to_process: Lista de diccionarios de blobs para procesar y subir.
        """
        ...
