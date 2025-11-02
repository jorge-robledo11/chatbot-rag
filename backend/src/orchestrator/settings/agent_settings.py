"""
Módulo que define el agente conversacional inteligente.

Contiene la definición del estado del grafo (AgentGraphState) y la clase
principal (AjoverAgent) que orquesta la lógica de chat, incluyendo la
toma de decisiones y la ejecución de herramientas de búsqueda (RAG).
"""

import asyncio
import re
import operator
from typing import Annotated, TypedDict

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from loguru import logger

class AgentGraphState(TypedDict):
    """
    Define el estado que se pasa entre los nodos del grafo.

    Attributes:
        messages (list[BaseMessage]): La lista de mensajes que componen la conversación.
        sources (list[dict]): Una lista explícita para almacenar las fuentes
                               consultadas en el turno actual.
    """
    messages: Annotated[list[BaseMessage], operator.add]
    sources: list[dict]

class AjoverAgent:
    """
    Agente inteligente que orquesta la búsqueda y generación de respuestas.
    """
    def __init__(
        self,
        model: AzureChatOpenAI,
        tools: list,
        system_prompt: str,
    ) -> None:
        """
        Inicializa el agente con un modelo y herramientas pre-configuradas.
        """
        logger.info(
            '🤖 Inicializando el agente con dependencias inyectadas...'
        )
        self.system_prompt = system_prompt
        self.model = model.bind_tools(tools)
        self.tool_map = {tool.name: tool for tool in tools}
        self.graph = self._build_graph()
        logger.success('✅ Agente y grafo compilados con éxito.')

    def _build_graph(self) -> StateGraph:
        """
        Construye y compila el StateGraph que define el flujo del agente.
        """
        graph = StateGraph(AgentGraphState)
        graph.add_node('agent', self._agent_node)
        graph.add_node('tools', self._tools_node)
        graph.add_edge(START, 'agent')
        graph.add_conditional_edges(
            'agent',
            self._should_call_tools,
            {'end': END, 'tools': 'tools'},
        )
        graph.add_edge('tools', 'agent')
        return graph.compile()

    def _should_call_tools(self, state: AgentGraphState) -> str:
        """
        Decide si el flujo debe invocar a las herramientas o terminar.
        """
        last_message = state['messages'][-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return 'tools'
        return 'end'

    async def _agent_node(self, state: AgentGraphState) -> dict:
        """
        Invoca al LLM para decidir el siguiente paso o generar una respuesta.
        """
        logger.info('🧠 Nodo Agente: Invocando al LLM...')
        try:
            messages_with_system = [
                SystemMessage(content=self.system_prompt),
                *state['messages'],
            ]
            response = await self.model.ainvoke(messages_with_system)
            return {'messages': [response]}
        except Exception as e:
            logger.exception(f'❌ Error en el nodo del agente: {e}')
            return {'messages': [AIMessage(content='Ocurrió un error interno.')]}

    async def _run_one_tool(self, tool_call: dict) -> ToolMessage:
        """
        Ejecuta una única llamada a herramienta de forma segura.
        """
        tool_name = tool_call['name']
        args = dict(tool_call.get('args', {}))
        try:
            tool_to_call = self.tool_map.get(tool_name)
            if not tool_to_call:
                raise KeyError(f"La herramienta '{tool_name}' no existe.")
            result = await tool_to_call.ainvoke(args)
            return ToolMessage(
                tool_call_id=tool_call['id'],
                name=tool_name,
                content=str(result),
            )
        except Exception as e:
            logger.error(f"❌ Error al ejecutar herramienta '{tool_name}': {e}")
            return ToolMessage(
                tool_call_id=tool_call['id'],
                name=tool_name,
                content=f'Error al ejecutar la herramienta {tool_name}.',
            )

    async def _tools_node(self, state: AgentGraphState) -> dict:
        """
        Ejecuta herramientas y extrae fuentes parseando la salida:
          - PDFs:  '**Archivo:** <nombre.pdf>'
          - Web:   '**Fuente:** <dominio/etiqueta>'
                   '**URL:** [texto](https://...)'  o  '**URL:** https://...'
        """
        tool_calls = state['messages'][-1].tool_calls
        tasks = [self._run_one_tool(call) for call in tool_calls]
        tool_outputs: list[ToolMessage] = await asyncio.gather(*tasks)

        extracted_sources = []

        pdf_pattern = re.compile(r"\*\*Archivo:\*\*\s*(.+)")
        web_source_pattern = re.compile(r"\*\*Fuente:\*\*\s*(.+)")
        web_url_md_pattern = re.compile(r"\*\*URL:\*\*\s*\[[^\]]*\]\((https?://[^\s)]+)\)")
        web_url_plain_pattern = re.compile(r"\*\*URL:\*\*\s*(https?://\S+)")

        files_set, domains_set, urls_set = set(), set(), set()

        for msg in tool_outputs:
            text = msg.content or ""

            for m in pdf_pattern.findall(text):
                if m.strip():
                    files_set.add(m.strip())

            for m in web_source_pattern.findall(text):
                if m.strip():
                    domains_set.add(m.strip())

            for m in web_url_md_pattern.findall(text):
                urls_set.add(m.strip())
            for m in web_url_plain_pattern.findall(text):
                urls_set.add(m.strip())

        for f in files_set:
            extracted_sources.append({"source_file": f})
        for d in domains_set:
            extracted_sources.append({"source_domain": d})
        for u in urls_set:
            extracted_sources.append({"source_url": u})

        logger.info(f"📚 Fuentes extraídas (vía Regex): {extracted_sources}")

        return {
            "messages": tool_outputs,
            "sources": extracted_sources,
        }
