from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FactoryBase(BaseModel):
    factory_name: str = Field(..., min_length=1, max_length=150)
    factory_address: Optional[str] = Field(None, max_length=255)
    no_of_employees: Optional[int] = Field(0)
    status: bool = Field(True)

class FactoryCreate(FactoryBase):
    pass

class FactoryUpdate(BaseModel):
    factory_name: Optional[str] = Field(None, min_length=1, max_length=150)
    factory_address: Optional[str] = Field(None, max_length=255)
    no_of_employees: Optional[int] = Field(None)
    status: Optional[bool] = Field(None)

class FactoryResponse(FactoryBase):
    factory_id: str
    created_at: datetime
