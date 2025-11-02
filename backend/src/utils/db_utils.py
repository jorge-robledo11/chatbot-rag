"""
Utilidades para gestión de base de datos MongoDB con Motor.

Este módulo proporciona funciones auxiliares para la gestión
de colecciones y operaciones básicas de base de datos.
"""

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError


async def ensure_collection_exists(
    db: AsyncIOMotorDatabase, collection_name: str
) -> None:
    """
    Crea la colección si no existe (no afecta si ya existe).

    Args:
        db: Instancia de la base de datos MongoDB.
        collection_name: Nombre de la colección a crear.

    Raises:
        RuntimeError: Si ocurre un error al listar o crear la colección.
    """
    try:
        names = await db.list_collection_names()
        if collection_name not in names:
            await db.create_collection(collection_name)
            logger.info(f"✅ Colección '{collection_name}' creada.")
        else:
            logger.debug(f"📁 Colección '{collection_name}' ya existe.")
    except PyMongoError as e:
        logger.error(
            f"❌ MongoDB error en ensure_collection_exists('{collection_name}'): {e}"
        )
        raise RuntimeError(
            f"Error al asegurar colección '{collection_name}': {e}"
        ) from e
