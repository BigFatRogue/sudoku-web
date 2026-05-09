import pytest
from httpx import AsyncClient
from app.core.enums import UuidEnum


@pytest.mark.asyncio
async def test_page_index(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_page_login(async_client: AsyncClient):
    response = await async_client.get("/login")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_auth_user(async_client: AsyncClient):
    response = await async_client.post("/api/v1/auth/user")
    assert response.status_code == 200

    assert response.cookies.get(UuidEnum.guest_uuid)

    data = response.json()
    assert data['user_id'] > 1
    assert data['username'] is None
    assert data['type_user'] == 'guest'


@pytest.mark.asyncio
async def test_auth_registration(async_client: AsyncClient):
    form_reg = {
        'email': 'user@email.com',
        'password': '12345678',
        'password_repet': '12345678'
    }

    response = await async_client.post(
        url="/api/v1/auth/registration", 
        data=form_reg)
    
    assert response.status_code == 200

    assert response.cookies.get(UuidEnum.session_uuid)
    
    data = response.json()
    assert data['user_id'] > 1
    assert data['username'] == 'user'
    assert data['type_user'] == 'user'

