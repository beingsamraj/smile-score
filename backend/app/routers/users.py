from fastapi import APIRouter, Query, HTTPException
from typing import Optional

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("")
async def get_users(
    search: Optional[str] = Query(None), 
    factory_id: Optional[str] = Query(None), 
    role: Optional[str] = Query(None), 
    status: Optional[str] = Query(None), 
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100)
):
    # Mocking users since D1 schema dropped it
    # Pydantic validation handles safety for params above
    data = [{"id": "USR001", "employee_code": "ADMIN001", "full_name": "Admin User", "email": "admin@smilescore.com", "role": "admin", "status": "active"}]
    return {"data": data, "total": 1, "page": page, "limit": limit}

@router.get("/{user_id}")
async def get_user(user_id: str):
    if user_id != "USR001":
        raise HTTPException(status_code=404, detail="User not found")
    return {"data": {"id": "USR001", "employee_code": "ADMIN001", "full_name": "Admin User", "email": "admin@smilescore.com", "role": "admin", "status": "active"}}
