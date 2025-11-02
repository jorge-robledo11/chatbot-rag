"""
Módulo central para la inyección de dependencias en FastAPI.

Cuando se ejecuta dentro de Azure Functions (la variable FUNCTIONS_WORKER_RUNTIME existe),
las dependencias se exponen como *coroutines* y hacen lazy-warm-up 👷‍♂️.

En cualquier otro entorno (uvicorn/pytest, etc.) se exportan como funciones
síncronas muy ligeras, asumiendo que el evento `startup` ya corrió.
"""

import os

from fastapi import Request

from backend.src.core.warm_up import ensure_warm_state
from backend.src.interfaces.cosmos_db_sessions_interface import (
    CosmosDBSessionsInterface,
)
from backend.src.interfaces.cosmos_db_users_interface import CosmosDBUsersInterface
from backend.src.interfaces.openai_interface import OpenAIInterface
from backend.src.interfaces.searchai_interface import SearchAIInterface
from backend.src.orchestrator.settings.agent_factory import AjoverAgent

IS_AZURE_FUNCTIONS: bool = os.getenv('FUNCTIONS_WORKER_RUNTIME') is not None


if IS_AZURE_FUNCTIONS:
    async def get_agent(request: Request) -> AjoverAgent:
        """
        Obtiene la instancia del agente IA inicializada en warm-up.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            AjoverAgent: Instancia del agente IA.
        """
        await ensure_warm_state(request)
        return request.app.state.agent

    async def get_session_manager(request: Request) -> CosmosDBSessionsInterface:
        """
        Obtiene el gestor de sesiones de Cosmos DB inicializado en warm-up.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            CosmosDBSessionsInterface: Gestor de sesiones de Cosmos DB.
        """
        await ensure_warm_state(request)
        return request.app.state.session_mgr

    async def get_user_manager(request: Request) -> CosmosDBUsersInterface:
        """
        Obtiene el gestor de usuarios de Cosmos DB inicializado en warm-up.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            CosmosDBUsersInterface: Gestor de usuarios de Cosmos DB.
        """
        await ensure_warm_state(request)
        return request.app.state.user_mgr

    async def get_searchai_pdf(request: Request) -> SearchAIInterface:
        """
        Obtiene el cliente de SearchAI para el índice PDF inicializado en warm-up.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            SearchAIInterface: Cliente SearchAI para índice PDF.
        """
        await ensure_warm_state(request)
        return request.app.state.searchai_pdf

    async def get_searchai_web(request: Request) -> SearchAIInterface:
        """
        Obtiene el cliente de SearchAI para el índice WEB inicializado en warm-up.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            SearchAIInterface: Cliente SearchAI para índice WEB.
        """
        await ensure_warm_state(request)
        return request.app.state.searchai_web

    async def get_openai(request: Request) -> OpenAIInterface:
        """
        Obtiene el cliente OpenAI inicializado en warm-up.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            OpenAIInterface: Cliente OpenAI.
        """
        await ensure_warm_state(request)
        return request.app.state.openai_client

else:
    def get_agent(request: Request) -> AjoverAgent:
        """
        Obtiene la instancia del agente IA desde el estado de la app.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            AjoverAgent: Instancia del agente IA.
        """
        return request.app.state.agent

    def get_session_manager(request: Request) -> CosmosDBSessionsInterface:
        """
        Obtiene el gestor de sesiones de Cosmos DB desde el estado de la app.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            CosmosDBSessionsInterface: Gestor de sesiones de Cosmos DB.
        """
        return request.app.state.session_mgr

    def get_user_manager(request: Request) -> CosmosDBUsersInterface:
        """
        Obtiene el gestor de usuarios de Cosmos DB desde el estado de la app.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            CosmosDBUsersInterface: Gestor de usuarios de Cosmos DB.
        """
        return request.app.state.user_mgr

    def get_searchai_pdf(request: Request) -> SearchAIInterface:
        """
        Obtiene el cliente de SearchAI para el índice PDF desde el estado de la app.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            SearchAIInterface: Cliente SearchAI para índice PDF.
        """
        return request.app.state.searchai_pdf

    def get_searchai_web(request: Request) -> SearchAIInterface:
        """
        Obtiene el cliente de SearchAI para el índice WEB desde el estado de la app.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            SearchAIInterface: Cliente SearchAI para índice WEB.
        """
        return request.app.state.searchai_web

    def get_openai(request: Request) -> OpenAIInterface:
        """
        Obtiene el cliente OpenAI desde el estado de la app.

        Args:
            request (Request): Objeto de request de FastAPI.

        Returns:
            OpenAIInterface: Cliente OpenAI.
        """
        return request.app.state.openai_client
