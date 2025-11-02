"""
Implementación de la interfaz OpenAIInterface para Azure OpenAI.

Esta clase encapsula la lógica para realizar llamadas a los modelos de lenguaje
(LLMs) de OpenAI, incluyendo generación de imágenes, embeddings y respuestas de chat.
Incorpora control de límites de tasa para operar de forma resiliente.
"""

import base64
from collections.abc import Awaitable
from typing import Any

import httpx
from loguru import logger
from openai import AsyncAzureOpenAI, RateLimitError

from backend.config.openai_settings import OpenAISettings
from backend.src.interfaces.openai_interface import OpenAIInterface
from backend.src.models.common import ChatMessage
from backend.src.utils.prompts_utils import (
    get_question_condensation_prompt,
    get_specialized_prompts,
)
from backend.src.utils.retries_utils import async_retry
from backend.src.utils.time_utils import AsyncTokenBucket

class OpenAI(OpenAIInterface):
    """
    Servicio para interacción con Azure OpenAI.

    Maneja chat, embeddings y descripción de imágenes con control de rate limiting.
    """

    _client: AsyncAzureOpenAI | None = None

    def __init__(
        self,
        client: AsyncAzureOpenAI | None,
        chat_deployment: str,
        embedding_deployment: str,
        temperature: float,
        rate: float = 1.0,
        capacity: int = 5,
    ) -> None:
        logger.debug(
            f"🚀 Inicializando servicio OpenAI: chat='{chat_deployment}', "
            f"embeddings='{embedding_deployment}', temp={temperature}"
        )
        self._client = client
        self._chat_deployment = chat_deployment
        self._embedding_deployment = embedding_deployment
        self._temperature = temperature
        self._rate_limiter = AsyncTokenBucket(rate=rate, capacity=capacity)
        logger.debug('✅ Servicio OpenAI inicializado correctamente')

    def _ensure_settings(
        self,
        settings: OpenAISettings | None,
    ) -> OpenAISettings:
        logger.debug('🔍 Validando configuración de OpenAI')
        if settings is None:
            logger.error('❌ Configuración de OpenAI es None')
            raise ValueError('OpenAI settings no pueden ser None')
        return settings

    @classmethod
    async def create(
        cls,
        settings: OpenAISettings | None = None,
    ) -> 'OpenAI':
        logger.debug('🔧 Iniciando OpenAI.create()')
        temp = cls.__new__(cls)
        cfg = temp._ensure_settings(settings)
        client: AsyncAzureOpenAI | None = None

        if cfg.api_key and cfg.endpoint:
            logger.debug('🔑 Configuración de API key y endpoint encontrada')
            timeout = httpx.Timeout(120.0, connect=10.0)
            try:
                client = AsyncAzureOpenAI(
                    api_key=cfg.api_key,
                    azure_endpoint=cfg.endpoint,
                    api_version=cfg.api_version,
                    timeout=timeout,
                )
                logger.success('🤖✅ Cliente AsyncAzureOpenAI inicializado')
            except Exception as e:
                logger.error(f'❌ Error inicializando AsyncAzureOpenAI: {e}')
                raise
        else:
            logger.error('❌ Falta API key o endpoint de Azure OpenAI')
            raise ValueError('Falta API key o endpoint de Azure OpenAI')

        return cls(
            client=client,
            chat_deployment=cfg.chat_deployment_name,
            embedding_deployment=cfg.embedding_deployment_name,
            temperature=cfg.temperature,
        )

    @property
    def client(self) -> AsyncAzureOpenAI:
        logger.debug('🔍 Accediendo a cliente de OpenAI')
        if self._client is None:
            logger.error('❌ Cliente OpenAI no inicializado')
            raise RuntimeError('Cliente OpenAI no inicializado')
        return self._client

    def _calculate_condensation_tokens(self, chat_history: list[ChatMessage]) -> int:
        if not chat_history:
            return 250
        num_messages = len(chat_history)
        if num_messages <= 2: tokens = 250
        elif num_messages <= 4: tokens = 300
        elif num_messages <= 6: tokens = 350
        else: tokens = 400
        logger.debug(f'📊 Tokens para condensación: {tokens} (mensajes: {num_messages})')
        return tokens

    @async_retry(max_retries=3, retry_wait=10.0)
    async def condense_question_with_history(
        self, chat_history: list[ChatMessage], follow_up_question: str
    ) -> str:
        logger.debug(f'🔄 Condensando pregunta con historial (len={len(chat_history)})')
        if not self._client or not chat_history:
            logger.warning('⚠️ Omisión de condensación: cliente no configurado o historial vacío')
            return follow_up_question

        await self._rate_limiter.consume()
        system_prompt = get_question_condensation_prompt()
        messages: list[dict[str, Any]] = [{'role': 'system', 'content': system_prompt}]
        for msg in chat_history:
            role_str = msg.role.value if msg.role is not None else 'user'
            messages.append({'role': role_str, 'content': msg.content})
        messages.append({'role': 'user', 'content': follow_up_question})
        dynamic_tokens = self._calculate_condensation_tokens(chat_history)

        try:
            resp = await self.client.chat.completions.create(
                model=self._chat_deployment,
                messages=messages,
                temperature=0.0,
                max_tokens=dynamic_tokens,
            )
            condensed = resp.choices[0].message.content or ''
            logger.info(f"✅ Pregunta condensada: '{condensed.strip()}'")
            return condensed.strip()
        except RateLimitError as e:
            logger.error(f'❌ Rate limit al condensar pregunta: {e}')
            return follow_up_question
        except Exception as e:
            logger.exception(f'❌ Error inesperado al condensar pregunta: {e}')
            return follow_up_question

    def get_image_description(self, image_bytes: bytes) -> Awaitable[str]:
        return self._get_image_description(image_bytes)

    @async_retry(max_retries=3, retry_wait=10.0)
    async def _get_image_description(self, image_bytes: bytes) -> str:
        logger.debug(f'🖼️ Analizando imagen ({len(image_bytes)} bytes)')
        await self._rate_limiter.consume()
        prompts = get_specialized_prompts('image_analysis')
        b64 = base64.b64encode(image_bytes).decode('utf-8')

        try:
            vision_messages = [
                {"role": "user", "content": [
                    {"type": "text", "text": prompts['user']},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{b64}",
                        "detail": "low"
                    }}
                ]}
            ]
            if prompts.get('system'):
                vision_messages.insert(0, {'role': 'system', 'content': prompts['system']})

            resp = await self.client.chat.completions.create(
                model=self._chat_deployment,
                messages=vision_messages,
                max_tokens=300,
                temperature=self._temperature,
            )
            description = resp.choices[0].message.content or ''
            logger.info(f'✅ Descripción de imagen obtenida ({len(description)} chars)')
            return description
        except RateLimitError as e:
            logger.error(f'❌ Rate limit al describir imagen: {e}')
            raise
        except Exception as e:
            logger.exception(f'❌ Error al analizar imagen: {e}')
            return '[Error al analizar imagen]'

    @async_retry(max_retries=3, retry_wait=10.0)
    async def get_text_embedding(self, text: str) -> list[float]:
        logger.debug(f'📊 Generando embedding para texto (len={len(text)})')
        if not self._client:
            return []
        await self._rate_limiter.consume()
        try:
            resp = await self.client.embeddings.create(
                model=self._embedding_deployment, 
                input=text
            )
            embedding: list[float] = resp.data[0].embedding
            logger.info(f'✅ Embedding generado (dim={len(embedding)})')
            return embedding
        except Exception as e:
            logger.exception(f'❌ Error al generar embedding: {e}')
            return []

    @async_retry(max_retries=3, retry_wait=10.0)
    async def get_texts_embedding(self, texts: list[str]) -> list[list[float]]:
        """
        Genera los embeddings para una lista de textos en una sola llamada (batch).
        """
        logger.debug(f'📊 Generando embeddings para {len(texts)} textos en lote.')
        if not self._client or not texts:
            return [[] for _ in texts]

        await self._rate_limiter.consume()
        try:
            resp = await self.client.embeddings.create(
                model=self._embedding_deployment,
                input=texts,
            )
            sorted_embeddings = sorted(resp.data, key=lambda e: e.index)
            embeddings: list[list[float]] = [item.embedding for item in sorted_embeddings]
            logger.info(f'✅ {len(embeddings)} embeddings generados en lote.')
            return embeddings
        except Exception as e:
            logger.exception(f'❌ Error al generar embeddings en lote: {e}')
            return [[] for _ in texts]


    @async_retry(max_retries=3, retry_wait=10.0)
    async def generate_chat_response(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        max_tokens: int,
    ) -> str:
        logger.debug(f'💬 Generando respuesta de chat (user_prompt len={len(user_prompt)})')
        if not self._client:
            return 'El servicio de IA no está configurado.'
        await self._rate_limiter.consume()
        try:
            resp = await self.client.chat.completions.create(
                model=self._chat_deployment,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                max_tokens=max_tokens,
                temperature=self._temperature,
            )
            raw: Any = resp.choices[0].message.content
            chat_response: str = str(raw) if raw is not None else 'No se pudo generar una respuesta.'
            logger.info('✅ Respuesta de chat generada')
            return chat_response
        except RateLimitError as e:
            logger.error(f'❌ Rate limit al generar respuesta: {e}')
            raise
        except Exception as e:
            logger.exception(f'❌ Error al generar respuesta de chat: {e}')
            return 'Hubo un problema al contactar al servicio de IA.'

    async def close(self) -> None:
        logger.debug('🔒 Cerrando cliente de Azure OpenAI')
        if not self._client:
            return
        try:
            await self._client.close()
            self._client = None
            logger.success('🔒✅ Cliente Azure OpenAI cerrado correctamente')
        except Exception as e:
            logger.error(f'❌ Error al cerrar cliente OpenAI: {e}')
            raise
