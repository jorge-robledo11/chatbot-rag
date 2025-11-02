#!/bin/bash
# ==============================================================================
# Script de Reseteo Completo para el Proyecto Ajover
#
# Borra de forma segura y concurrente:
#   1. Los blobs de imágenes procesadas en Azure Blob Storage.
#   2. El índice de búsqueda en Azure AI Search.
#
# Uso:
#   ./cleanup.sh           # Borra ambos (pedirá confirmación)
#   ./cleanup.sh --yes     # Borra ambos (sin confirmación)
#   ./cleanup.sh --blobs   # Borra solo los blobs
#   ./cleanup.sh --index   # Borra solo el índice
# ==============================================================================

set -e

# Crear un archivo Python temporal de forma segura
SCRIPT_PY="$(mktemp cleanup_script_XXXXXX.py)"

# Usar un heredoc para escribir el código Python en el archivo temporal
cat > "$SCRIPT_PY" << 'EOF'
import asyncio
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# --- Dependencias de Azure ---
from azure.storage.blob.aio import BlobServiceClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# --- Configuración del Logger ---
logger.remove()
logger.add(sys.stderr, level="INFO", colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")

# --- Funciones de Limpieza Específicas ---

async def delete_azure_blobs(connection_string: str, container_name: str):
    """Borra todos los blobs bajo el prefijo 'imagenes-procesadas/'."""
    prefix = "imagenes-procesadas/"
    logger.info(f"Conectando a Blob Storage para limpiar la carpeta '{prefix}'...")
    
    async with BlobServiceClient.from_connection_string(connection_string) as client:
        container_client = client.get_container_client(container_name)
        
        blobs_to_delete = [blob.name async for blob in container_client.list_blobs(name_starts_with=prefix)]
        
        if not blobs_to_delete:
            logger.success(f"✅ La carpeta de blobs '{prefix}' ya está limpia. No hay nada que hacer.")
            return

        logger.warning(f"Se encontraron {len(blobs_to_delete)} blobs para eliminar en '{prefix}'.")
        delete_tasks = [container_client.delete_blob(blob) for blob in blobs_to_delete]
        await asyncio.gather(*delete_tasks)
        logger.success(f"🗑️✅ Se eliminaron {len(blobs_to_delete)} blobs con éxito.")

async def delete_azure_search_index(endpoint: str, api_key: str, index_name: str):
    """Borra un índice de Azure AI Search si existe."""
    logger.info(f"Conectando a Azure AI Search para eliminar el índice '{index_name}'...")
    
    async with SearchIndexClient(endpoint, AzureKeyCredential(api_key)) as client:
        try:
            await client.get_index(index_name)
            logger.warning(f"Se encontró el índice '{index_name}'. Procediendo a eliminarlo...")
            await client.delete_index(index_name)
            logger.success(f"🗑️✅ Índice '{index_name}' eliminado con éxito.")
        except HttpResponseError as e:
            if e.status_code == 404:
                logger.success(f"✅ El índice '{index_name}' no existe. Ya está limpio.")
            else:
                logger.error(f"❌ Error inesperado al intentar acceder al índice '{index_name}': {e.message}")
                raise
        except Exception:
            logger.exception(f"❌ Fallo crítico al intentar eliminar el índice '{index_name}'.")
            raise

async def main():
    """Punto de entrada principal del script de limpieza."""
    logger.info("🚀 Iniciando script de reseteo completo del entorno...")
    
    # --- Carga de Configuración ---
    load_dotenv()
    blob_conn_str = os.getenv("BLOB_STORAGE_CONNECTION_STRING")
    blob_container = os.getenv("BLOB_STORAGE_CONTAINER_NAME")
    search_endpoint = os.getenv("AZURE_SEARCH_AI_ENDPOINT")
    search_api_key = os.getenv("AZURE_SEARCH_AI_API_KEY")
    search_index_name = os.getenv("AZURE_SEARCH_AI_PDF_INDEX")

    if not all([blob_conn_str, blob_container, search_endpoint, search_api_key, search_index_name]):
        logger.critical("❌ Faltan variables de entorno. Asegúrate de que todas las claves de Blob Storage y AI Search estén en tu .env")
        sys.exit(1)
        
    # --- Análisis de Argumentos ---
    args = sys.argv[1:]
    delete_blobs_flag = "--blobs" in args or not ("--blobs" in args or "--index" in args)
    delete_index_flag = "--index" in args or not ("--blobs" in args or "--index" in args)
    
    # --- Lógica de Ejecución ---
    tasks = []
    if delete_blobs_flag:
        tasks.append(delete_azure_blobs(blob_conn_str, blob_container))
    if delete_index_flag:
        tasks.append(delete_azure_search_index(search_endpoint, search_api_key, search_index_name))

    if not tasks:
        logger.info("No se especificó ninguna acción. Usa --blobs, --index o ninguna para ambos.")
        return

    logger.info("Ejecutando tareas de limpieza de forma concurrente...")
    await asyncio.gather(*tasks)
    logger.success("🎉 Reseteo del entorno completado con éxito.")

if __name__ == "__main__":
    asyncio.run(main())
EOF

# --- Lógica de Confirmación de Seguridad ---
if [[ " $* " != *" --yes "* ]]; then
    echo "=========================================================="
    echo "⚠️ ADVERTENCIA: Estás a punto de borrar datos PERMANENTEMENTE."
    echo "   - Imágenes procesadas en Azure Blob Storage."
    echo "   - El índice de búsqueda 'ajover-index' en Azure AI Search."
    echo "=========================================================="
    read -p "Escribe 'BORRAR' para confirmar: " CONFIRMATION
    if [ "$CONFIRMATION" != "BORRAR" ]; then
        echo "❌ Operación cancelada por el usuario."
        rm -f "$SCRIPT_PY"
        exit 1
    fi
fi

# Ejecutar el script Python con uv, pasando todos los argumentos
echo "Iniciando la ejecución del script de limpieza..."
uv run python "$SCRIPT_PY" "$@"

# Limpiar el archivo temporal
rm -f "$SCRIPT_PY"
