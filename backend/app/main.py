from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import supabase

app = FastAPI(title="Smile Score API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
