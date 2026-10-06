import pytest
from app.services.d1_client import D1Client
import httpx

@pytest.mark.asyncio
async def test_d1_client_init():
    client = D1Client()
    assert client is not None
    assert client._http_client is None
    await client.close()

@pytest.mark.asyncio
async def test_d1_client_http_pool():
    client = D1Client()
    http_client = await client._get_http_client()
    assert isinstance(http_client, httpx.AsyncClient)
    assert not http_client.is_closed
    await client.close()
    assert http_client.is_closed
