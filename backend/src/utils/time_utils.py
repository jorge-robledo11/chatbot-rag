"""
Utilidades para manejo de tiempo y rate limiting en la zona horaria de Colombia.

Este módulo proporciona funciones para trabajar con timestamps,
calcular duraciones de sesiones, y gestión de rate limiting asíncrono.
"""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from time import perf_counter
from zoneinfo import ZoneInfo

from loguru import logger

COLOMBIA_TIMEZONE = ZoneInfo('America/Bogota')


def get_colombia_time() -> datetime:
    """
    Obtiene la fecha y hora actual en la zona horaria de Colombia.

    Returns:
        Datetime con timezone de Colombia.

    Raises:
        RuntimeError: Si hay problemas con la zona horaria.
    """
    try:
        current_time = datetime.now(COLOMBIA_TIMEZONE)
        logger.debug(f'🕐 Hora Colombia obtenida: {current_time.isoformat()}')
        return current_time
    except Exception as e:
        logger.error(f'❌ Error obteniendo hora de Colombia: {e}')
        raise RuntimeError(f'Error al obtener hora de Colombia: {e}') from e


@asynccontextmanager
async def async_timed_block(name: str) -> AsyncGenerator[None, None]:
    """
    Un gestor de contexto asíncrono para medir y registrar el tiempo de ejecución.

    Registra automáticamente el inicio y fin del bloque de código,
    incluyendo el tiempo total de ejecución.

    Args:
        name: Nombre descriptivo del bloque de código para logging.

    Yields:
        None: El contexto para ejecutar el código cronometrado.

    Example:
        ```
        async with async_timed_block('Procesamiento de documentos'):
            await process_documents()
        ```
    """
    if not isinstance(name, str) or not name.strip():
        logger.warning("⚠️ Nombre de bloque cronometrado vacío, usando 'unnamed_block'")
        name = 'unnamed_block'

    logger.info(f"⏱️ Iniciando bloque cronometrado: '{name}'...")
    start_time = perf_counter()
    exception_occurred = False

    try:
        yield
    except Exception as e:
        exception_occurred = True
        logger.error(
            f"❌ Excepción en bloque cronometrado '{name}': {type(e).__name__}: {e}"
        )
        raise
    finally:
        end_time = perf_counter()
        elapsed_seconds = end_time - start_time

        if exception_occurred:
            logger.warning(
                f"⏱️⚠️ Bloque '{name}' terminó con excepción después de "
                f'{elapsed_seconds:.2f} segundos.'
            )
        else:
            logger.success(
                f"⏱️✅ Bloque '{name}' completado en {elapsed_seconds:.2f} segundos."
            )


class AsyncTokenBucket:
    """
    Implementación de Token Bucket asíncrono para rate limiting interno.

    Utiliza el algoritmo de token bucket para controlar la tasa de llamadas
    a servicios externos como OpenAI, evitando sobrepasar los límites de rate.

    Attributes:
        _rate: Tokens generados por segundo.
        _capacity: Capacidad máxima del bucket.
        _tokens: Tokens disponibles actualmente.
        _last_update: Timestamp de la última actualización.
        _lock: Lock asyncio para operaciones thread-safe.
        _bucket_id: Identificador único para logging.

    Example:
        ```
        bucket = AsyncTokenBucket(rate=2.0, capacity=5)


        async def call_api():
            await bucket.consume()  # Espera si es necesario
        ```
    """

    def __init__(self, rate: float, capacity: int, bucket_id: str = 'default') -> None:
        """
        Inicializa el token bucket con la tasa y capacidad especificadas.

        Args:
            rate: Número de tokens generados por segundo.
            capacity: Número máximo de tokens que puede contener el bucket.
            bucket_id: Identificador para logging y debugging.

        Raises:
            ValueError: Si rate o capacity son inválidos.
            RuntimeError: Si no hay un event loop activo.
        """
        if not isinstance(rate, int | float) or rate <= 0:
            raise ValueError(f'rate debe ser un número positivo, recibido: {rate}')

        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError(
                f'capacity debe ser un entero positivo, recibido: {capacity}'
            )

        if not isinstance(bucket_id, str) or not bucket_id.strip():
            bucket_id = 'unnamed_bucket'

        self._rate = float(rate)
        self._capacity = capacity
        self._tokens = float(capacity)
        self._bucket_id = bucket_id.strip()
        self._lock = asyncio.Lock()

        try:
            self._last_update = asyncio.get_running_loop().time()
        except RuntimeError as e:
            logger.error(
                f"❌ Error inicializando token bucket '{self._bucket_id}': No hay event loop activo"
            )
            raise RuntimeError(
                f'AsyncTokenBucket requiere un event loop activo: {e}'
            ) from e

        logger.info(
            f"🪣 Token bucket '{self._bucket_id}' inicializado: "
            f'rate={self._rate}/s, capacity={self._capacity}'
        )

    async def consume(self, tokens: int = 1) -> None:
        """
        Consume tokens del bucket, esperando si es necesario.

        Args:
            tokens: Número de tokens a consumir (por defecto 1).

        Raises:
            ValueError: Si tokens es inválido.
        """
        if not isinstance(tokens, int) or tokens <= 0:
            raise ValueError(f'tokens debe ser un entero positivo, recibido: {tokens}')

        if tokens > self._capacity:
            logger.warning(
                f'⚠️ Solicitados {tokens} tokens pero capacity es {self._capacity} '
                f"en bucket '{self._bucket_id}'"
            )

        async with self._lock:
            await self._refill_tokens()

            if self._tokens < tokens:
                delay = (tokens - self._tokens) / self._rate
                logger.info(
                    f"⏳ Rate limit en bucket '{self._bucket_id}': "
                    f'esperando {delay:.2f}s para {tokens} tokens'
                )

                await asyncio.sleep(delay)
                await self._refill_tokens()

            self._tokens = max(0.0, self._tokens - tokens)

            logger.debug(
                f"🪣 Consumidos {tokens} tokens del bucket '{self._bucket_id}'. "
                f'Tokens restantes: {self._tokens:.2f}'
            )

    async def _refill_tokens(self) -> None:
        """Rellena tokens basado en el tiempo transcurrido."""
        now = asyncio.get_running_loop().time()
        elapsed = now - self._last_update

        new_tokens = elapsed * self._rate
        old_tokens = self._tokens

        self._tokens = min(self._capacity, self._tokens + new_tokens)
        self._last_update = now

        if new_tokens > 0.1:
            logger.debug(
                f"🔄 Bucket '{self._bucket_id}' rellenado: "
                f'{old_tokens:.2f} → {self._tokens:.2f} tokens '
                f'(+{new_tokens:.2f} en {elapsed:.2f}s)'
            )

    def get_status(self) -> dict[str, str | int | float]:
        """
        Obtiene el estado actual del bucket para debugging.

        Returns:
            Diccionario con información del estado del bucket.
        """
        return {
            'bucket_id': self._bucket_id,
            'rate': self._rate,
            'capacity': self._capacity,
            'current_tokens': round(self._tokens, 2),
            'utilization_percent': round((1 - self._tokens / self._capacity) * 100, 2),
            'last_update': self._last_update,
        }
