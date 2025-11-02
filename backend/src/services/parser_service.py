import asyncio
import tempfile
import os
from loguru import logger

from langchain.text_splitter import TextSplitter
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from langchain_core.embeddings import Embeddings
from langchain_experimental.text_splitter import SemanticChunker

from backend.src.interfaces.openai_interface import OpenAIInterface
from backend.src.interfaces.parser_interface import ParserInterface


class EmbeddingAdapter(Embeddings):
    """
    Adaptador para usar un modelo de embedding asíncrono en un contexto síncrono de LangChain,
    enviando siempre la tarea al loop principal de forma thread-safe.
    """
    def __init__(self, openai_interface: OpenAIInterface):
        self.openai_interface = openai_interface
        self.loop = asyncio.get_event_loop()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """
        Ejecuta la generación de embeddings sobre el loop existente, de forma thread-safe.
        """
        try:
            coro = self.aembed_documents(texts)
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)
            return future.result()
        except Exception as e:
            logger.error(f"Error durante la generación de embeddings en el adaptador: {e}")
            return [[] for _ in texts]

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return await self.openai_interface.get_texts_embedding(texts)

    def embed_query(self, text: str) -> list[float]:
        """
        Ejecuta la generación de un solo embedding de consulta sobre el loop existente,
        de forma thread-safe, para que LangChain reciba siempre un objeto JSON válido.
        """
        try:
            coro = self.aembed_query(text)
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)
            return future.result()
        except Exception as e:
            logger.error(f"Error durante embed_query en el adaptador: {e}")
            return []

    async def aembed_query(self, text: str) -> list[float]:
        return await self.openai_interface.get_text_embedding(text)


class ParserService(ParserInterface):
    """
    Servicio que implementa la lógica de parseo y chunking de documentos.
    """

    def __init__(self, openai_interface: OpenAIInterface, semaphore: asyncio.Semaphore):
        embedding_adapter = EmbeddingAdapter(openai_interface)
        self.text_splitter: TextSplitter = SemanticChunker(
            embeddings=embedding_adapter,
            add_start_index=True
        )
        self._semaphore = semaphore
        logger.info("🔧 ParserService (con SemanticChunker y Semáforo) inicializado.")

    async def extract_chunks(self, document_bytes: bytes) -> list[str]:
        temp_file_path = None
        try:
            # 1) Guardamos PDF en disco
            tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            temp_file_path = tmp.name
            tmp.write(document_bytes)
            tmp.close()

            # 2) Carga protegida por semáforo
            logger.trace('📑 Esperando semáforo para PyMuPDF...')
            async with self._semaphore:
                logger.trace('📑 Cargando PDF con PyMuPDF...')
                loader = PyMuPDFLoader(file_path=temp_file_path)
                loop = asyncio.get_running_loop()
                documents = await loop.run_in_executor(None, loader.load)

            # 3) Concatenamos texto
            full_text = " ".join(doc.page_content for doc in documents)
            if not full_text:
                logger.warning("No se extrajo texto del documento.")
                return []

            logger.info(f"🔬 Texto extraído ({len(full_text)} caracteres). Ahora chunking semántico…")

            # 4) Chunking en hilo aparte
            chunks = await asyncio.to_thread(self.text_splitter.split_text, full_text)

            logger.success(f"✅ Texto dividido en {len(chunks)} chunks semánticos.")
            return chunks

        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
