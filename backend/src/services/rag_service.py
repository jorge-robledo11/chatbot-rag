"""
Servicio RAG para procesamiento de consultas conversacionales.

Este módulo implementa la lógica de negocio principal para el sistema RAG,
orquestando búsqueda híbrida, generación de respuestas y evaluación de confianza.
"""

from loguru import logger

from backend.config.rag_settings import RAGSettings
from backend.src.interfaces.openai_interface import OpenAIInterface
from backend.src.interfaces.rag_interface import RAGInterface
from backend.src.interfaces.searchai_interface import SearchAIInterface
from backend.src.models.common import BasicSource, Priority, QueryType
from backend.src.models.requests import BaseQueryRequest
from backend.src.models.responses import BaseQueryResponse
from backend.src.utils.identity_utils import generate_deterministic_trace_id
from backend.src.utils.prompts_utils import build_rag_user_prompt, get_rag_system_prompt
from backend.src.utils.text_utils import count_tokens, sanitize_user_input
from backend.src.utils.time_utils import get_colombia_time


class RAGService(RAGInterface):
    """
    Servicio de lógica de negocio que orquesta el proceso RAG conversacional.

    Todas las dependencias se inyectan desde la infraestructura centralizada.
    """

    def __init__(
        self,
        search_service: SearchAIInterface,
        openai_service: OpenAIInterface,
        settings: RAGSettings,
    ) -> None:
        """
        Inicializa el servicio RAG con las dependencias necesarias.

        Args:
            search_service: Interfaz para búsqueda híbrida en documentos.
            openai_service: Interfaz para generación de respuestas con LLM.
            settings: Configuraciones específicas para el servicio RAG.
        """
        self.search_service = search_service
        self.openai_service = openai_service
        self.settings = settings

    def _get_chat_history(self, request: BaseQueryRequest) -> list:
        """
        Obtiene el historial de chat de forma segura.

        Args:
            request: Solicitud base que puede tener historial de chat.

        Returns:
            Lista con el historial de chat o lista vacía.
        """
        return getattr(request, 'chat_history', [])

    def _get_query_type(self, request: BaseQueryRequest) -> QueryType:
        """
        Obtiene el tipo de consulta de forma segura.

        Args:
            request: Solicitud base que puede especificar tipo de consulta.

        Returns:
            Tipo de consulta (PDF o WEB), por defecto PDF si no viene nada.
        """
        return getattr(request, 'query_type', QueryType.PDF)

    def _get_priority(self, request: BaseQueryRequest) -> Priority:
        """
        Obtiene la prioridad de forma segura.

        Args:
            request: Solicitud base que puede tener prioridad.

        Returns:
            Prioridad o valor por defecto (NORMAL).
        """
        return getattr(request, 'priority', Priority.NORMAL)

    async def process_query(self, request: BaseQueryRequest) -> BaseQueryResponse:
        """
        Procesa una consulta utilizando el pipeline RAG completo.

        Args:
            request: Solicitud de consulta con todos los datos necesarios.

        Returns:
            BaseQueryResponse con el texto de respuesta, puntuación de confianza y metadatos.
        """
        colombia_timestamp = get_colombia_time()
        session_id = request.session_id
        chat_history = self._get_chat_history(request)
        query_type = self._get_query_type(request)
        priority = self._get_priority(request)

        interaction_id = generate_deterministic_trace_id(
            session_id or 'new_session', len(chat_history) // 2 + 1
        )
        sanitized_query = sanitize_user_input(request.query)
        log_session_id = session_id[:12] if session_id else 'N/A'

        logger.info(
            f"🤖 Procesando consulta en sesión {log_session_id}… - '{sanitized_query[:50]}'"
        )

        try:
            # 1) Condensar pregunta si es seguimiento
            if chat_history:
                standalone_query = await self.openai_service.condense_question_with_history(
                    chat_history=chat_history,
                    follow_up_question=sanitized_query,
                )
            else:
                standalone_query = sanitized_query

            # 2) Realizar búsqueda híbrida (índice ya configurado en search_service)
            search_results = await self.search_service.hybrid_search(
                query=standalone_query,
                top_k=self.settings.search_top_k,
            )

            # 3) Construir contexto y generar respuesta
            context = self._build_optimized_context(search_results)
            response_text, confidence = await self._generate_response(
                query=sanitized_query,
                context=context,
                query_type=query_type,
                priority=priority,
            )

            return BaseQueryResponse(
                response=response_text,
                confidence_score=confidence,
                session_id=session_id,
                interaction_id=interaction_id,
                timestamp=colombia_timestamp,
                sources=[
                    self._convert_to_basic_source(result) for result in search_results
                ],
            )

        except Exception as e:
            logger.error(
                f'❌ Error fatal procesando consulta en sesión {session_id}: {e}',
                exc_info=True,
            )
            return BaseQueryResponse(
                response='Lo siento, un error inesperado ocurrió.',
                confidence_score=0.0,
                session_id=session_id,
                interaction_id=interaction_id,
                timestamp=colombia_timestamp,
            )

    def _build_optimized_context(
        self,
        search_results: list[dict[str, str | list[str]]],
    ) -> str:
        """
        Construye un contexto optimizado a partir de los resultados de búsqueda.

        Args:
            search_results: Lista de documentos encontrados en la búsqueda.

        Returns:
            Contexto textual optimizado para el modelo de lenguaje.
        """
        if not search_results:
            return 'No se encontró información relevante en la base de conocimiento.'

        context_parts: list[str] = []
        total_tokens = 0

        for i, result in enumerate(search_results, start=1):
            content = (
                f"[Fuente {i}: {result.get('source_file','N/A')}]\n"
                f"{result.get('content','')}\n"
            )
            content_tokens = count_tokens(content)
            if total_tokens + content_tokens > self.settings.max_context_tokens:
                logger.warning(
                    f"⚠️ Límite de tokens de contexto alcanzado tras {i-1} fuentes."
                )
                break

            context_parts.append(content)
            total_tokens += content_tokens

        logger.info(
            f"📚 Contexto construido con {total_tokens} tokens en {len(context_parts)} fuentes."
        )
        return "\n".join(context_parts)

    def _get_max_tokens_for_query_type(self, query_type: QueryType) -> int:
        """
        Obtiene el número máximo de tokens según el tipo de consulta.

        Args:
            query_type: Tipo de consulta (PDF o WEB).

        Returns:
            Número máximo de tokens permitidos para el tipo de consulta.
        """
        token_mapping = {
            QueryType.PDF: self.settings.pdf_response_max_tokens,
            QueryType.WEB: self.settings.web_response_max_tokens,
        }
        return token_mapping[query_type]

    async def _generate_response(
        self,
        query: str,
        context: str,
        query_type: QueryType,
        priority: Priority,
    ) -> tuple[str, float]:
        """
        Genera una respuesta utilizando el modelo de lenguaje.

        Args:
            query: Consulta del usuario sanitizada.
            context: Contexto construido a partir de documentos relevantes.
            query_type: Tipo de consulta para personalizar el prompt.
            priority: Prioridad de la consulta.

        Returns:
            Tupla con la respuesta generada y su puntuación de confianza.
        """
        system_prompt = get_rag_system_prompt(query_type.value)
        user_prompt = build_rag_user_prompt(
            context,
            query,
            query_type.value,
            priority.value,
        )
        max_tokens = self._get_max_tokens_for_query_type(query_type)

        logger.info(
            f"💬 Enviando prompt a LLM (max_tokens={max_tokens}, tipo={query_type.value})"
        )
        response_text = await self.openai_service.generate_chat_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
        )

        confidence = 0.3 if "No se encontró información" in context else 0.85
        logger.info(f"🤔 Confianza calculada: {confidence}")
        return response_text, confidence

    def _convert_to_basic_source(
        self,
        search_result: dict[str, str | list[str]],
    ) -> BasicSource:
        """
        Convierte un resultado de búsqueda en un objeto BasicSource.

        Args:
            search_result: Resultado de búsqueda con metadatos del documento.

        Returns:
            Objeto BasicSource con la información estructurada.
        """
        content = search_result.get('content', '')
        excerpt = str(content)[:200] if content else ''

        return BasicSource(
            document_id=search_result.get('id', 'unknown'),
            title=search_result.get('source_file', 'Documento de Ajover'),
            excerpt=excerpt,
            source_type='documentacion_tecnica',
            source_file=search_result.get('source_file', 'unknown.pdf'),
        )
