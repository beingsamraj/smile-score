from fastapi import APIRouter, HTTPException, Query
from app.services.d1_client import d1
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api/devices", tags=["Devices"])

@router.get("")
async def get_devices(
    search: Optional[str] = Query(None, description="Search term"), 
    factory_id: Optional[str] = Query(None, description="Factory ID"), 
    type: Optional[str] = Query(None, description="Device Type"), 
    status: Optional[str] = Query(None, description="Device Status"), 
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * limit
    where_clauses = []
    params = []
    
    if search:
        where_clauses.append("(device_name LIKE ? OR device_id LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    if status:
        where_clauses.append("status = ?")
        params.append(status.upper())
    if type:
        where_clauses.append("device_type = ?")
        params.append(type)
        
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # Get total
    count_res = await d1.execute(f"SELECT COUNT(*) as c FROM devices{where_sql}", params)
    total = count_res[0]['c'] if count_res else 0
    
    # Get paginated data
    sql = f"SELECT id, device_id as device_code, device_name, device_type, status, location as factory_name FROM devices{where_sql} LIMIT ? OFFSET ?"
    res = await d1.execute(sql, params + [limit, offset])
    
    for r in res:
        r['status'] = str(r['status']).lower()
        
    return {"data": res, "total": total, "page": page, "limit": limit}

@router.get("/{device_id}")
async def get_device(device_id: str):
    res = await d1.execute("SELECT id, device_id as device_code, device_name, device_type, status, location as factory_name FROM devices WHERE device_id = ?", [device_id])
    if not res:
        raise HTTPException(status_code=404, detail="Device not found")
    r = res[0]
    r['status'] = str(r['status']).lower()
    return {"data": r}
