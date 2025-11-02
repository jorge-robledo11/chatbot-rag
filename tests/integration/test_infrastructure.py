import pytest
from backend.src.infrastructure import get_infrastructure

@pytest.mark.asyncio
async def test_infrastructure_lifecycle():
    """
    Test end-to-end de la infraestructura: inicialización y cierre.
    """
    infra = get_infrastructure()

    # Test: inicialización de servicios
    openai = await infra.get_openai()
    assert openai is not None, "OpenAI no se inicializó."

    searchai = await infra.get_searchai()
    assert searchai is not None, "SearchAI no se inicializó."

    blob_storage = await infra.get_blob_storage()
    assert blob_storage is not None, "BlobStorage no se inicializó."

    session_manager = await infra.get_cosmos_db_session()
    assert session_manager is not None, "CosmosDBSessionManager no se inicializó."

    user_manager = await infra.get_cosmos_db_user()
    assert user_manager is not None, "CosmosDBUserManager no se inicializó."

    # Test: shutdown (cierre de recursos)
    await infra.shutdown()
