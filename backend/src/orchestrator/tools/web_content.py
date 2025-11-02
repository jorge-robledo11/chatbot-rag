from typing import Any, Iterable
from langchain_core.tools import BaseTool, tool
from loguru import logger
from backend.src.interfaces.searchai_interface import SearchAIInterface
from backend.config.settings import get_settings

_settings = get_settings()
_rag_cfg = _settings.rag


# ---------------------------
# Utilidades de ranking/búsqueda
# ---------------------------
def _expand_query_if_needed(q: str) -> str:
    """
    Expande la consulta con sinónimos/claves para mejorar recall en índice web.
    """
    q_norm = (q or "").lower()

    expansions: list[str] = []

    # Bloques semánticos frecuentes en sitio corporativo
    if any(k in q_norm for k in ["mision", "misión", "proposito", "propósito", "razon de ser", "razón de ser"]):
        expansions += ["mision", "misión", "proposito", "propósito", "razón de ser"]

    if any(k in q_norm for k in ["vision", "visión", "futuro"]):
        expansions += ["vision", "visión", "futuro"]

    if any(k in q_norm for k in ["valor", "valores", "principios"]):
        expansions += ["valores", "principios"]

    if any(k in q_norm for k in ["quien es", "quién es", "quienes somos", "quiénes somos", "sobre ajover", "sobre nosotros", "acerca de"]):
        expansions += ["quiénes somos", "sobre ajover", "sobre nosotros", "acerca de"]

    if any(k in q_norm for k in ["contacto", "tel", "teléfono", "telefono", "número", "numero", "whatsapp", "correo", "email"]):
        expansions += ["contacto", "teléfono", "número", "correo"]

    if any(k in q_norm for k in ["proyecto", "proyectos", "casos de éxito"]):
        expansions += ["proyectos", "casos de éxito"]

    if any(k in q_norm for k in ["sostenible", "sostenibilidad", "ambiental", "cccs"]):
        expansions += ["sostenibilidad", "ambiental", "CCCS"]

    # Si no hay expansiones relevantes, devolvemos la original
    if not expansions:
        return q

    expanded = f"{q} " + " ".join(sorted(set(expansions)))
    logger.debug(f"🔍 Expansión de consulta web: '{expanded}'")
    return expanded


def _intent_flags(q: str) -> dict[str, bool]:
    q = (q or "").lower()
    return {
        "is_mision": any(k in q for k in ["mision", "misión", "proposito", "propósito", "razon de ser", "razón de ser"]),
        "is_vision": any(k in q for k in ["vision", "visión", "futuro"]),
        "is_valores": any(k in q for k in ["valor", "valores", "principios"]),
        "is_about": any(k in q for k in ["quien es", "quién es", "quienes somos", "quiénes somos", "sobre ajover", "sobre nosotros", "acerca de"]),
        "is_contacto": any(k in q for k in ["contacto", "tel", "teléfono", "telefono", "número", "numero", "whatsapp", "correo", "email"]),
        "is_proyectos": any(k in q for k in ["proyecto", "proyectos", "casos de éxito"]),
        "is_sostenibilidad": any(k in q for k in ["sostenible", "sostenibilidad", "ambiental", "cccs"]),
    }


def _score_doc(doc: dict[str, Any], q: str, flags: dict[str, bool]) -> float:
    """
    Scoring simple:
    - Título que contenga la palabra clave relevante: +10
    - Contenido que contenga la palabra clave relevante: +3
    - Boost por 'source' esperado según intención (p.ej. sobre_ajover para misión/visión/valores/about): +12
    - Boost adicional si el title es exactamente "Misión" / "Visión" / "Valores": +20
    """
    title = (doc.get("title") or "").lower()
    content = (doc.get("content") or "").lower()
    source = (doc.get("source") or "").lower()

    score = 0.0

    # Palabras clave por intención
    if flags["is_mision"]:
        for k in ["mision", "misión", "proposito", "propósito", "razón de ser"]:
            if k in title:
                score += 10
            if k in content:
                score += 3
        if title.strip() in {"misión", "mision"}:
            score += 20
        # Fuente esperada
        if source == "sobre_ajover":
            score += 12

    if flags["is_vision"]:
        for k in ["vision", "visión", "futuro"]:
            if k in title:
                score += 10
            if k in content:
                score += 3
        if title.strip() in {"visión", "vision"}:
            score += 20
        if source == "sobre_ajover":
            score += 12

    if flags["is_valores"]:
        for k in ["valores", "principios"]:
            if k in title:
                score += 10
            if k in content:
                score += 3
        if title.strip() in {"valores"}:
            score += 20
        if source == "sobre_ajover":
            score += 12

    if flags["is_about"]:
        for k in ["quiénes somos", "quienes somos", "sobre ajover", "sobre nosotros", "acerca de"]:
            if k in title:
                score += 10
            if k in content:
                score += 3
        if source == "sobre_ajover":
            score += 12

    if flags["is_contacto"]:
        for k in ["contacto", "teléfono", "telefono", "número", "numero", "correo", "email", "whatsapp"]:
            if k in title:
                score += 10
            if k in content:
                score += 3
        if source == "contacto":
            score += 12

    if flags["is_proyectos"]:
        for k in ["proyecto", "proyectos", "casos de éxito"]:
            if k in title:
                score += 10
            if k in content:
                score += 3
        if source == "proyectos":
            score += 12

    if flags["is_sostenibilidad"]:
        for k in ["sostenibilidad", "ambiental", "cccs"]:
            if k in title:
                score += 10
            if k in content:
                score += 3
        if source == "sostenibilidad":
            score += 12

    return score


def _rerank_web_results(query: str, docs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Rerank no invasivo para priorizar páginas canónicas del sitio corporativo.
    No filtra resultados; solo reordena por score descendente.
    """
    flags = _intent_flags(query)
    scored = [
        (doc, _score_doc(doc, query, flags))
        for doc in docs
    ]
    # Si ningún doc recibe score > 0, conservamos el orden original
    if not any(s > 0 for _, s in scored):
        return docs

    scored.sort(key=lambda x: x[1], reverse=True)
    top_preview = [
        {
            "title": d.get("title"),
            "source": d.get("source"),
            "url": d.get("source_url"),
            "score": s,
        }
        for d, s in scored[:5]
    ]
    logger.debug(f"🏁 Rerank web TOP5: {top_preview}")
    return [d for d, _ in scored]


# ---------------------------
# Formateo de resultados
# ---------------------------

def _format_web_search_results(documents: Iterable[dict[str, Any]]) -> str:
    """
    Formatea los resultados para que el LLM pueda citar claramente fuente/URL.
    """
    docs = list(documents)
    if not docs:
        return 'No se encontraron resultados relevantes en las páginas web indexadas.'

    formatted = []
    for i, doc in enumerate(docs, start=1):
        title = doc.get('title', 'Sin título')
        content = doc.get('content', 'Sin contenido.')
        source = doc.get('source', 'Desconocida')
        url = doc.get('source_url', 'No disponible')

        # Acorta contenido para evitar ruido excesivo al LLM (pero deja contexto suficiente)
        content_snippet = content if len(content) <= 1000 else content[:1000] + "..."

        formatted.append(
            f"""{i}. **Título:** {title}
- **Contenido:** {content_snippet}
- **Fuente:** {source}
- **URL:** [{url}]({url})"""
        )
    logger.debug(f'🔵 Formateados {len(formatted)} docs web.')
    return '\n'.join(formatted)


# ---------------------------
# Fábrica de herramienta
# ---------------------------

def create_web_search_tool(
    search_service: SearchAIInterface,
    characters_limit: int = 80,
) -> BaseTool:
    """
    Herramienta de búsqueda web (LangChain Tool).
    Usa la configuración RAG y llama a `hybrid_search(query, top_k)`.
    Aplica expansión de consulta y rerank ligero para páginas canónicas.
    """

    @tool
    async def tool_web_search(query: str) -> str:
        """
        Busca en el contenido web oficial de Ajover.

        Args:
            query (str): La consulta de búsqueda del usuario.

        Returns:
            str: Resultados formateados.
        """
        logger.debug('🔵 [tool_web_search] Invocada (búsqueda web).')
        if not query:
            return 'Error: Se requiere una consulta de búsqueda.'

        # 1) Expandir consulta para mejorar recall en campos title/content
        expanded_query = _expand_query_if_needed(query)

        # 2) Ajustar top_k si es intención corporativa típica (misión/visión/valores/about/contacto)
        intents = _intent_flags(query)
        top_k = _rag_cfg.search_top_k
        if any(intents[k] for k in ["is_mision", "is_vision", "is_valores", "is_about", "is_contacto"]):
            top_k = max(top_k, 20)

        try:
            # 3) Buscar
            docs = await search_service.hybrid_search(
                query=expanded_query,
                top_k=top_k,
            )

            logger.success(f'🟦 Web docs encontrados: {len(docs)}')
            logger.debug(f"🔵 Raw web preview: {str(docs)[:characters_limit]}...")

            # 4) Rerank suave para priorizar páginas canónicas
            docs = _rerank_web_results(query, docs)

            # 5) Formatear para el LLM (incluye **Fuente:** y **URL:** que tu regex de agent_settings ya extrae)
            formatted = _format_web_search_results(docs)
            return formatted

        except Exception as e:
            logger.exception(f'❌ [tool_web_search] Error: {e}')
            return 'Ocurrió un error al buscar en las páginas web.'

    return tool_web_search
