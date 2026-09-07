from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.database import supabase

dept_router = APIRouter(prefix="/api/departments", tags=["Departments"])

@dept_router.get("")
def list_departments(factory_id: Optional[str] = None):
    try:
        query = supabase.table("departments").select("*")
        if factory_id:
            query = query.eq("factory_id", factory_id)
        res = query.execute()
        return {"data": res.data or [], "total": len(res.data or [])}
    except Exception as e:
        return {"data": [], "total": 0, "error": str(e)}
