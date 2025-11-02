"""
Servicio de enriquecimiento de documentos con IA para indexación y búsqueda.
"""

import asyncio
import pathlib
from typing import Any

from aiolimiter import AsyncLimiter
from openai import APIConnectionError
from loguru import logger

from backend.config import get_settings
from backend.src.interfaces.blob_storage_interface import BlobStorageInterface
from backend.src.interfaces.image_interface import ImageInterface
from backend.src.interfaces.openai_interface import OpenAIInterface
from backend.src.interfaces.parser_interface import ParserInterface
from backend.src.utils.identity_utils import (
    generate_content_hash,
    generate_document_id,
    generate_image_id,
)
from backend.src.utils.time_utils import async_timed_block
from backend.src.utils.validation_utils import (
    validate_document_id_format,
    validate_image_id_format,
)


class EnricherService:
    """
    Servicio para enriquecer documentos con análisis de IA y generación de embeddings.
    """

    def __init__(
        self,
        openai_service: OpenAIInterface,
        storage_service: BlobStorageInterface,
        image_processor: ImageInterface,
        document_parser: ParserInterface,
        vision_limiter: AsyncLimiter,
        embedding_limiter: AsyncLimiter,
    ) -> None:
        settings = get_settings()
        self.openai_service = openai_service
        self.storage_service = storage_service
        self.image_processor = image_processor
        self.document_parser = document_parser
        self.vision_limiter = vision_limiter
        self.embedding_limiter = embedding_limiter
        self.images_prefix = settings.blob_storage.images_prefix
        logger.info(f"🔧 EnricherService inicializado (images_prefix={self.images_prefix}).")

    async def process_document_into_chunks(
        self, blob_name: str, blob_content: bytes
    ) -> list[dict[str, Any]]:
        """Orquesta el proceso completo de chunking y enriquecimiento."""
        parent_doc_id = generate_document_id(blob_name)
        if not validate_document_id_format(parent_doc_id):
            logger.error(f'❌ ID de documento padre inválido: {parent_doc_id}')
            return []

        file_name = pathlib.Path(blob_name).name
        logger.info(f'📑 Iniciando enriquecimiento para: {file_name}')

        try:
            async with async_timed_block(f'Extracción de Chunks e Imágenes para {file_name}'):
                logger.info(f"Paso 1/2: Extrayendo texto y chunks para {file_name}...")
                try:
                    chunks = await self.document_parser.extract_chunks(blob_content)
                except Exception as parse_err:
                    logger.warning(f"⚠️ Error extract_chunks en {file_name}: {parse_err}")
                    chunks = []

                logger.info(f"Paso 2/2: Extrayendo imágenes para {file_name}...")
                images = await self.image_processor.convert_pdf_to_images(blob_content)

            if not chunks:
                logger.warning(f"No se extrajeron chunks de {file_name}. Se generará un chunk vacío para continuar proceso.")
                chunks = [""]

            image_descriptions, image_urls = await self._process_images_desc_url(
                parent_doc_id, file_name, images[:10]
            )

            tasks = [
                self._create_chunk_document(
                    blob_name=blob_name,
                    blob_content=blob_content,
                    parent_doc_id=parent_doc_id,
                    chunk_index=i,
                    chunk_content=chunk_content,
                    image_urls=image_urls,
                    image_descriptions=image_descriptions
                )
                for i, chunk_content in enumerate(chunks)
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            enriched_chunks = [res for res in results if res and not isinstance(res, Exception)]

            logger.success(f'✅ Documento {file_name} procesado en {len(enriched_chunks)} chunks.')
            return enriched_chunks

        except Exception as e:
            logger.exception(f'❌ Error crítico enriqueciendo {blob_name}: {e}')
            return []

    async def _create_chunk_document(
        self, blob_name: str, blob_content: bytes, parent_doc_id: str,
        chunk_index: int, chunk_content: str, image_urls: list[str],
        image_descriptions: list[str]
    ) -> dict[str, Any] | None:
        """Crea, enriquece y vectoriza un único chunk."""
        try:
            file_name = pathlib.Path(blob_name).name
            chunk_id = generate_document_id(f"{blob_name}_chunk_{chunk_index + 1}")

            enriched_content = f"Documento '{file_name}': {chunk_content}"

            async with self.embedding_limiter:
                content_vector = await self.openai_service.get_text_embedding(enriched_content)

            return {
                'id': chunk_id,
                'parent_document_id': parent_doc_id,
                'content': chunk_content,
                'content_vector': content_vector,
                'source_file': file_name,
                'source_file_hash': generate_content_hash(blob_content),
                'chunk_number': chunk_index + 1,
                'image_urls': image_urls,
                'image_descriptions': image_descriptions,
            }
        except Exception as e:
            logger.error(f"❌ Fallo al enriquecer el chunk {chunk_index + 1} de {blob_name}: {e}", exc_info=True)
            return None

    async def _process_images_desc_url(
        self, doc_id: str, file_name: str, images: list[bytes],
    ) -> tuple[list[str], list[str]]:
        """Procesa una lista de imágenes, generando descripciones y URLs."""
        if not images:
            return [], []

        logger.info(f'🖼️ Procesando {len(images)} imágenes...')
        tasks = [
            self._describe_and_store_image(doc_id, idx, img, file_name, len(images))
            for idx, img in enumerate(images)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        descriptions, urls = [], []
        for res in results:
            if isinstance(res, dict) and res.get('description') is not None and res.get('url'):
                descriptions.append(res['description'])
                urls.append(res['url'])
        return descriptions, urls

    async def _describe_and_store_image(
        self, doc_id: str, idx: int, img: bytes, file_name: str, total_images: int,
    ) -> dict[str, str | None]:
        """Procesa una sola imagen: la almacena, redimensiona y describe."""
        image_id = generate_image_id(doc_id, idx + 1)
        if not validate_image_id_format(image_id):
            return {'description': None, 'url': None}

        async with async_timed_block(f'Proc. imagen {idx + 1}/{total_images} de {file_name}'):
            # Almacena la imagen (comprimir y subir)
            try:
                compressed_img = await self.image_processor.compress_image(img)
                img_to_store = compressed_img if compressed_img else img
                image_blob_name = f'{self.images_prefix}/{image_id}.jpg'
                image_url = await self.storage_service.upload_image(img_to_store, image_blob_name)
            except Exception as e:
                logger.error(f'❌ Error al guardar imagen {idx + 1}: {e}')
                return {'description': None, 'url': None}

            # Describe la imagen con AI, atrapando errores de conexión
            try:
                img_for_analysis = await self.image_processor.resize_image_for_vision(img)
                async with self.vision_limiter:
                    desc_text = await self.openai_service.get_image_description(img_for_analysis)
                description = f'[IMAGEN: {desc_text}]'
            except APIConnectionError as e:
                logger.warning(f"⚠️ No se pudo obtener la descripción de imagen '{file_name}' (id={image_id}): {e}")
                description = '[IMAGEN: error de conexión]'
            except Exception as e:
                logger.error(f'❌ Fallo al describir imagen {idx + 1}: {e}', exc_info=True)
                description = '[IMAGEN: error de análisis]'

            return {'description': description, 'url': image_url}
