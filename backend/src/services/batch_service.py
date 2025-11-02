import asyncio
from typing import Any

from loguru import logger
from tqdm.asyncio import tqdm

from backend.src.interfaces.change_detector_interface import BlobToProcess
from backend.src.interfaces.searchai_interface import SearchAIInterface
from backend.src.services.enricher_service import EnricherService


class BatchService:
    """
    Gestiona el procesamiento concurrente y la carga de lotes de documentos.

    Orquesta el enriquecimiento de documentos y su posterior carga en
    Azure AI Search, manejando la concurrencia para maximizar el rendimiento.
    """

    def __init__(
        self,
        search_service: SearchAIInterface,
        enricher_service: EnricherService,
        concurrency: int = 50,
        batch_size: int = 100,
    ) -> None:
        self.search_service = search_service
        self.enricher_service = enricher_service
        self.semaphore = asyncio.Semaphore(concurrency)
        self.batch_size = batch_size
        logger.info(
            f"🔧 BatchService (modo chunking) inicializado con concurrencia {concurrency} y tamaño de lote {batch_size}."
        )

    async def process_and_upload_batch(self, blobs_to_process: list[BlobToProcess]) -> None:
        await self.search_service.create_index_if_not_exists()
        logger.info(f"📨 Iniciando procesamiento de {len(blobs_to_process)} blobs en lotes.")

        all_enriched_chunks: list[dict[str, Any]] = []

        async def process_blob(blob: BlobToProcess) -> list[dict[str, Any]]:
            async with self.semaphore:
                logger.debug(f"▶️  Empezando enrich de {blob['name']}")
                try:
                    chunks = await self.enricher_service.process_document_into_chunks(
                        blob_name=blob['name'],
                        blob_content=blob['content'],
                    )
                    logger.debug(f"✅ Enriquecidos {len(chunks)} chunks de {blob['name']}")
                    return chunks or []
                except Exception as e:
                    logger.error(f"❌ Fallo al procesar {blob['name']}: {e}", exc_info=True)
                    # Devuelve lista vacía para continuar con otros blobs
                    return []

        tasks = [process_blob(blob) for blob in blobs_to_process]
        results = await tqdm.gather(*tasks, desc="Enriqueciendo documentos")

        # Recolectamos todos los chunks enriquecidos
        for chunks in results:
            all_enriched_chunks.extend(chunks)

        total = len(all_enriched_chunks)
        if total == 0:
            logger.warning("⚠️ No se generaron chunks para indexar.")
            return

        # Subida en batches
        logger.info(f"📦 Total de {total} chunks listos. Subiendo en batches de {self.batch_size}...")
        for idx in range(0, total, self.batch_size):
            batch = all_enriched_chunks[idx : idx + self.batch_size]
            batch_num = idx // self.batch_size + 1
            logger.debug(f"⏫ Subiendo batch {batch_num} ({len(batch)} chunks)...")
            try:
                await self.search_service.upload_documents_batch(batch)
                logger.debug(f"✅ Batch {batch_num} subido.")
            except Exception:
                logger.error(f"❌ Error subiendo batch {batch_num}. Continuando con el siguiente.")

        logger.success(f"🎉 Carga completada: {total} chunks indexados.")
