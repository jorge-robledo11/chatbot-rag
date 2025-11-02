"""
Paquete de utilidades para el sistema Ajover.

Este __init__.py expone las funciones más comunes de los sub-módulos
para facilitar su importación en otras partes de la aplicación.
"""

from .identity_utils import (
    generate_deterministic_id,
    generate_deterministic_trace_id,
    generate_document_id,
    generate_image_id,
    generate_secure_session_id,
)
from .prompts_utils import (
    IMAGE_ANALYSIS_SYSTEM_PROMPT,
    IMAGE_ANALYSIS_USER_PROMPT,
    RAG_SYSTEM_PROMPTS,
    build_rag_user_prompt,
    get_rag_system_prompt,
    get_specialized_prompts,
)
from .text_utils import (
    count_tokens,
    sanitize_user_input,
)
from .time_utils import (
    get_colombia_time,
)
from .validation_utils import (
    validate_document_id_format,
    validate_image_id_format,
    validate_session_id_format,
)

__all__ = [
    'IMAGE_ANALYSIS_SYSTEM_PROMPT',
    'IMAGE_ANALYSIS_USER_PROMPT',
    'RAG_SYSTEM_PROMPTS',
    'build_rag_user_prompt',
    'count_tokens',
    'generate_deterministic_id',
    'generate_deterministic_trace_id',
    'generate_document_id',
    'generate_image_id',
    'generate_secure_session_id',
    'get_colombia_time',
    'get_rag_system_prompt',
    'get_specialized_prompts',
    'sanitize_user_input',
    'validate_document_id_format',
    'validate_image_id_format',
    'validate_session_id_format',
]
