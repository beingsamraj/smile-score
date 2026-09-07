from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional
from app.database import supabase
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceListResponse
import uuid
from datetime import datetime, timezone

router = APIRouter(
    prefix="/api/devices",
    tags=["Devices"]
)

def map_db_device_to_response(device_data: dict, factory_name: Optional[str] = None) -> dict:
    device_id = device_data.get("device_id", "")
    
    # Map status boolean to string
    status_str = "inactive"
    db_status = device_data.get("status")
    if db_status is True:
        status_str = "online"
    elif db_status is False:
        status_str = "inactive"
        
    return {
        "id": device_id,
        "device_code": device_id,
        "device_name": device_data.get("device_name", ""),
        "device_type": device_data.get("device_type", "other"),
        "factory_id": device_data.get("factory_id"),
        "factory_name": factory_name,
        "mac_address": device_data.get("mac_address"),
        "location": device_data.get("location"),
        "firmware_version": device_data.get("firmware_version"),
        "description": device_data.get("description"),
        "status": status_str,
        "last_seen": device_data.get("last_seen"),
        "created_at": device_data.get("created_at"),
        "updated_at": device_data.get("updated_at") or device_data.get("created_at")
    }

@router.get("", response_model=DeviceListResponse)
def get_devices(
    search: Optional[str] = None,
    factory_id: Optional[str] = None,
    device_type: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    try:
        query = supabase.table("devices").select("*")
        
        if factory_id:
            query = query.eq("factory_id", factory_id)
        if device_type:
            query = query.eq("device_type", device_type)
        if status_filter:
            if status_filter.lower() in ["online"]:
                query = query.eq("status", True)
            else:
                query = query.eq("status", False)
            
        res = query.execute()
        devices_data = res.data or []
        
        if search:
            search_lower = search.lower()
            devices_data = [
                d for d in devices_data
                if (d.get("device_name") and search_lower in d["device_name"].lower()) or
                   (d.get("device_id") and search_lower in d["device_id"].lower()) or
                   (d.get("mac_address") and search_lower in d["mac_address"].lower()) or
                   (d.get("location") and search_lower in d["location"].lower())
            ]
            
        total = len(devices_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = devices_data[start:end]
        
        factory_ids = list(set([d.get("factory_id") for d in paginated_data if d.get("factory_id")]))
        factory_map = {}
        if factory_ids:
            fac_res = supabase.table("factories").select("factory_id, factory_name").in_("factory_id", factory_ids).execute()
            for fac in (fac_res.data or []):
                factory_map[fac["factory_id"]] = fac["factory_name"]
                
        response_data = []
        for d in paginated_data:
            fac_name = factory_map.get(d.get("factory_id"))
            response_data.append(map_db_device_to_response(d, fac_name))
            
        return {
            "data": response_data,
            "total": total,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(device_id: str):
    try:
        res = supabase.table("devices").select("*").eq("device_id", device_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Device not found")
            
        device_data = res.data[0]
        factory_name = None
        if device_data.get("factory_id"):
            fac_res = supabase.table("factories").select("factory_name").eq("factory_id", device_data["factory_id"]).execute()
            if fac_res.data:
                factory_name = fac_res.data[0]["factory_name"]
                
        return map_db_device_to_response(device_data, factory_name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(device: DeviceCreate):
    try:
        if device.mac_address:
            res = supabase.table("devices").select("device_id").eq("mac_address", device.mac_address).execute()
            if res.data:
                raise HTTPException(status_code=409, detail="MAC Address already exists")
                
        if device.factory_id:
            res = supabase.table("factories").select("factory_id").eq("factory_id", device.factory_id).execute()
            if not res.data:
                raise HTTPException(status_code=404, detail="Factory not found")
                
        new_device_id = "DEV-" + uuid.uuid4().hex[:6].upper()
        
        new_device = {
            "device_id": new_device_id,
            "device_name": device.device_name,
            "device_type": device.device_type,
            "factory_id": device.factory_id,
            "mac_address": device.mac_address,
            "location": device.location,
            "firmware_version": device.firmware_version,
            "description": device.description,
            "status": True if device.status.lower() == "online" else False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        supabase.table("devices").insert(new_device).execute()
        return get_device(new_device_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(device_id: str, device: DeviceUpdate):
    try:
        existing = supabase.table("devices").select("*").eq("device_id", device_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Device not found")
            
        if device.mac_address and device.mac_address != existing.data[0].get("mac_address"):
            res = supabase.table("devices").select("device_id").eq("mac_address", device.mac_address).execute()
            if res.data:
                raise HTTPException(status_code=409, detail="MAC Address already exists")
                
        update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if device.device_name is not None:
            update_data["device_name"] = device.device_name
        if device.device_type is not None:
            update_data["device_type"] = device.device_type
        if device.factory_id is not None:
            update_data["factory_id"] = device.factory_id
        if device.mac_address is not None:
            update_data["mac_address"] = device.mac_address
        if device.location is not None:
            update_data["location"] = device.location
        if device.firmware_version is not None:
            update_data["firmware_version"] = device.firmware_version
        if device.description is not None:
            update_data["description"] = device.description
        if device.status is not None:
            update_data["status"] = True if device.status.lower() == "online" else False
            
        supabase.table("devices").update(update_data).eq("device_id", device_id).execute()
        return get_device(device_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: str):
    try:
        existing = supabase.table("devices").select("*").eq("device_id", device_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Device not found")
            
        update_data = {
            "status": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        supabase.table("devices").update(update_data).eq("device_id", device_id).execute()
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
