from fastapi import APIRouter, HTTPException
from app.database import supabase
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview")
def get_overview():
    return {
        "active_workers": 2,
        "overall_smile_score": 4.2,
        "happy_percentage": 60,
        "ok_percentage": 30,
        "sad_percentage": 10,
        "production_risk": {"level": "LOW", "confidence": 0.9}
    }

@router.get("/smile-trend")
def get_smile_trend(period: str = "today"):
    import random
    data = []
    now = datetime.now()
    if period == "today":
        for i in range(24):
            time_val = (now.replace(hour=i, minute=0, second=0)).isoformat()
            data.append({"timestamp": time_val, "smile_score": round(random.uniform(3.5, 4.8), 1)})
    elif period == "week":
        for i in range(7):
            time_val = (now - timedelta(days=6-i)).isoformat()
            data.append({"timestamp": time_val, "smile_score": round(random.uniform(3.5, 4.8), 1)})
    
    return {"period": period, "data": data}

@router.get("/emotion-distribution")
def get_emotion_distribution():
    return {"happy": 60, "ok": 30, "sad": 10, "total": 100}

@router.get("/workers")
def get_workers():
    try:
        workers_res = supabase.table("workers").select("*").execute()
        workers = workers_res.data or []
        result = []
        for w in workers:
            result.append({
                "id": w.get("worker_id"),
                "worker_code": w.get("employee_id"),
                "name": w.get("name"),
                "department": w.get("department_id"),
                "status": "ACTIVE" if w.get("status") else "INACTIVE",
                "emotion": "happy",
                "smile_score": 4.5
            })
        return {"workers": result[:10]}
    except Exception:
        return {"workers": []}

@router.get("/alerts")
def get_alerts():
    try:
        res = supabase.table("alerts").select("*").order("created_at", desc=True).limit(10).execute()
        alerts = res.data or []
        result = []
        for a in alerts:
             result.append({
                 "id": a.get("alert_id"),
                 "type": a.get("alert_type"),
                 "severity": a.get("severity"),
                 "message": a.get("message"),
                 "timestamp": a.get("created_at")
             })
        return {"alerts": result}
    except Exception:
        return {"alerts": []}

@router.get("/production-risk")
def get_production_risk():
    return {"level": "LOW", "confidence": 0.9, "factors": ["Good worker morale", "Low defect rate"], "last_updated": datetime.now().isoformat()}

@router.get("/departments")
def get_departments():
    try:
        res = supabase.table("departments").select("*").execute()
        deps = res.data or []
        result = [{"id": d.get("department_id"), "name": d.get("department_name"), "smile_score": 4.2, "risk": "LOW"} for d in deps]
        return {"departments": result}
    except Exception:
        return {"departments": []}

@router.get("/devices")
def get_devices():
    try:
        res = supabase.table("devices").select("*").execute()
        devices = res.data or []
        return {"devices": devices}
    except Exception:
        return {"devices": []}

@router.get("/recent-activity")
def get_recent_activity():
    return {"activities": [
        {"timestamp": datetime.now().isoformat(), "worker": "John Doe", "event": "Clocked In", "device": "DEV001"},
        {"timestamp": (datetime.now() - timedelta(minutes=10)).isoformat(), "worker": "Jane Smith", "event": "Feedback submitted", "device": "DEV002"}
    ]}

@router.get("/button-feedback")
def get_button_feedback():
    return {"happy": 150, "ok": 45, "sad": 12, "total": 207}

@router.get("/ai-insights")
def get_ai_insights():
    return {"insights": [
        {"id": "1", "title": "Morale Improvement", "description": "Smile scores in Assembly are up 15% this week.", "type": "positive", "actionable": False},
        {"id": "2", "title": "Fatigue Warning", "description": "Late shift workers showing signs of fatigue.", "type": "warning", "actionable": True}
    ]}

@router.get("/shifts")
def get_shifts():
    return {"shifts": []}
