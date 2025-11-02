"""
Interfaz para operaciones de almacenamiento de blobs.

Este módulo define el contrato para interacciones con almacenamiento en la nube.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class BlobStorageInterface(Protocol):
    """
    Define la interfaz para las operaciones básicas con un servicio de almacenamiento de blobs.

    Abstrae la interacción con el almacenamiento en la nube (subir, descargar, listar),
    facilitando el cambio de proveedor o el testing.
    """

    async def upload_bytes(self, data: bytes, blob_name: str, content_type: str) -> str:
        """
        Subir bytes sin procesar al almacenamiento de blobs.

        Args:
            data: Bytes sin procesar para subir.
            blob_name: Nombre para el blob.
            content_type: Tipo MIME del contenido.

        Returns:
            URL del blob subido.
        """
        ...

    async def upload_image(self, img_bytes: bytes, blob_name: str) -> str:
        """
        Subir bytes de imagen al almacenamiento de blobs.

        Args:
            img_bytes: Datos de imagen como bytes.
            blob_name: Nombre para el blob de imagen.

        Returns:
            URL de la imagen subida.
        """
        ...

    async def download_bytes(self, blob_name: str) -> bytes:
        """
        Descargar contenido del blob como bytes.

        Args:
            blob_name: Nombre del blob a descargar.

        Returns:
            Bytes sin procesar del contenido del blob.
        """
        ...

    async def list_blobs(self, prefix: str | None = None) -> list[str]:
        """
        Listar todos los blobs con filtro opcional de prefijo.

        Args:
            prefix: Prefijo opcional para filtrar blobs.

        Returns:
            Lista de nombres de blobs.
        """
        ...

    async def close(self) -> None:
        """Cerrar el cliente de almacenamiento y limpiar recursos."""
        ...
