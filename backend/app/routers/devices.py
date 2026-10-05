
from fastapi import APIRouter
from app.services.d1_client import d1

router = APIRouter(prefix="/api/devices", tags=["Devices"])

@router.get("")
async def get_devices(search: str = None, factory_id: str = None, type: str = None, status: str = None, page: int = 1, limit: int = 100):
    # device_code mapped from device_id
    res = await d1.execute("SELECT id, device_id as device_code, device_name, device_type, status, location as factory_name FROM devices LIMIT 100")
    for r in res:
        r['status'] = r['status'].lower()
    return {"data": res, "total": len(res), "page": page, "limit": limit}

@router.get("/{device_id}")
async def get_device(device_id: str):
    return {}
