"""
Servicio para detección de cambios entre Azure Blob Storage y Azure AI Search.

Este módulo proporciona funcionalidades para identificar, descargar y preparar
documentos nuevos o modificados, comparando hashes de contenido.
"""
from loguru import logger
from backend.src.interfaces.blob_storage_interface import BlobStorageInterface
from backend.src.interfaces.change_detector_interface import (
    BlobToProcess,
    ChangeDetectorInterface,
)
from backend.src.interfaces.searchai_interface import SearchAIInterface
from backend.src.utils.identity_utils import generate_content_hash

class ChangeDetectorService(ChangeDetectorInterface):
    """
    Detecta cambios entre Azure Blob Storage y un índice de Azure AI Search.
    
    Su responsabilidad es devolver una lista de blobs listos para procesar,
    incluyendo su contenido binario.
    """

    def __init__(
        self, storage_service: BlobStorageInterface, search_service: SearchAIInterface
    ) -> None:
        """
        Inicializa el servicio de detección de cambios.
        """
        self.storage_service = storage_service
        self.search_service = search_service
        logger.info("🔧 ChangeDetectorService inicializado.")

    async def get_blobs_to_process(self, source_prefix: str) -> list[BlobToProcess]:
        """
        Identifica y descarga los blobs que son nuevos o han sido modificados.
        """
        logger.info(
            f"🕵️‍♂️ Iniciando detección de cambios para el prefijo: '{source_prefix}'"
        )

        try:
            indexed_docs_meta = await self.search_service.get_documents_metadata(
                fields=['source_file', 'source_file_hash']
            )
            indexed_hashes = {doc['source_file']: doc.get('source_file_hash') for doc in indexed_docs_meta if doc.get('source_file')}
            logger.info(
                f'📑 Se recuperaron metadatos para {len(indexed_hashes)} documentos únicos del índice.'
            )
        except Exception as e:
            logger.warning(
                f"⚠️ No se pudieron obtener metadatos del índice (¿es nuevo?): {e}. "
                "Se tratarán todos los archivos como nuevos."
            )
            indexed_hashes = {}

        try:
            all_blobs_meta = await self.storage_service.list_blobs(prefix=source_prefix)
            source_pdf_blobs_meta = [
                blob_meta for blob_meta in all_blobs_meta if blob_meta['name'].lower().endswith('.pdf')
            ]
            logger.info(
                f"📂 Se encontraron {len(source_pdf_blobs_meta)} PDFs en Blob Storage."
            )
        except Exception as e:
            logger.error(
                f"❌ Error al listar blobs de Azure: {e}. No se procesará ningún blob.", exc_info=True
            )
            return []

        blobs_needing_processing: list[BlobToProcess] = []
        for blob_summary in source_pdf_blobs_meta:
            blob_name = blob_summary['name']
            try:
                blob_content = await self.storage_service.download_bytes(blob_name)
                current_hash = generate_content_hash(blob_content)
                stored_hash = indexed_hashes.get(blob_name)
                
                if stored_hash != current_hash:
                    if stored_hash:
                        logger.info(
                            f"  🔄 CAMBIO DETECTADO: '{blob_name}'."
                        )
                    else:
                        logger.info(
                            f"  🆕 NUEVO BLOB DETECTADO: '{blob_name}'."
                        )

                    blobs_needing_processing.append({
                        'name': blob_name,
                        'content': blob_content,
                        'current_hash': current_hash,
                    })
                else:
                    logger.trace(f"✅ Sin cambios en '{blob_name}'. Omitiendo.")
            except Exception as e:
                logger.error(
                    f"❌ Error procesando el blob '{blob_name}' durante la detección: {e}",
                    exc_info=True
                )
                continue

        logger.info(
            f'🔔 Detección de cambios completada. Se procesarán {len(blobs_needing_processing)} blobs.'
        )
        return blobs_needing_processing
