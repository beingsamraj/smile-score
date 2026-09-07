from fastapi import APIRouter, HTTPException
from app.database import supabase
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/overview")
def get_overview():
    try:
        # Active workers
        try:
            workers_res = supabase.table("workers").select("id", count="exact").eq("status", "ACTIVE").execute()
            active_workers = workers_res.count if workers_res.count is not None else 0
        except Exception:
            active_workers = 0

        # Emotions
        try:
            emotions_res = supabase.table("emotions").select("emotion, smile_score").execute()
            emotions = emotions_res.data or []
        except Exception:
            emotions = []
        
        total_emotions = len(emotions)
        if total_emotions > 0:
            happy_count = sum(1 for e in emotions if e.get("emotion") == "happy")
            ok_count = sum(1 for e in emotions if e.get("emotion") == "ok")
            sad_count = sum(1 for e in emotions if e.get("emotion") == "sad")
            
            happy_percentage = round((happy_count / total_emotions) * 100)
            ok_percentage = round((ok_count / total_emotions) * 100)
            sad_percentage = round((sad_count / total_emotions) * 100)
            
            scores = [e.get("smile_score") for e in emotions if e.get("smile_score") is not None]
            overall_smile_score = round(sum(scores) / len(scores), 1) if scores else 0
        else:
            happy_percentage = 0
            ok_percentage = 0
            sad_percentage = 0
            overall_smile_score = 0
            
        # Production risk
        try:
            risk_res = supabase.table("production_risk").select("*").order("timestamp", desc=True).limit(1).execute()
            if risk_res.data and len(risk_res.data) > 0:
                latest_risk = risk_res.data[0]
                risk = {
                    "level": latest_risk.get("risk_level", "NO_DATA"),
                    "confidence": latest_risk.get("confidence")
                }
            else:
                risk = {"level": "NO_DATA", "confidence": None}
        except Exception:
            risk = {"level": "NO_DATA", "confidence": None}
            
        return {
            "active_workers": active_workers,
            "overall_smile_score": overall_smile_score,
            "happy_percentage": happy_percentage,
            "ok_percentage": ok_percentage,
            "sad_percentage": sad_percentage,
            "production_risk": risk
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/smile-trend")
def get_smile_trend(period: str = "today"):
    try:
        res = supabase.table("emotions").select("timestamp, smile_score").order("timestamp", desc=False).execute()
        data = res.data or []
        trend = [{"timestamp": item.get("timestamp"), "smile_score": item.get("smile_score")} for item in data if item.get("smile_score") is not None]
        return {"period": period, "data": trend}
    except Exception:
        return {"period": period, "data": []}

@router.get("/emotion-distribution")
def get_emotion_distribution():
    try:
        res = supabase.table("emotions").select("emotion").execute()
        emotions = res.data or []
        happy = sum(1 for e in emotions if e.get("emotion") == "happy")
        ok = sum(1 for e in emotions if e.get("emotion") == "ok")
        sad = sum(1 for e in emotions if e.get("emotion") == "sad")
        return {"happy": happy, "ok": ok, "sad": sad, "total": len(emotions)}
    except Exception:
        return {"happy": 0, "ok": 0, "sad": 0, "total": 0}

@router.get("/workers")
def get_workers():
    try:
        workers_res = supabase.table("workers").select("*, departments(name)").execute()
        workers = workers_res.data or []
        result = []
        for w in workers:
            department_name = w.get("departments", {}).get("name") if w.get("departments") else "Unknown"
            result.append({
                "id": w.get("id"),
                "worker_code": w.get("worker_code"),
                "name": w.get("name"),
                "department": department_name,
                "status": w.get("status"),
                "emotion": "Unknown",
                "smile_score": 0
            })
        return {"workers": result}
    except Exception:
        return {"workers": []}

@router.get("/alerts")
def get_alerts():
    try:
        res = supabase.table("alerts").select("*").order("timestamp", desc=True).limit(10).execute()
        return {"alerts": res.data or []}
    except Exception:
        return {"alerts": []}

@router.get("/production-risk")
def get_production_risk():
    try:
        res = supabase.table("production_risk").select("*").order("timestamp", desc=True).limit(1).execute()
        if res.data and len(res.data) > 0:
            latest = res.data[0]
            return {
                "level": latest.get("risk_level"),
                "confidence": latest.get("confidence"),
                "factors": [],
                "last_updated": latest.get("timestamp")
            }
        return {"level": "NO_DATA", "confidence": None, "factors": []}
    except Exception:
        return {"level": "NO_DATA", "confidence": None, "factors": []}

@router.get("/departments")
def get_departments():
    try:
        res = supabase.table("departments").select("*").execute()
        deps = res.data or []
        result = [{"id": d.get("id"), "name": d.get("name"), "smile_score": 0, "risk": "NO_DATA"} for d in deps]
        return {"departments": result}
    except Exception:
        return {"departments": []}

@router.get("/devices")
def get_devices():
    try:
        res = supabase.table("devices").select("*").execute()
        return {"devices": res.data or []}
    except Exception:
        return {"devices": []}

@router.get("/recent-activity")
def get_recent_activity():
    try:
        res = supabase.table("emotions").select("*, workers(name), devices(device_code)").order("timestamp", desc=True).limit(10).execute()
        activities = []
        for e in (res.data or []):
            worker_name = e.get("workers", {}).get("name") if e.get("workers") else "Unknown Worker"
            device_code = e.get("devices", {}).get("device_code") if e.get("devices") else "Unknown Device"
            activities.append({
                "timestamp": e.get("timestamp"),
                "worker": worker_name,
                "event": e.get("emotion"),
                "device": device_code
            })
        return {"activities": activities}
    except Exception:
        return {"activities": []}

@router.get("/button-feedback")
def get_button_feedback():
    try:
        res = supabase.table("emotions").select("emotion").eq("source", "button").execute()
        emotions = res.data or []
        happy = sum(1 for e in emotions if e.get("emotion") == "happy")
        ok = sum(1 for e in emotions if e.get("emotion") == "ok")
        sad = sum(1 for e in emotions if e.get("emotion") == "sad")
        return {"happy": happy, "ok": ok, "sad": sad, "total": len(emotions)}
    except Exception:
        return {"happy": 0, "ok": 0, "sad": 0, "total": 0}

@router.get("/ai-insights")
def get_ai_insights():
    return {"insights": []}

@router.get("/shifts")
def get_shifts():
    try:
        res = supabase.table("shifts").select("*").execute()
        return {"shifts": res.data or []}
    except Exception:
        return {"shifts": []}
