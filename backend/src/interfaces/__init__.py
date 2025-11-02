"""
Interfaces de contrato del sistema.

Este módulo expone las interfaces más importantes del sistema para facilitar
su importación y mantener la consistencia arquitectónica.
"""

from .batch_interface import BatchInterface
from .blob_storage_interface import BlobStorageInterface
from .change_detector_interface import ChangeDetectorInterface
from .cosmos_db_sessions_interface import CosmosDBSessionsInterface
from .cosmos_db_users_interface import CosmosDBUsersInterface
from .image_interface import ImageInterface
from .openai_interface import OpenAIInterface
from .parser_interface import ParserInterface
from .searchai_interface import SearchAIInterface

__all__ = [
    'BatchInterface',
    'BlobStorageInterface',
    'ChangeDetectorInterface',
    'CosmosDBSessionsInterface',
    'CosmosDBUsersInterface',
    'ImageInterface',
    'OpenAIInterface',
    'ParserInterface',
    'SearchAIInterface',
]
