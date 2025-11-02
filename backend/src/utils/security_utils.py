"""
Utilidades de seguridad para autenticación y hashing de contraseñas.

Este módulo proporciona funciones para verificar y generar hashes
de contraseñas usando bcrypt de forma segura.
"""

from loguru import logger
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str | None) -> str:
    """
    Genera el hash de una contraseña usando bcrypt.

    Args:
        password: Contraseña en texto plano.

    Returns:
        Hash bcrypt de la contraseña.

    Raises:
        ValueError: Si la contraseña no es un string válido.
        RuntimeError: Si ocurre un error internamente al hashear.
    """
    if not isinstance(password, str) or not password:
        msg = 'password debe ser un string no vacío'
        logger.error(f'❌ {msg}')
        raise ValueError(msg)

    try:
        hashed: str = pwd_context.hash(password)
        return hashed
    except Exception as e:
        logger.error(f'❌ Error al generar hash de contraseña: {e}')
        raise RuntimeError('Error interno al procesar la contraseña') from e
