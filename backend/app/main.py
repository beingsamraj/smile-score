import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import supabase
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Smile Score API")

import logging
from pythonjsonlogger import jsonlogger
import uuid

# Configure JSON Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# Clear existing handlers
if logger.hasHandlers():
    logger.handlers.clear()
    
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.info("Request started", extra={"request_id": request_id, "method": request.method, "url": str(request.url)})
    response = await call_next(request)
    logger.info("Request completed", extra={"request_id": request_id, "status_code": response.status_code})
    return response

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

from app.routers import dashboard, factories, users, devices, workers, departments, reports
app.include_router(dashboard.router)
app.include_router(factories.router)
app.include_router(users.router)
app.include_router(devices.router)
app.include_router(workers.router)
app.include_router(departments.dept_router)
app.include_router(reports.router)
from app.routers.d1_api import router as d1_router
app.include_router(d1_router)

# ─── WebSocket Connection Manager ──────────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._ping_tasks: dict = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Start heartbeat ping task
        task = asyncio.create_task(self.heartbeat(websocket))
        self._ping_tasks[websocket] = task

    async def heartbeat(self, websocket: WebSocket):
        try:
            while True:
                await asyncio.sleep(20)
                await websocket.send_json({"type": "ping", "timestamp": datetime.now(timezone.utc).isoformat()})
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.error(f"WebSocket heartbeat error: {e}")
            self.disconnect(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self._ping_tasks:
            self._ping_tasks[websocket].cancel()
            del self._ping_tasks[websocket]

    async def broadcast(self, message: dict):
        dead = []
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception as e:
                logging.error(f"Broadcast failed: {e}")
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = ConnectionManager()

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "pong":
                pass
    except (WebSocketDisconnect, asyncio.TimeoutError, Exception) as e:
        logging.error(f"WebSocket closed: {e}")
        manager.disconnect(websocket)

# Utility to broadcast emotion updates (call this from any POST emotion endpoint)
async def broadcast_emotion_update(emotion_data: dict):
    await manager.broadcast({
        "type": "emotion_update",
        "data": emotion_data,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


# ─── Worker Wellness Timeline ────────────────────────────────────────────────────
@app.get("/api/workers/{worker_id}/timeline")
def get_worker_timeline(worker_id: str, days: int = 7):
    try:
        # Verify worker exists
        w_res = supabase.table("workers").select("worker_id, name, employee_id, designation, department_id, factory_id, status").eq("worker_id", worker_id).execute()
        if not w_res.data:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Worker not found")
        worker = w_res.data[0]

        # Get emotion events for last N days
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        e_res = supabase.table("emotions").select("emotion_id, emotion, smile_score, created_at").eq("worker_id", worker_id).gte("created_at", since).order("created_at").execute()
        events = e_res.data or []

        # Group by day
        daily_buckets: dict = {}
        for e in events:
            ts = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
            day_key = ts.strftime("%Y-%m-%d")
            if day_key not in daily_buckets:
                daily_buckets[day_key] = {"happy": 0, "ok": 0, "sad": 0, "scores": []}
            
            emotion_val = e.get("emotion", "OK")
            # Handle legacy and new values robustly
            emotion_normalized = str(emotion_val).strip().upper()
            if emotion_normalized == "HAPPY":
                counter_key = "happy"
            elif emotion_normalized == "SAD":
                counter_key = "sad"
            else:
                counter_key = "ok"
                
            daily_buckets[day_key][counter_key] += 1
            if e.get("smile_score") is not None:
                daily_buckets[day_key]["scores"].append(float(e["smile_score"]))

        # Build daily summary list
        daily = []
        for day, data in sorted(daily_buckets.items()):
            scores = data.pop("scores")
            data["avg_smile_score"] = round(sum(scores) / len(scores), 1) if scores else 0
            data["date"] = day
            data["total"] = data["happy"] + data["ok"] + data["sad"]
            daily.append(data)

        # Overall stats
        total_events = len(events)
        all_scores = [float(e["smile_score"]) for e in events if e.get("smile_score") is not None]
        overall_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0

        return {
            "worker": worker,
            "period_days": days,
            "total_events": total_events,
            "overall_smile_score": overall_score,
            "daily": daily,
            "events": events[-20:]  # last 20 raw events for the event log
        }
    except Exception as e:
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))


from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from app.ai_models.anomaly_detector import anomaly_detector

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    # Initialize background jobs
    scheduler.add_job(run_anomaly_detection, 'interval', minutes=15, coalesce=True, max_instances=1)
    scheduler.start()
    logging.info("APScheduler started: running anomaly detection every 15 minutes.")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()\n    from app.services.d1_client import d1\n    await d1.close()

async def run_anomaly_detection():
    try:
        # Get emotions from the last 15 minutes
        since = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        res = supabase.table("emotions").select("emotion_id, worker_id, smile_score, created_at").gte("created_at", since).execute()
        recent_emotions = res.data or []
        
        for e in recent_emotions:
            if e.get("smile_score") is not None:
                # Basic hour of day
                hour = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).hour
                score = float(e["smile_score"])
                
                result = anomaly_detector.detect_anomaly(score, hour)
                
                if result["is_anomaly"] and result["severity"] in ["WARNING", "CRITICAL"]:
                    # Create an alert
                    new_alert = {
                        "severity": result["severity"].lower(),
                        "message": f"Anomalous emotion drop detected for worker {e['worker_id']}. Anomaly Score: {result['anomaly_score']}",
                        "worker_id": e["worker_id"],
                        "alert_type": "ANOMALY",
                        "status": "open"
                    }
                    supabase.table("alerts").insert(new_alert).execute()
                    
                    # Push via WebSocket
                    await manager.broadcast({
                        "type": "new_alert",
                        "data": new_alert
                    })
    except Exception as e:
        logging.error(f"Error in run_anomaly_detection: {e}")

from pydantic import BaseModel
from fastapi import HTTPException

from pydantic import BaseModel
from typing import Optional

class FeedbackRequest(BaseModel):
    emotion: str
    rfid_uid: Optional[str] = None
    worker_id: Optional[str] = None

from app.services.active_worker import active_worker_service, map_essl_to_worker

class ActiveWorkerTestRequest(BaseModel):
    worker_id: str
    essl_user_id: str

@app.get("/api/active-worker")
async def get_active_worker():
    state = await active_worker_service.get_active_worker()
    if state:
        return state
    return {"active": False, "worker_id": None}

@app.post("/api/test/active-worker")
async def test_set_active_worker(req: ActiveWorkerTestRequest):
    # This is ONLY for testing the ESP32 bridge
    await active_worker_service.set_active_worker(req.essl_user_id, req.worker_id)
    return {"status": "success", "message": f"Test active worker set to {req.worker_id}"}

from app.services.d1_client import d1
import uuid

# @app.post("/api/feedback")
async def submit_feedback(request: FeedbackRequest):
    try:
        emotion = request.emotion.strip().upper()
        if emotion not in ["HAPPY", "OK", "SAD"]:
            raise HTTPException(status_code=400, detail="Invalid emotion. Must be HAPPY, OK, or SAD.")
            
        if not request.rfid_uid and not request.worker_id:
            raise HTTPException(status_code=400, detail="Either rfid_uid or worker_id must be provided.")
            
        from fastapi.responses import JSONResponse
            
        # 1. Identity Verification (Cloudflare D1)
        if request.rfid_uid:
            normalized_rfid = request.rfid_uid.strip().upper()
            w_res = await d1.execute("SELECT worker_id, factory_id, department_id, employee_id, name, designation, status FROM workers WHERE rfid_uid = ?", [normalized_rfid])
            if not w_res:
                return JSONResponse(status_code=404, content={"success": False, "message": "RFID card not registered"})
        else:
            w_res = await d1.execute("SELECT worker_id, factory_id, department_id, employee_id, name, designation, status FROM workers WHERE worker_id = ?", [request.worker_id])
            if not w_res:
                return JSONResponse(status_code=404, content={"success": False, "message": "Worker not found"})

        worker_data = w_res[0]
        
        # 2. Check Active Status
        if worker_data.get("status") in (0, False, "false", "0"):
            return JSONResponse(status_code=403, content={"success": False, "message": "Worker is inactive"})
            
        # Calculate score
        score_map = {"HAPPY": 1.00, "OK": 0.50, "SAD": 0.00}
        smile_score = score_map[emotion]
        
        # 3. Insert into DB (Cloudflare D1)
        emotion_id = str(uuid.uuid4())
        
        insert_sql = """
        INSERT INTO emotions (emotion_id, worker_id, department_id, factory_id, emotion, smile_score)
        VALUES (?, ?, ?, ?, ?, ?)
        RETURNING *
        """
        
        e_res = await d1.execute(insert_sql, [
            emotion_id,
            worker_data["worker_id"],
            worker_data.get("department_id"),
            worker_data.get("factory_id"),
            emotion,
            smile_score
        ])
        
        if not e_res:
            raise HTTPException(status_code=500, detail="Failed to insert feedback into database")
            
        inserted_record = e_res[0]
        
        # Broadcast via WebSocket
        await broadcast_emotion_update(inserted_record)
        
        # CLEAR the active worker after successful feedback (legacy workflow cleanup)
        current_state = await active_worker_service.get_active_worker()
        if current_state and current_state["worker_id"] == worker_data["worker_id"]:
            await active_worker_service.clear_active_worker()
            
        return {
            "success": True,
            "message": "Feedback recorded successfully",
            "data": {
                "worker_id": worker_data["worker_id"],
                "employee_id": worker_data.get("employee_id"),
                "name": worker_data.get("name"),
                "emotion": emotion,
                "smile_score": smile_score,
                "department_id": worker_data.get("department_id"),
                "factory_id": worker_data.get("factory_id")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Unhandled exception:")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/openapi")
def get_openapi_spec():
    return app.openapi()

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
@limiter.limit("10/minute")
def login(req: LoginRequest, request: Request):
    try:
        # Query the custom users table for the provided username
        response = supabase.table("users").select("*").eq("username", req.username).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
            
        user = response.data[0]
        
        # Check user_pin
        import bcrypt
        import jwt
        from datetime import datetime, timedelta, timezone
        
        stored_pin = str(user.get("user_pin"))
        is_valid = False
        try:
            if stored_pin.startswith("$2b$") or stored_pin.startswith("$2a$"):
                is_valid = bcrypt.checkpw(req.password.encode('utf-8'), stored_pin.encode('utf-8'))
            else:
                is_valid = (stored_pin == req.password)
        except Exception:
            pass
            
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
            
        token = jwt.encode(
            {"sub": str(user.get("user_id")), "role": user.get("user_role"), "exp": datetime.now(timezone.utc) + timedelta(hours=24)},
            "SMILE_SCORE_SECRET_JWT_KEY_SUPER_SECURE",
            algorithm="HS256"
        )
            
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
                "token": token,
                "factory_id": user.get("factory_id")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Unhandled exception:")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
