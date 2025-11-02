"""
Interfaz para operaciones de procesamiento de imágenes.

Este módulo define el contrato para conversión de PDF a imagen y compresión.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class ImageInterface(Protocol):
    """
    Define la interfaz para operaciones de procesamiento de imágenes.

    Abstrae la lógica de conversión de PDFs a imágenes y la compresión de estas,
    permitiendo flexibilidad en las implementaciones subyacentes.
    """

    async def convert_pdf_to_images(
        self, pdf_bytes: bytes, dpi: int = 300
    ) -> list[bytes] | None:
        """
        Convertir bytes de PDF a una lista de bytes de imágenes.

        Args:
            pdf_bytes: Datos de PDF sin procesar.
            dpi: Resolución para la conversión de imagen.

        Returns:
            Lista de bytes de imágenes o None si la conversión falla.
        """
        ...

    async def compress_image(
        self, image_bytes: bytes, max_size_bytes: int
    ) -> bytes | None:
        """
        Comprimir imagen para reducir el tamaño del archivo.

        Args:
            image_bytes: Datos de imagen originales.
            max_size_bytes: Tamaño máximo permitido en bytes.

        Returns:
            Bytes de imagen comprimida o None si la compresión falla.
        """
        ...
