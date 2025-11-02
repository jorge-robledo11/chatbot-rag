"""
Utilidades para generación de IDs determinísticos y seguros.

Este módulo proporciona funciones para generar IDs únicos y seguros
para diversas entidades de datos, como documentos, imágenes y sesiones.
"""

import base64
import hashlib
import secrets


def generate_deterministic_id(input_str: str, max_length: int = 40) -> str:
    """
    Genera un ID determinístico y seguro para URL usando un hash SHA-256.

    Ideal para crear IDs estables para entidades de datos.

    Args:
        input_str: Cadena de entrada para generar el hash.
        max_length: Longitud máxima del ID generado.

    Returns:
        ID determinístico en formato base64 URL-safe.
    """
    hash_bytes = hashlib.sha256(input_str.encode('utf-8')).digest()
    base64_bytes = base64.urlsafe_b64encode(hash_bytes)
    clean_id = base64_bytes.decode('utf-8').rstrip('=')
    return clean_id[:max_length]


def generate_document_id(blob_name: str) -> str:
    """
    Genera un ID determinístico para un documento a partir de su nombre de blob.

    Args:
        blob_name: Nombre del blob del documento.

    Returns:
        ID determinístico para el documento.
    """
    normalized_path = blob_name.strip('/').lower()
    return generate_deterministic_id(normalized_path)


def generate_image_id(doc_id: str, image_index: int) -> str:
    """
    Genera un ID determinístico para una imagen dentro de un documento.

    Args:
        doc_id: ID del documento.
        image_index: Índice de la imagen.

    Returns:
        ID determinístico para la imagen.
    """
    image_identifier = f'{doc_id}_img_{image_index:03d}'
    return generate_deterministic_id(image_identifier)


def generate_secure_session_id() -> str:
    """
    Genera un ID de sesión seguro y no predecible, cumpliendo con estándares de seguridad.

    Returns:
        ID de sesión seguro y no predecible.
    """
    random_bytes = secrets.token_bytes(16)  # 128 bits de entropía
    return f'sess_{random_bytes.hex()}'


def generate_deterministic_trace_id(session_id: str, interaction_index: int) -> str:
    """
    Genera un ID de trazabilidad determinístico basado en un ID de sesión seguro.

    Útil para unir logs y eventos sin exponer la lógica de la sesión.

    Args:
        session_id: ID de sesión seguro.
        interaction_index: Índice de interacción.

    Returns:
        ID de trazabilidad determinístico.
    """
    trace_base = f'{session_id}_interaction_{interaction_index:04d}'
    return generate_deterministic_id(trace_base)


def generate_content_hash(content_bytes: bytes) -> str:
    """
    Genera una huella digital (hash MD5) del contenido de un archivo.

    Esta función es ideal para la detección de cambios en el contenido de un archivo,
    ya que un cambio de un solo byte producirá un hash completamente diferente.

    Args:
        content_bytes: El contenido del archivo en formato binario.

    Returns:
        Una cadena hexadecimal de 32 caracteres que representa el hash MD5.
    """
    return hashlib.md5(content_bytes).hexdigest()