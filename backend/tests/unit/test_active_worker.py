import pytest
from app.services.active_worker import ActiveWorkerState

@pytest.mark.asyncio
async def test_active_worker_lifecycle():
    state = ActiveWorkerState()
    
    # Initially None
    res = await state.get_active_worker()
    assert res is None
    
    # Set worker
    await state.set_active_worker("ESSL001", "W001", timeout_seconds=10)
    res = await state.get_active_worker()
    assert res is not None
    assert res["worker_id"] == "W001"
    assert res["essl_employee_id"] == "ESSL001"
    
    # Clear worker
    await state.clear_active_worker()
    res = await state.get_active_worker()
    assert res is None

@pytest.mark.asyncio
async def test_active_worker_expiration():
    state = ActiveWorkerState()
    # Set with 0 timeout to test expiration immediately
    await state.set_active_worker("ESSL002", "W002", timeout_seconds=-1)
    res = await state.get_active_worker()
    assert res is None
