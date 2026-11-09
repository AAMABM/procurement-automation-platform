import pytest


@pytest.mark.asyncio
async def test_liveness(client):
    r = await client.get("/api/v1/health/live")
    assert r.status_code == 200
    assert r.json() == {"status": "alive"}


@pytest.mark.asyncio
async def test_readiness(client):
    r = await client.get("/api/v1/health/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"