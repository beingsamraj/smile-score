import nest_asyncio
wait_dummy = nest_asyncio.apply()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import supabase

app = FastAPI(title="Smile Score API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import dashboard, factories, users, devices, workers, departments, reports
app.include_router(dashboard.router)
app.include_router(factories.router)
app.include_router(users.router)
app.include_router(devices.router)
app.include_router(workers.router)
app.include_router(departments.dept_router)
app.include_router(reports.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "smile-score-backend"
    }

@app.get("/api/test/supabase")
def test_supabase():
    try:
        # Simple test to fetch factories (even if empty, it tests connection)
        response = supabase.table("factories").select("*").limit(1).execute()
        return {
            "status": "success",
            "message": "FastAPI connected to Supabase"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Configured but table unavailable or connection failed"
        }

from pydantic import BaseModel
from fastapi import HTTPException, status

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
def login(req: LoginRequest):
    try:
        # Query the custom users table for the provided username
        response = supabase.table("users").select("*").eq("username", req.username).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
            
        user = response.data[0]
        
        # Check user_pin
        if user.get("user_pin") != req.password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
            
        # Check if active
        if user.get("status") is False:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is disabled")

        # Check role access
        role = user.get("user_role", "").lower()
        if role not in ["admin", "superadmin", "super_admin"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ACCESS_DENIED")
            
        return {
            "status": "success",
            "user": {
                "user_id": user.get("user_id"),
                "username": user.get("username"),
                "user_role": user.get("user_role"),
                "factory_id": user.get("factory_id")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
