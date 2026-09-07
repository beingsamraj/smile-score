from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DeviceCreate(BaseModel):
    device_name: str
    device_type: str = Field(default="esp32", description="Must be one of: esp32, rfid_reader, button_panel, camera, gateway, other")
    factory_id: Optional[str] = None
    mac_address: Optional[str] = None
    location: Optional[str] = None
    firmware_version: Optional[str] = None
    description: Optional[str] = None
    status: str = Field(default="inactive", description="Must be one of: online, offline, inactive, maintenance")

class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    device_type: Optional[str] = None
    factory_id: Optional[str] = None
    mac_address: Optional[str] = None
    location: Optional[str] = None
    firmware_version: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class DeviceResponse(BaseModel):
    id: str  # maps to device_id (and device_code)
    device_code: str # maps to device_id
    device_name: str
    device_type: str
    factory_id: Optional[str] = None
    factory_name: Optional[str] = None
    mac_address: Optional[str] = None
    location: Optional[str] = None
    firmware_version: Optional[str] = None
    description: Optional[str] = None
    status: str  # mapped from True->online, False->inactive
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class DeviceListResponse(BaseModel):
    data: list[DeviceResponse]
    total: int
    page: int
    limit: int
