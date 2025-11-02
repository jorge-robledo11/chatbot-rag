"""
Módulo para la creación y gestión del agente singleton.

Este archivo contiene la lógica para:
- Inicializar de forma asíncrona el agente y sus dependencias (LLM, herramientas).
- Proveer una función para obtener la instancia singleton del agente.
- Manejar el historial de chat persistente.
- Orquestar la invocación del agente con las consultas del usuario.
"""

import asyncio

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import AzureChatOpenAI
from loguru import logger

from backend.src.infrastructure.infrastructure import get_infrastructure
from backend.src.models.common import ChatMessage, MessageRole
from backend.src.orchestrator.settings.agent_settings import (
    AgentGraphState,
    AjoverAgent,
)
from backend.src.orchestrator.settings.system_prompts import AGENT_SYSTEM_PROMPT
from backend.src.orchestrator.tools.pdf_content import create_pdf_search_tool
from backend.src.orchestrator.tools.web_content import create_web_search_tool

infra = get_infrastructure()
_agent_instance: AjoverAgent | None = None
_agent_lock = asyncio.Lock()



async def initialize_agent() -> None:
    """
    Inicializa la instancia singleton del Agente.

    Carga los servicios de SearchAI para PDF y web en paralelo,
    inicializa el cliente de AzureChatOpenAI y ensambla el AjoverAgent con sus herramientas.
    """
    global _agent_instance

    if _agent_instance:
        logger.info('✅ El agente ya estaba inicializado. Saltando creación.')
        return

    logger.info('🔧 Creando instancia del agente...')

    async with _agent_lock:
        if _agent_instance is not None:
            return

        pdf_index = infra.settings.search_ai.pdf_index
        web_index = infra.settings.search_ai.web_index

        logger.debug(f'⏳ Loading SearchAI… (pdf={pdf_index}, web={web_index})')
        pdf_svc, web_svc = await asyncio.gather(
            infra.get_searchai(index_type='pdf'),
            infra.get_searchai(index_type='web'),
        )
        logger.success(f"✅ SearchAI listos (PDF='{pdf_index}', WEB='{web_index}')")

        cfg = infra.settings.openai

        logger.info('🤖 Inicializando AzureChatOpenAI…')
        chat_model = AzureChatOpenAI(
            azure_endpoint=cfg.endpoint,
            api_key=cfg.api_key,
            api_version=cfg.api_version,
            azure_deployment=cfg.chat_deployment_name,
            temperature=cfg.temperature,
            streaming=False,
        )
        logger.success('✅ Modelo AzureChatOpenAI listo.')

        pdf_tool = create_pdf_search_tool(search_service=pdf_svc)
        web_tool = create_web_search_tool(search_service=web_svc)

        _agent_instance = AjoverAgent(
            model=chat_model,
            tools=[pdf_tool, web_tool],
            system_prompt=AGENT_SYSTEM_PROMPT,
        )
        logger.success('🚀 Agente listo para solicitudes.')


def get_agent_singleton() -> AjoverAgent:
    """
    Retorna la instancia singleton del agente.

    Raises:
        RuntimeError: Si el agente no ha sido inicializado. Es necesario
                      llamar a `initialize_agent()` primero.
    """
    if _agent_instance is None:
        raise RuntimeError(
            'El agente no ha sido inicializado. Llama primero a initialize_agent().'
        )
    return _agent_instance


async def get_persistent_chat_history(
    session_id: str,
    characters_limit: int = 50,
) -> list[HumanMessage | AIMessage]:
    """
    Recupera y adapta el historial de chat persistente al formato de LangChain.

    Args:
        session_id (str): El identificador de la sesión de la cual recuperar el historial.
        characters_limit (int): El número de caracteres a mostrar en los logs.

    Returns:
        list[HumanMessage | AIMessage]: Una lista de mensajes convertidos.
    """
    history: list[HumanMessage | AIMessage] = []

    try:
        session_mgr = await infra.get_cosmos_db_session()
        session = await session_mgr.get_session(session_id)
        logger.trace(f'🔍 Sesión {session_id} recuperada: {session}')

        if not session or not session.chat_history:
            logger.debug(f'Historial vacío para session_id={session_id}')
            return history

        for raw in session.chat_history:
            msg: ChatMessage = (
                raw if isinstance(raw, ChatMessage) else ChatMessage(**raw)
            )

            if msg.role == MessageRole.USER:
                history.append(HumanMessage(content=msg.content))
                logger.trace(f'↳ USER: {msg.content[:characters_limit]}')
            elif msg.role == MessageRole.ASSISTANT:
                history.append(AIMessage(content=msg.content))
                logger.trace(f'↳ ASSISTANT: {msg.content[:characters_limit]}')
            else:
                logger.debug(f'🚫 Rol desconocido (omitido): {msg.role}')

        logger.debug(f'📜 Historial convertido ({len(history)} mensajes)')

    except Exception as exc:
        logger.warning(f'No se pudo recuperar historial para {session_id}: {exc}')

    return history


async def invoke_agent(
    agent: AjoverAgent,
    user_query: str,
    session_id: str | None = None,
    characters_limit: int = 50,
) -> dict:
    """
    Ejecuta la consulta del usuario a través del agente.

    Orquesta el flujo de trabajo del agente:
    1. Recupera el historial y persiste el mensaje del usuario.
    2. Invoca el grafo del agente con un estado simplificado.
    3. Extrae la respuesta y las fuentes de forma segura desde el estado final.
    """
    session_mgr = await infra.get_cosmos_db_session()

    if session_id:
        hist_task = asyncio.create_task(get_persistent_chat_history(session_id))
        push_task = asyncio.create_task(
            session_mgr.add_message_to_history(
                session_id,
                ChatMessage(role=MessageRole.USER, content=user_query),
            )
        )
        history, _ = await asyncio.gather(hist_task, push_task)
    else:
        new_sess = await session_mgr.create_session(user_id='anonymous_user')
        session_id = new_sess.session_id
        history = []

    logger.debug(f'📚 Historial para grafo ({len(history)} mensajes)')

    initial_state: AgentGraphState = {
        'messages': [*history, HumanMessage(content=user_query)],
        'sources': [],
    }

    logger.info(
        f"▶️ Invocando grafo con consulta: '{user_query[:characters_limit]}…'"
    )
    final_state = await agent.graph.ainvoke(initial_state)

    ai_response: str = final_state['messages'][-1].content
    logger.success(f"✔️ Respuesta: '{ai_response[:characters_limit]}…'")
    
    sources = final_state.get('sources', [])
    logger.info(f"📚 Fuentes extraídas (controlado por backend): {sources}")

    asyncio.create_task(
        session_mgr.add_message_to_history(
            session_id,
            ChatMessage(role=MessageRole.ASSISTANT, content=ai_response),
        )
    )

    return {
        'answer': ai_response,
        'session_id': session_id,
        'sources': sources,
        'confidence_score': final_state.get('confidence_score', 1.0),
        'escalation_recommended': final_state.get('escalation_recommended', False),
    }
