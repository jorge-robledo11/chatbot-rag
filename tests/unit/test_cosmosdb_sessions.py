import pytest
from uuid import uuid4
from backend.src.core.dependencies import get_session_manager
from backend.src.models.common import ChatMessage, SessionStatus

@pytest.mark.asyncio
async def test_crud_cosmosdb_sessions():
    sessions = await get_session_manager()
    try:
        user_id = str(uuid4())

        # Crear sesión
        session = await sessions.create_session(user_id)
        assert session.user_id == user_id

        # Recuperar sesión
        fetched = await sessions.get_session(session.session_id)
        assert fetched is not None
        assert fetched.user_id == user_id

        # Agregar mensaje al historial
        msg = ChatMessage(role="user", content="Hola, ¿estás ahí?")
        updated = await sessions.add_message_to_history(session.session_id, msg)
        assert len(updated.chat_history) > 0
        assert updated.chat_history[-1].content == "Hola, ¿estás ahí?"

        # Cambiar estado de la sesión
        updated_status = await sessions.update_session_status(session.session_id, SessionStatus.INACTIVE)
        assert updated_status.status == SessionStatus.INACTIVE

        # Limpiar historial
        cleared = await sessions.clear_history(session.session_id)
        assert cleared.chat_history == []
    finally:
        await sessions.close()
