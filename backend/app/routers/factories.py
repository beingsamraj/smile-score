from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/factories", tags=["Factories"])

class FactoryCreate(BaseModel):
    factory_name: str
    status: bool = True
    
class FactoryUpdate(BaseModel):
    factory_name: Optional[str] = None
    status: Optional[bool] = None

@router.get("")
async def get_factories(
    search: Optional[str] = Query(None), 
    status: Optional[str] = Query(None)
):
    return [{"factory_id": "FAC001", "factory_name": "Main Plant", "status": True}]

@router.post("")
async def create_factory(factory_data: FactoryCreate):
    return {"success": True, "factory": {"factory_id": "FAC002", "factory_name": factory_data.factory_name, "status": factory_data.status}}

@router.put("/{factory_id}")
async def update_factory(factory_id: str, factory_data: FactoryUpdate):
    return {"success": True}

@router.get("/{factory_id}")
async def get_factory(factory_id: str):
    return {"factory_id": "FAC001", "factory_name": "Main Plant", "status": True}
