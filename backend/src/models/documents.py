"""
Modelos de datos para documentos y procesamiento de blobs.

Define las estructuras de datos utilizadas para el procesamiento
de documentos y su indexación en Azure AI Search.
"""

from datetime import datetime
from typing import TypedDict


class BlobToProcess(TypedDict):
    """
    Estructura de datos para un blob que necesita procesamiento.

    - name: Nombre completo del blob (ej: 'pdfs-fuente/doc.pdf')
    - content: Contenido binario del blob
    - current_hash: Hash MD5 actual del contenido del blob
    """

    name: str
    content: bytes
    current_hash: str


class BlobData(TypedDict):
    """
    Estructura de datos para un blob a procesar.

    - name: Nombre completo del blob (ej: 'pdfs-fuente/doc.pdf')
    - content: Contenido binario del blob
    - current_hash: Hash MD5 actual del contenido del blob
    """

    name: str
    content: bytes
    size: int
    last_modified: datetime
    content_type: str


class EnrichedDocument(TypedDict):
    """
    Representa un documento que ha sido procesado y enriquecido.

    - id: Identificador único del documento
    - content: Contenido del documento
    - content_vector: Vector de contenido del documento
    - source_file: Nombre del archivo fuente
    - source_file_hash: Hash MD5 del archivo fuente
    - image_urls: URLs de las imágenes del documento
    - image_descriptions: Descripciones de las imágenes del documento
    """

    id: str
    content: str
    content_vector: list[float]
    source_file: str
    source_file_hash: str
    image_urls: list[str]
    image_descriptions: list[str]
