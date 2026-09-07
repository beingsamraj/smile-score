from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WorkerCreate(BaseModel):
    name: str
    factory_id: str
    department_id: str
    rfid_uid: str
    designation: Optional[str] = None
    status: Optional[bool] = True

class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    factory_id: Optional[str] = None
    department_id: Optional[str] = None
    rfid_uid: Optional[str] = None
    designation: Optional[str] = None
    status: Optional[bool] = None

class WorkerResponse(BaseModel):
    worker_id: str
    employee_id: str
    name: str
    factory_id: str
    factory_name: Optional[str] = None
    department_id: str
    department_name: Optional[str] = None
    rfid_uid: str
    designation: Optional[str] = None
    status: bool
    created_at: datetime

class WorkerListResponse(BaseModel):
    data: list[WorkerResponse]
    total: int
    page: int
    limit: int
