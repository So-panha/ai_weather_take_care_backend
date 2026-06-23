import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "strongpassword123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient):
    # First register
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "strongpassword123"
        }
    )
    
    # Then login
    response = await async_client.post(
        "/api/v1/auth/login",
        data={
            "username": "login@example.com",
            "password": "strongpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
