from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.d1_client import d1
from pydantic import BaseModel

router = APIRouter(prefix="/api/users", tags=["Users"])

class UserCreate(BaseModel):
    employee_code: str
    full_name: str
    email: str
    role: str
    status: Optional[str] = 'active'

@router.get("")
async def get_users(
    search: Optional[str] = Query(None), 
    role: Optional[str] = Query(None), 
    status: Optional[str] = Query(None), 
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * limit
    where_clauses = []
    params = []
    
    if search:
        where_clauses.append("(full_name LIKE ? OR email LIKE ? OR employee_code LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if role and role.lower() != 'all':
        where_clauses.append("role = ?")
        params.append(role.lower())
    if status and status.lower() != 'all':
        where_clauses.append("status = ?")
        params.append(status.lower())
        
    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    count_res = await d1.execute(f"SELECT COUNT(*) as c FROM users {where_sql}", params)
    total = count_res[0]['c'] if count_res else 0
    
    res = await d1.execute(f"SELECT * FROM users {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?", params + [limit, offset])
    
    return {"data": res, "total": total, "page": page, "limit": limit}

@router.get("/{user_id}")
async def get_user(user_id: str):
    res = await d1.execute("SELECT * FROM users WHERE id = ?", [user_id])
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    return {"data": res[0]}
