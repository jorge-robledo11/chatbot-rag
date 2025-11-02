import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from backend.src.models.documents import EnrichedDocument
from pipelines import pdf_indexing_pipeline

@pytest.mark.asyncio
async def test_full_pipeline_integration(mocker, mock_blob_to_process):
    # Arrange: Mockear las dependencias de más bajo nivel (infraestructura)
    mock_blob_storage_instance = MagicMock()
    mock_blob_storage_instance.get_blobs.return_value = [mock_blob_to_process]
    mock_blob_storage_instance.download_blob.return_value = mock_blob_to_process.content
    mocker.patch('backend.pipelines.indexing_pipeline.BlobStorage', return_value=mock_blob_storage_instance)

    mock_search_ai_instance = MagicMock()
    mock_search_ai_instance.get_documents_metadata = AsyncMock(return_value={}) # Simula que no hay docs en el índice
    mock_search_ai_instance.upload_documents = AsyncMock() # La llamada final que verificaremos
    mocker.patch('backend.pipelines.indexing_pipeline.SearchAI', return_value=mock_search_ai_instance)

    # Mockear el servicio de OpenAI para que devuelva resultados predecibles
    mock_openai_instance = MagicMock()
    def mock_run_batch_job(requests, endpoint):
        if "chat/completions" in endpoint:
            # Simular respuesta de análisis de imagen
            return asyncio.completed_future([
                {
                    "custom_id": f"doc:{mock_blob_to_process.name}|page:1",
                    "response": {"body": {"choices": [{"message": {"content": "Descripcion de imagen."}}]}}
                }
            ])
        elif "embeddings" in endpoint:
            # Simular respuesta de embedding
            return asyncio.completed_future([
                {
                    "custom_id": f"doc:{mock_blob_to_process.name}",
                    "response": {"body": {"data": [{"embedding": [0.1, 0.2, 0.3]}]}}
                }
            ])
        return asyncio.completed_future([])
    
    mock_openai_instance.run_batch_job = mock_run_batch_job
    mocker.patch('backend.pipelines.indexing_pipeline.OpenAI', return_value=mock_openai_instance)
    mocker.patch('backend.src.infraestructure.searchai.OpenAI', return_value=mock_openai_instance)

    # Act: Ejecutar el punto de entrada principal del pipeline
    await pdf_indexing_pipeline.main()

    # Assert: Verificar el resultado final
    mock_search_ai_instance.upload_documents.assert_called_once()
    
    # Inspeccionar los argumentos con los que se llamó a upload_documents
    call_args = mock_search_ai_instance.upload_documents.call_args
    uploaded_docs = call_args.args[0]
    
    assert len(uploaded_docs) == 1
    doc: EnrichedDocument = uploaded_docs[0]
    
    assert doc.id == "catalogo_tejas_2024_pdf"
    assert "Este es el texto de prueba" in doc.content
    assert "Descripcion de Imagen en Página 1" in doc.content
    assert doc.content_vector == [0.1, 0.2, 0.3]
    assert doc.md5_hash is not None
