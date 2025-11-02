from typing import Any
from langchain_core.tools import BaseTool, tool
from loguru import logger
from backend.src.interfaces.searchai_interface import SearchAIInterface
from backend.config.settings import get_settings

_settings = get_settings()
_rag_cfg = _settings.rag


def _format_search_results(documents: list[dict[str, Any]]) -> str:
    """
    Formatea los resultados de búsqueda para presentarlos de manera legible.

    Args:
        documents (list[dict[str, Any]]): Una lista de documentos encontrados.

    Returns:
        str: Una cadena de texto formateada con los resultados.
    """
    if not documents:
        return 'No se encontraron resultados relevantes en los PDFs indexados.'

    formatted_docs = []
    for doc in documents:
        source = doc.get('source_file', 'Documento PDF')
        content = doc.get('content', 'Sin contenido.')
        images = doc.get('image_urls', [])
        images_md = '\n      - '.join(images) if images else 'Ninguna'

        formatted_doc = f"""
        1. **Archivo:** {source}
        - **Contenido:** {content}
        - **Imágenes Relevantes:**
            - {images_md}
        """
        formatted_docs.append(formatted_doc.strip())
    return '\n'.join(formatted_docs)


def create_pdf_search_tool(
    search_service: SearchAIInterface,
    characters_limit: int = 50,
) -> BaseTool:
    """
    Fábrica de herramienta de búsqueda PDF para LangChain.

    Inyecta el servicio de búsqueda y usa la configuración RAG singleton para
    buscar en el índice de PDFs sin limitar manualmente el número de docs.
    """

    @tool
    async def tool_pdf_search(
        query: str,
    ) -> str:
        """
        Busca en documentos PDF técnicos de Ajover.

        Args:
            query (str): La consulta de búsqueda del usuario.

        Returns:
            str: Los resultados formateados o un mensaje de error.
        """
        logger.debug('🟠 [tool_pdf_search] Invocada (búsqueda PDF).')
        if not query:
            logger.warning('🔶 [tool_pdf_search] Invocación sin consulta válida.')
            return 'Error: Se requiere una consulta de búsqueda.'

        try:
            logger.debug(f"🟧 Ejecutando hybrid_search en índice PDF: '{query}'")
            documents = await search_service.hybrid_search(
                query=query,
                top_k=_rag_cfg.search_top_k,
            )
            logger.success(f'🟧 PDFs encontrados: {len(documents)}')
            logger.debug(
                '🟠 [tool_pdf_search] Respuesta raw de SearchAI: '
                f'{str(documents)[:characters_limit]}...'
            )
            return _format_search_results(documents)
        except Exception as e:
            logger.exception(f'❌ [tool_pdf_search] Error durante la búsqueda PDF: {e}')
            return 'Ocurrió un error al buscar en los documentos PDF.'

    return tool_pdf_search
