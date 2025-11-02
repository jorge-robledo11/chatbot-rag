import nest_asyncio
nest_asyncio.apply()

import asyncio
from dotenv import load_dotenv, find_dotenv
from loguru import logger
from aiolimiter import AsyncLimiter

from backend.src.utils.time_utils import async_timed_block
from backend.src.core.logging_config import setup_logging
from backend.config import get_settings
from backend.src.infrastructure.infrastructure import get_infrastructure
from backend.src.services.image_service import ImageService
from backend.src.services.parser_service import ParserService
from backend.src.services.enricher_service import EnricherService
from backend.src.services.change_detection_service import ChangeDetectorService
from backend.src.services.batch_service import BatchService

# Límites de tasa para API de visión y embeddings
vision_limiter = AsyncLimiter(max_rate=40, time_period=3)
embedding_limiter = AsyncLimiter(max_rate=40, time_period=3)

# Carga variables de entorno de .env
load_dotenv(find_dotenv())

async def main():
    """
    Orquesta el pipeline de sincronización de documentos.
    """
    setup_logging()
    logger.info("🚀 Iniciando el pipeline de sincronización multimodal inteligente...")

    settings = get_settings()
    infra = get_infrastructure()

    async with async_timed_block("Pipeline Completo de Indexación"):
        try:
            # [Paso 1] Obtener BlobStorage
            logger.debug("🔍 [Paso 1] Obteniendo BlobStorage...")
            storage_service = await infra.get_blob_storage()
            logger.success(f"✅ BlobStorage OK: {storage_service.__class__}")

            # [Paso 2] Obtener SearchAI
            logger.debug("🔍 [Paso 2] Obteniendo SearchAI...")
            search_service  = await infra.get_searchai()
            logger.success(f"✅ SearchAI OK: {search_service.__class__}")

            # [Paso 3] Obtener OpenAI
            logger.debug("🔍 [Paso 3] Obteniendo OpenAI...")
            openai_service  = await infra.get_openai()
            logger.success(f"✅ OpenAI OK: {openai_service.__class__}")

            # [Paso 4] Crear/validar índice
            logger.debug("🛠️ [Paso 4] Creando/validando índice...")
            await search_service.create_index_if_not_exists()
            logger.success("✅ Índice validado/creado")

            # [Paso 5] Inicializar servicios de enriquecimiento
            logger.debug("🛠️ [Paso 5] Inicializando servicios de enriquecimiento...")
            image_service    = ImageService(semaphore=asyncio.Semaphore(1))
            parser_service   = ParserService(openai_interface=openai_service, semaphore=asyncio.Semaphore(1))
            enricher_service = EnricherService(
                openai_service=openai_service,
                storage_service=storage_service,
                image_processor=image_service,
                document_parser=parser_service,
                vision_limiter=vision_limiter,
                embedding_limiter=embedding_limiter,
            )
            batch_service    = BatchService(search_service=search_service, enricher_service=enricher_service)
            change_detector  = ChangeDetectorService(storage_service=storage_service, search_service=search_service)
            logger.success("✅ Servicios de enriquecimiento inicializados")

            # [Paso 6] Detectar blobs a procesar
            logger.debug("🛠️ [Paso 6] Detectando blobs a procesar...")
            source_prefix     = settings.blob_storage.source_prefix
            blobs_to_process  = await change_detector.get_blobs_to_process(source_prefix)
            logger.success(f"✅ Detectados {len(blobs_to_process)} blobs")

            if not blobs_to_process:
                logger.success("🎉 El índice ya está sincronizado. No hay nada que procesar.")
                return

            # [Paso 7] Procesar batch
            logger.debug(f"🛠️ [Paso 7] Procesando {len(blobs_to_process)} documentos...")
            await batch_service.process_and_upload_batch(blobs_to_process)
            logger.success("🎉 Pipeline de sincronización finalizado con éxito.")
            
        except Exception:
            logger.exception("❌ Ocurrió un error fatal no controlado en el pipeline principal.")

        finally:
            if infra:
                logger.info("🔒 Cerrando conexiones externas para liberar recursos...")
                await infra.shutdown()
                logger.success("✅ Conexiones cerradas.")


if __name__ == "__main__":
    asyncio.run(main())
