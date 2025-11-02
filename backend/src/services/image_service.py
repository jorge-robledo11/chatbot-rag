"""
Servicio de procesamiento de imágenes y conversión de PDFs.

Este módulo proporciona funcionalidades para convertir documentos PDF
a imágenes, comprimirlas para almacenamiento y redimensionarlas
para análisis de IA, utilizando PyMuPDF (fitz) y OpenCV.
"""

import asyncio
import cv2
import fitz
import numpy as np
from loguru import logger

from backend.src.interfaces.image_interface import ImageInterface

class ImageService(ImageInterface):
    """Implementación de procesamiento de imágenes y PDFs, utilizando PyMuPDF y OpenCV."""
    
    def __init__(self, semaphore: asyncio.Semaphore):
        self._semaphore = semaphore
        logger.info("🔧 ImageService inicializado con semáforo de procesamiento.")

    async def convert_pdf_to_images(self, pdf_bytes: bytes, dpi: int = 300) -> list[bytes]:
        """Convierte un PDF a imágenes, protegido por un semáforo."""
        logger.trace('🖼️ ImageService esperando para adquirir el cerrojo del PDF...')
        async with self._semaphore:
            logger.trace('🖼️ ImageService adquirió el cerrojo. Procesando PDF...')
            try:
                return await asyncio.to_thread(self._render_pdf, pdf_bytes, dpi)
            finally:
                logger.trace('🖼️ ImageService liberó el cerrojo del PDF.')

    def _render_pdf(self, pdf_bytes: bytes, dpi: int) -> list[bytes]:
        """Lógica síncrona de renderizado de PDF."""
        try:
            pdf_doc = fitz.open(stream=pdf_bytes, filetype='pdf')
            images = [page.get_pixmap(dpi=dpi, alpha=False) for page in pdf_doc]
            images_bytes = []
            for pix in images:
                img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                success, encoded_image = cv2.imencode('.png', img_bgr)
                if success:
                    images_bytes.append(encoded_image.tobytes())
            return images_bytes
        except Exception as e:
            logger.error(f'❌ Error durante el renderizado del PDF: {e}')
            return []

    async def compress_image(
        self, image_bytes: bytes, max_size_bytes: int = 256_000
    ) -> bytes | None:
        """
        Comprime una imagen para que no supere un tamaño máximo en bytes para almacenamiento.
        """
        logger.info(
            f'📉 Iniciando compresión de imagen (límite: {max_size_bytes} bytes)...'
        )

        def _compress() -> bytes | None:
            try:
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is None:
                    return None

                for quality in range(85, 20, -15):
                    success, encoded_img = cv2.imencode(
                        '.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                    )
                    if success and len(encoded_img) <= max_size_bytes:
                        logger.success(
                            f'📉✅ Imagen comprimida con calidad {quality}. Tamaño final: {len(encoded_img)} bytes.'
                        )
                        compressed_bytes: bytes = encoded_img.tobytes()
                        return compressed_bytes
                return None
            except Exception as e:
                logger.error(f'❌ Error al comprimir la imagen: {e}')
                return None

        return await asyncio.to_thread(_compress)

    async def resize_image_for_vision(self, img_bytes: bytes, max_dim: int = 1024) -> bytes:
        """
        Redimensiona una imagen a un tamaño máximo para análisis de IA, manteniendo la relación de aspecto.
        Esto es crucial para cumplir con los límites de tokens de los modelos de visión.
        """
        def _resize() -> bytes:
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            h, w = img.shape[:2]
            if w > max_dim or h > max_dim:
                scale = max_dim / max(h, w)
                new_w, new_h = int(w * scale), int(h * scale)
                img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                logger.trace(f"🖼️📏 Imagen redimensionada para análisis de IA a {new_w}x{new_h}.")

            success, encoded_img = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            resized_bytes: bytes = encoded_img.tobytes()
            return resized_bytes

        return await asyncio.to_thread(_resize)
