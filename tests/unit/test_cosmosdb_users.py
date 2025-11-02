import pytest
from uuid import uuid4
from backend.src.core.dependencies import get_user_manager
from backend.src.models.common import User

@pytest.mark.asyncio
async def test_crud_cosmosdb_users():
    users = await get_user_manager()
    try:
        email = f"test-{uuid4()}@example.com"
        password = "superSecretPass123!"

        # Crear usuario
        user: User = await users.create_user(email, password)
        assert user.email == email
        assert user.user_id is not None

        # Obtener usuario por ID
        fetched_by_id = await users.get_user_by_id(user.user_id)
        assert fetched_by_id is not None
        assert fetched_by_id.email == email

        # Obtener usuario por email
        fetched_by_email = await users.get_user_by_email(email)
        assert fetched_by_email is not None
        assert fetched_by_email.user_id == user.user_id

        # Validar que el password está hasheado y nunca es igual al texto plano
        assert fetched_by_id.hashed_password != password
        assert len(fetched_by_id.hashed_password) > 10  # Normal para un hash bcrypt/argon2
    finally:
        await users.close()
