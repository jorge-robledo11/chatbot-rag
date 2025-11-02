"""
Interfaz para operaciones del servicio OpenAI.

Este módulo define el contrato para interacciones con modelos de IA.
"""

from collections.abc import Awaitable
from typing import Protocol, runtime_checkable

from backend.src.models.common import ChatMessage


@runtime_checkable
class OpenAIInterface(Protocol):
    """
    Define la interfaz para interactuar con los servicios de OpenAI.

    Abstrae las llamadas a modelos de lenguaje (LLMs) para descripción de imágenes,
    generación de respuestas, embeddings y manejo de historial de chat,
    promoviendo un diseño modular.
    """

    def get_response_max_tokens(
        self, chat_history: list[ChatMessage]
    ) -> Awaitable[int]:
        """
        Calcula max_tokens de forma controlada.

        Args:
            chat_history: Lista de mensajes previos en la conversación.

        Returns:
            El número máximo de tokens para la respuesta.
        """
        ...

    def get_image_description(self, image_bytes: bytes) -> Awaitable[str]:
        """
        Generar descripción para una imagen usando IA.

        Args:
            image_bytes: Datos de imagen a analizar.

        Returns:
            Descripción generada por IA de la imagen.
        """
        ...

    def generate_chat_response(
        self, system_prompt: str, user_prompt: str, max_tokens: int
    ) -> Awaitable[str]:
        """
        Generar respuesta de chat usando modelo de IA.

        Args:
            system_prompt: Instrucciones del sistema para la IA.
            user_prompt: Pregunta o mensaje del usuario.
            max_tokens: Máximo de tokens para la respuesta.

        Returns:
            Respuesta generada por IA.
        """
        ...

    def get_text_embedding(self, text: str) -> Awaitable[list[float]]:
        """
        Generar vector de embedding de texto.

        Args:
            text: Texto a convertir en embedding.

        Returns:
            Representación vectorial del texto.
        """
        ...

    def condense_question_with_history(
        self,
        chat_history: list[ChatMessage],
        follow_up_question: str,
    ) -> Awaitable[str]:
        """
        Condensar una pregunta de seguimiento con contexto del historial de chat.

        Args:
            chat_history: Mensajes previos en la conversación.
            follow_up_question: Pregunta actual del usuario.

        Returns:
            Pregunta condensada con contexto.
        """
        ...

    def close(self) -> Awaitable[None]:
        """Cerrar el cliente de OpenAI y limpiar recursos."""
        ...
