from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from datetime import datetime
import uuid
from app.database import supabase
from app.schemas.factory import FactoryCreate, FactoryUpdate

router = APIRouter(prefix="/api/factories", tags=["factories"])

def generate_factory_code() -> str:
    res = supabase.table("factories").select("factory_id").order("created_at", desc=True).limit(1).execute()
    if res.data and len(res.data) > 0:
        last_id = res.data[0].get("factory_id", "F000")
        try:
            # Assuming pattern F001
            num = int(last_id.replace("F", ""))
            return f"F{(num + 1):03d}"
        except:
            return f"F{str(uuid.uuid4())[:3].upper()}"
    return "F001"

@router.get("")
def list_factories(search: Optional[str] = None, status_filter: Optional[str] = Query(None, alias="status")):
    try:
        query = supabase.table("factories").select("*")
        if status_filter and status_filter in ["active", "inactive"]:
            is_active = status_filter == "active"
            query = query.eq("status", is_active)
        if search:
            query = query.or_(f"factory_name.ilike.%{search}%,factory_address.ilike.%{search}%,factory_id.ilike.%{search}%")
            
        res = query.order("created_at", desc=True).execute()
        
        if not hasattr(res, 'data'):
            return {"data": [], "total": 0}
            
        return {"data": res.data or [], "total": len(res.data or [])}
    except Exception as e:
        return {"data": [], "total": 0, "error": str(e)}

@router.get("/{factory_id}")
def get_factory(factory_id: str):
    res = supabase.table("factories").select("*").eq("factory_id", factory_id).execute()
    if not res.data or len(res.data) == 0:
        raise HTTPException(status_code=404, detail="Factory not found")
    return res.data[0]

@router.post("", status_code=status.HTTP_201_CREATED)
def create_factory(factory: FactoryCreate):
    try:
        factory_code = generate_factory_code()
        
        data = factory.model_dump(exclude_unset=True)
        data["factory_id"] = factory_code
        data["created_at"] = datetime.utcnow().isoformat()
        
        res = supabase.table("factories").insert(data).execute()
        if not res.data or len(res.data) == 0:
            raise HTTPException(status_code=400, detail="Failed to create factory")
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{factory_id}")
def update_factory(factory_id: str, factory: FactoryUpdate):
    existing = supabase.table("factories").select("factory_id").eq("factory_id", factory_id).execute()
    if not existing.data or len(existing.data) == 0:
        raise HTTPException(status_code=404, detail="Factory not found")
        
    data = factory.model_dump(exclude_unset=True)
    if not data:
        return get_factory(factory_id)
        
    try:
        res = supabase.table("factories").update(data).eq("factory_id", factory_id).execute()
        return res.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{factory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_factory(factory_id: str):
    users_check = supabase.table("users").select("user_id").eq("factory_id", factory_id).limit(1).execute()
    if users_check.data and len(users_check.data) > 0:
        raise HTTPException(status_code=409, detail="This factory cannot be deleted because it has associated user records.")
        
    try:
        res = supabase.table("factories").delete().eq("factory_id", factory_id).execute()
        if not res.data or len(res.data) == 0:
            raise HTTPException(status_code=404, detail="Factory not found")
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
