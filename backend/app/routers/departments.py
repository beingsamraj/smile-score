from fastapi import APIRouter
from typing import Optional
from app.services.d1_client import d1

dept_router = APIRouter(prefix="/api/departments", tags=["Departments"])

@dept_router.get("")
async def list_departments(factory_id: Optional[str] = None):
    try:
        sql = "SELECT * FROM departments"
        params = []
        if factory_id:
            sql += " WHERE factory_id = ?"
            params.append(factory_id)
            
        res = await d1.execute(sql, params)
        return {"data": res or [], "total": len(res or [])}
    except Exception as e:
        return {"data": [], "total": 0, "error": str(e)}
