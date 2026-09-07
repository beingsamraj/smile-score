from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: str = Field(default="worker", description="Must be one of: worker, supervisor, manager, admin")
    factory_id: Optional[str] = None
    rfid_uid: Optional[str] = None
    status: str = Field(default="active", description="Must be active or inactive")

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    factory_id: Optional[str] = None
    rfid_uid: Optional[str] = None
    status: Optional[str] = None

class UserResponse(BaseModel):
    id: str  # maps to user_id
    auth_user_id: Optional[str] = None
    employee_code: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str  # maps to user_role
    factory_id: Optional[str] = None
    factory_name: Optional[str] = None
    rfid_uid: Optional[str] = None
    status: str  # mapping True to 'active', False to 'inactive'
    created_at: datetime
    updated_at: datetime

class UserListResponse(BaseModel):
    data: list[UserResponse]
    total: int
    page: int
    limit: int
