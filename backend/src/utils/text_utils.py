"""
Utilidades para manipulación y sanitización de texto.

Este módulo proporciona funciones para sanitizar entradas de usuario,
contar tokens y truncar texto según límites de tokens.
"""

import re

from loguru import logger


def sanitize_user_input(text: str | None, max_length: int = 2000) -> str:
    """
    Sanitiza el input del usuario para remover caracteres potencialmente peligrosos.

    Y espacios extra, y lo trunca a max_length.

    Args:
        text: Texto a sanitizar.
        max_length: Longitud máxima permitida.

    Returns:
        Texto sanitizado y truncado.

    Raises:
        ValueError: Si text no es str o max_length no es int positivo.
    """
    if not isinstance(text, str):
        logger.error(f'sanitize_user_input: se esperaba str, recibido {type(text)}')
        raise ValueError(f'text debe ser str, recibido {type(text)}')

    if not isinstance(max_length, int) or max_length <= 0:
        logger.error(
            f'sanitize_user_input: max_length debe ser int positivo, recibido {max_length}'
        )
        raise ValueError(f'max_length debe ser int positivo, recibido {max_length}')

    if not text:
        return ''

    sanitized = re.sub(r'[<>&"\']', '', text)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    return sanitized[:max_length]


def count_tokens(text: str | None) -> int:
    """
    Estima la cantidad de tokens en un texto.

    - Usa tiktoken si está instalado.
    - Si no, cuenta palabras como aproximación.

    Args:
        text: Texto a analizar.

    Returns:
        Número estimado de tokens.

    Raises:
        ValueError: Si text no es str.
    """
    if not isinstance(text, str):
        logger.error(f'count_tokens: se esperaba str, recibido {type(text)}')
        raise ValueError(f'text debe ser str, recibido {type(text)}')

    try:
        import tiktoken

        encoding = tiktoken.get_encoding('cl100k_base')
        return len(encoding.encode(text))
    except (ImportError, Exception):
        logger.warning(
            'tiktoken no disponible. Usando aproximación de tokens por palabras.'
        )
        return len(text.split())


def truncate_to_token_limit(text: str | None, max_tokens: int = 8192) -> str:
    """
    Trunca el texto para que no supere max_tokens tokens.

    Args:
        text: Texto a truncar.
        max_tokens: Número máximo de tokens permitidos.

    Returns:
        Texto truncado.

    Raises:
        ValueError: Si text no es str o max_tokens no es int positivo.
    """
    if not isinstance(text, str):
        logger.error(f'truncate_to_token_limit: se esperaba str, recibido {type(text)}')
        raise ValueError(f'text debe ser str, recibido {type(text)}')

    if not isinstance(max_tokens, int) or max_tokens <= 0:
        logger.error(f'truncate_to_token_limit: max_tokens inválido {max_tokens}')
        raise ValueError('max_tokens debe ser entero positivo')

    try:
        import tiktoken

        enc = tiktoken.get_encoding('cl100k_base')
        tokens = enc.encode(text)
        if len(tokens) > max_tokens:
            logger.warning(
                f'truncate_to_token_limit: truncando de {len(tokens)} a {max_tokens} tokens'
            )
            # Anotación explícita para satisfacer MyPy
            decoded_text: str = enc.decode(tokens[:max_tokens])
            return decoded_text
        return text
    except ImportError:
        logger.warning(
            'truncate_to_token_limit: tiktoken no disponible, truncando por palabras'
        )
    except Exception as e:
        logger.error(
            f'truncate_to_token_limit: error con tiktoken: {e}, truncando por palabras'
        )

    # Fallback por palabras
    words = text.split()
    approx_limit = int(max_tokens * 1.5)
    if len(words) > approx_limit:
        logger.warning(
            f'truncate_to_token_limit: truncando texto a {approx_limit} palabras'
        )
        return ' '.join(words[:approx_limit])
    return text
