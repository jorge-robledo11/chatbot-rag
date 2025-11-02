"""
Interfaz para detección de cambios en almacenamiento de blobs.

Este módulo define el contrato para detectar blobs modificados.
"""

from typing import Protocol, runtime_checkable

from backend.src.models.documents import BlobToProcess


@runtime_checkable
class ChangeDetectorInterface(Protocol):
    """
    Define la interfaz para la detección de cambios en blobs.

    Abstrae del método para obtener la lista de blobs que necesitan ser procesados,
    basándose en un prefijo de origen, facilitando la sincronización eficiente de datos.
    """

    async def get_blobs_to_process(self, source_prefix: str) -> list[BlobToProcess]:
        """
        Obtener lista de blobs que necesitan procesamiento basado en cambios.

        Args:
            source_prefix: Prefijo para filtrar blobs de origen.

        Returns:
            Lista de blobs que requieren procesamiento.
        """
        ...
