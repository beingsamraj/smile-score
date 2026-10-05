
from fastapi import APIRouter
from app.services.d1_client import d1

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("")
async def get_users(search: str = None, factory_id: str = None, role: str = None, status: str = None, page: int = 1, limit: int = 100):
    # Mocking users since D1 schema dropped it
    return {"data": [{"id": "USR001", "employee_code": "ADMIN001", "full_name": "Admin User", "email": "admin@smilescore.com", "role": "admin", "status": "active"}], "total": 1, "page": page, "limit": limit}
