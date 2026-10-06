import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_forecast_insufficient_data():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/forecast/factory/UNKNOWN_FAC")
    
    # Missing factory
    assert response.status_code == 404
    
@pytest.mark.asyncio
async def test_risk_factory_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/risk/factory/UNKNOWN_FAC")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_recommendations_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/recommendations/factory/UNKNOWN_FAC")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_risk_factories_pagination():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/risk/factories?page=1&limit=5")
        
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
