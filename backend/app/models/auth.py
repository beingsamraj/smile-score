from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    user_role: str
    factory_id: str | None
    status: bool
