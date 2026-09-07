from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from app.database import supabase
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
import uuid
from datetime import datetime, timezone

router = APIRouter(
    prefix="/api/users",
    tags=["Users"]
)

def map_db_user_to_response(user_data: dict, factory_name: Optional[str] = None) -> dict:
    # Handle missing fields carefully just in case
    return {
        "id": user_data.get("user_id", ""),
        "auth_user_id": user_data.get("auth_user_id"),
        "employee_code": user_data.get("employee_code") or user_data.get("user_id", ""),
        "full_name": user_data.get("full_name") or user_data.get("username", "Unknown"),
        "email": user_data.get("email"),
        "phone": user_data.get("phone"),
        "role": user_data.get("user_role", "worker"),
        "factory_id": user_data.get("factory_id"),
        "factory_name": factory_name,
        "rfid_uid": user_data.get("rfid_uid"),
        "status": "active" if user_data.get("status") is True else "inactive",
        "created_at": user_data.get("created_at"),
        "updated_at": user_data.get("updated_at") or user_data.get("created_at")
    }

@router.get("", response_model=UserListResponse)
def get_users(
    search: Optional[str] = None,
    factory_id: Optional[str] = None,
    role: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        query = supabase.table("users").select("*")
        
        if factory_id:
            query = query.eq("factory_id", factory_id)
        if role:
            query = query.eq("user_role", role)
        if status_filter:
            db_status = True if status_filter.lower() == "active" else False
            query = query.eq("status", db_status)
            
        # Execute query
        res = query.execute()
        
        users_data = res.data or []
        
        # In-memory search (since Supabase select doesn't easily do cross-column ilike in python client)
        if search:
            search_lower = search.lower()
            users_data = [
                u for u in users_data
                if (u.get("full_name") and search_lower in u["full_name"].lower()) or
                   (u.get("employee_code") and search_lower in u["employee_code"].lower()) or
                   (u.get("email") and search_lower in u["email"].lower()) or
                   (u.get("rfid_uid") and search_lower in u["rfid_uid"].lower())
            ]
            
        # Pagination
        total = len(users_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = users_data[start:end]
        
        # Fetch factory names
        factory_ids = list(set([u.get("factory_id") for u in paginated_data if u.get("factory_id")]))
        factory_map = {}
        if factory_ids:
            fac_res = supabase.table("factories").select("factory_id, factory_name").in_("factory_id", factory_ids).execute()
            for fac in (fac_res.data or []):
                factory_map[fac["factory_id"]] = fac["factory_name"]
                
        response_data = []
        for u in paginated_data:
            fac_name = factory_map.get(u.get("factory_id"))
            response_data.append(map_db_user_to_response(u, fac_name))
            
        return {
            "data": response_data,
            "total": total,
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str):
    try:
        res = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        user_data = res.data[0]
        
        factory_name = None
        if user_data.get("factory_id"):
            fac_res = supabase.table("factories").select("factory_name").eq("factory_id", user_data["factory_id"]).execute()
            if fac_res.data:
                factory_name = fac_res.data[0]["factory_name"]
                
        return map_db_user_to_response(user_data, factory_name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    try:
        # Check uniqueness of rfid_uid
        if user.rfid_uid:
            res = supabase.table("users").select("user_id").eq("rfid_uid", user.rfid_uid).execute()
            if res.data:
                raise HTTPException(status_code=409, detail="RFID UID already exists")
                
        # Validate factory
        if user.factory_id:
            res = supabase.table("factories").select("factory_id").eq("factory_id", user.factory_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail="Factory not found")
                
        new_user_id = "U" + uuid.uuid4().hex[:8].upper()
        emp_code = "EMP-" + uuid.uuid4().hex[:6].upper()
        
        new_user = {
            "user_id": new_user_id,
            "username": user.email.split("@")[0] if user.email else new_user_id, # Fallback username for login compatibility
            "user_pin": "1234", # Default pin for login compatibility
            "user_role": user.role,
            "factory_id": user.factory_id,
            "status": True if user.status.lower() == "active" else False,
            "employee_code": emp_code,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "rfid_uid": user.rfid_uid,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        res = supabase.table("users").insert(new_user).execute()
        
        # Return response
        return get_user(new_user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user: UserUpdate):
    try:
        # Check if user exists
        existing = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Check uniqueness of rfid_uid if it changed
        if user.rfid_uid and user.rfid_uid != existing.data[0].get("rfid_uid"):
            res = supabase.table("users").select("user_id").eq("rfid_uid", user.rfid_uid).execute()
            if res.data:
                raise HTTPException(status_code=409, detail="RFID UID already exists")
                
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if user.full_name is not None:
            update_data["full_name"] = user.full_name
        if user.email is not None:
            update_data["email"] = user.email
        if user.phone is not None:
            update_data["phone"] = user.phone
        if user.role is not None:
            update_data["user_role"] = user.role
        if user.factory_id is not None:
            update_data["factory_id"] = user.factory_id
        if user.rfid_uid is not None:
            update_data["rfid_uid"] = user.rfid_uid
        if user.status is not None:
            update_data["status"] = True if user.status.lower() == "active" else False
            
        supabase.table("users").update(update_data).eq("user_id", user_id).execute()
        
        return get_user(user_id)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    try:
        # Instead of hard delete, deactivate
        existing = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="User not found")
            
        update_data = {
            "status": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("users").update(update_data).eq("user_id", user_id).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


