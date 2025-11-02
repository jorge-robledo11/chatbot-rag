"""
Utilidades para validación de formatos de IDs.

Este módulo proporciona funciones para validar los formatos
de IDs de documentos, sesiones e imágenes.
"""

import re

_DOC_ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]{8,40}$')
_SESSION_ID_PATTERN = re.compile(r'^sess_[0-9a-f]{32}$')
_IMAGE_ID_PATTERN = re.compile(r'^[A-Za-z0-9_-]{10,40}$')


def validate_document_id_format(doc_id: str | None) -> bool:
    """
    Valida que un ID de documento cumpla el formato requerido.

    Args:
        doc_id: ID de documento a validar.

    Returns:
        True si el ID es válido, False en caso contrario.
    """
    if not isinstance(doc_id, str):
        return False
    return bool(_DOC_ID_PATTERN.fullmatch(doc_id))


def validate_session_id_format(session_id: str | None) -> bool:
    """
    Valida que un ID de sesión tenga formato correcto.

    Args:
        session_id: ID de sesión a validar.

    Returns:
        True si el ID es válido, False en caso contrario.
    """
    if not isinstance(session_id, str):
        return False
    return bool(_SESSION_ID_PATTERN.fullmatch(session_id))


def validate_image_id_format(image_id: str | None) -> bool:
    """
    Valida que un ID de imagen cumpla el formato requerido.

    Args:
        image_id: ID de imagen a validar.

    Returns:
        True si el ID es válido, False en caso contrario.
    """
    if not isinstance(image_id, str):
        return False
    return bool(_IMAGE_ID_PATTERN.fullmatch(image_id))
