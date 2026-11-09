import pytest


async def _login(client) -> str:
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "ChangeMe123!"},
    )
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_requires_authentication(client):
    r = await client.get("/api/v1/users")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_and_list_user(client):
    token = await _login(client)
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "email": "buyer1@example.com",
            "password": "BuyerPass123!",
            "full_name": "Buyer One",
            "role_ids": [],
        },
    )
    assert r.status_code == 201, r.text
    created_id = r.json()["id"]

    r2 = await client.get("/api/v1/users", headers=headers)
    assert r2.status_code == 200
    ids = [u["id"] for u in r2.json()["items"]]
    assert created_id in ids