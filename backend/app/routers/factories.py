from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.services.d1_client import d1
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/api/factories", tags=["Factories"])

class FactoryCreate(BaseModel):
    factory_name: str
    location: Optional[str] = None
    status: bool = True
    
class FactoryUpdate(BaseModel):
    factory_name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[bool] = None

@router.get("")
async def get_factories(
    search: Optional[str] = Query(None), 
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * limit
    where_clauses = []
    params = []
    
    if search:
        where_clauses.append("factory_name LIKE ?")
        params.append(f"%{search}%")
    if status is not None and status.lower() != "all":
        if status.lower() == "true":
            where_clauses.append("status = 1")
        elif status.lower() == "false":
            where_clauses.append("status = 0")
            
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    count_res = await d1.execute(f"SELECT COUNT(*) as c FROM factories{where_sql}", params)
    total = count_res[0]['c'] if count_res else 0
    
    sql = f"SELECT factory_id, factory_name, location, status, created_at FROM factories{where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?"
    res = await d1.execute(sql, params + [limit, offset])
    
    for r in res:
        r['status'] = bool(r.get('status'))
        
    return {"data": res, "total": total, "page": page, "limit": limit}

@router.post("")
async def create_factory(factory_data: FactoryCreate):
    factory_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    status_int = 1 if factory_data.status else 0
    
    sql = """
    INSERT INTO factories (factory_id, factory_name, location, status, created_at)
    VALUES (?, ?, ?, ?, ?)
    RETURNING *
    """
    res = await d1.execute(sql, [factory_id, factory_data.factory_name, factory_data.location, status_int, now])
    
    if not res:
        raise HTTPException(status_code=500, detail="Failed to create factory")
        
    created = res[0]
    created['status'] = bool(created.get('status'))
    return {"success": True, "data": created}

@router.put("/{factory_id}")
async def update_factory(factory_id: str, factory_data: FactoryUpdate):
    # Get current
    current = await d1.execute("SELECT * FROM factories WHERE factory_id = ?", [factory_id])
    if not current:
        raise HTTPException(status_code=404, detail="Factory not found")
        
    updates = []
    params = []
    
    if factory_data.factory_name is not None:
        updates.append("factory_name = ?")
        params.append(factory_data.factory_name)
    if factory_data.location is not None:
        updates.append("location = ?")
        params.append(factory_data.location)
    if factory_data.status is not None:
        updates.append("status = ?")
        params.append(1 if factory_data.status else 0)
        
    if not updates:
        return {"success": True, "data": current[0]}
        
    params.append(factory_id)
    sql = f"UPDATE factories SET {', '.join(updates)} WHERE factory_id = ? RETURNING *"
    res = await d1.execute(sql, params)
    
    if not res:
        raise HTTPException(status_code=500, detail="Failed to update factory")
        
    updated = res[0]
    updated['status'] = bool(updated.get('status'))
    return {"success": True, "data": updated}

@router.get("/{factory_id}")
async def get_factory(factory_id: str):
    res = await d1.execute("SELECT factory_id, factory_name, location, status, created_at FROM factories WHERE factory_id = ?", [factory_id])
    if not res:
        raise HTTPException(status_code=404, detail="Factory not found")
        
    r = res[0]
    r['status'] = bool(r.get('status'))
    return {"data": r}
