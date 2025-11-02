"""
Utilidades para reintentos asíncronos con backoff exponencial.

Este módulo proporciona decoradores para reintentar funciones asíncronas
ante excepciones específicas, con estrategias de backoff y jitter.
"""

import asyncio
import random
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from loguru import logger
from openai import RateLimitError

P = ParamSpec('P')
T = TypeVar('T')


def async_retry(
    max_retries: int = 3,
    retry_wait: float = 10.0,
    exceptions: tuple[type[Exception], ...] = (RateLimitError,),
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Decorador para reintentar funciones asíncronas ante ciertas excepciones.

    Args:
        max_retries: Número máximo de reintentos.
        retry_wait: Tiempo base (segundos) entre reintentos, con backoff exponencial.
        exceptions: Excepciones que disparan el reintento.

    Returns:
        Decorador que envuelve la función con lógica de reintentos.
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            last_exception: Exception | None = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = retry_wait * (2**attempt) + random.uniform(0, 2)
                        logger.warning(
                            f'⏳ {type(e).__name__} en intento {attempt + 1}/{max_retries}: {e}. '
                            f'Esperando {wait_time:.1f}s antes de reintentar.'
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(
                            f'❌ Excedidos los reintentos ({max_retries}) por {type(e).__name__}: {e}'
                        )
                        raise
                except Exception as e:
                    logger.error(f'❌ Error inesperado: {e}')
                    raise

            if last_exception:
                raise last_exception
            raise RuntimeError(
                'Error inesperado en async_retry: bucle terminó sin retorno'
            )

        return wrapper

    return decorator
