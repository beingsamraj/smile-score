
from fastapi import APIRouter
from app.services.d1_client import d1

router = APIRouter(prefix="/api/workers", tags=["Workers"])

@router.get("")
async def get_workers(search: str = None, factory_id: str = None, department_id: str = None, status: str = None, page: int = 1, limit: int = 100):
    res = await d1.execute("SELECT id, employee_id as worker_id, employee_name as name, department as department_name, status FROM employees LIMIT 100")
    for r in res:
        r['status'] = True if r['status'] == 'ACTIVE' else False
    return {"data": res, "total": len(res), "page": page, "limit": limit}

@router.get("/{worker_id}")
async def get_worker(worker_id: str):
    return {}
