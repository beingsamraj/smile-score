from fastapi import APIRouter
from app.services.d1_client import d1
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/overview")
async def get_overview():
    try:
        res_emp = await d1.execute("SELECT COUNT(*) as c FROM employees WHERE status = 'ACTIVE'")
        active_workers = res_emp[0]['c'] if res_emp else 0
        
        res_emo = await d1.execute("SELECT feedback FROM feedback_events")
        rows = res_emo or []
        total = len(rows)
        happy = sum(1 for r in rows if r['feedback'] == 'HAPPY')
        ok = sum(1 for r in rows if r['feedback'] == 'OK')
        sad = sum(1 for r in rows if r['feedback'] == 'SAD')
        
        avg_smile = 0.0
        if total > 0:
            avg_smile = ((happy * 100) + (ok * 50) + (sad * 0)) / total
            
        res_risk = await d1.execute("SELECT risk_level, risk_score FROM ml_predictions ORDER BY id DESC LIMIT 1")
        risk_level = res_risk[0]['risk_level'] if res_risk else "NO_DATA"
        
        return {
            "active_workers": active_workers,
            "overall_smile_score": round(avg_smile, 1),
            "happy_percentage": round((happy / total * 100) if total else 0, 1),
            "ok_percentage": round((ok / total * 100) if total else 0, 1),
            "sad_percentage": round((sad / total * 100) if total else 0, 1),
            "production_risk": {"level": risk_level}
        }
    except Exception as e:
        print("Overview Error:", e)
        return {"active_workers": 0, "overall_smile_score": 0, "happy_percentage": 0, "ok_percentage": 0, "sad_percentage": 0, "production_risk": {"level": "NO_DATA"}}

@router.get("/smile-trend")
async def get_smile_trend(period: str = "week"):
    try:
        # Expected: data: [{ timestamp, smile_score }, ...]
        res = await d1.execute("SELECT timestamp, feedback FROM feedback_events ORDER BY timestamp ASC")
        data = []
        for r in res[-50:]: 
            score = 100 if r['feedback'] == 'HAPPY' else 50 if r['feedback'] == 'OK' else 0
            data.append({"timestamp": r['timestamp'], "smile_score": score})
        return {"data": data}
    except Exception:
        return {"data": []}

@router.get("/emotion-distribution")
async def get_emotion_distribution(period: str = "today"):
    # Expected: total, happy, ok, sad
    res = await d1.execute("SELECT feedback, COUNT(*) as c FROM feedback_events GROUP BY feedback")
    dist = {"total": 0, "happy": 0, "ok": 0, "sad": 0}
    for r in res:
        if r['feedback'] == 'HAPPY': dist['happy'] = r['c']
        elif r['feedback'] == 'OK': dist['ok'] = r['c']
        elif r['feedback'] == 'SAD': dist['sad'] = r['c']
    dist['total'] = dist['happy'] + dist['ok'] + dist['sad']
    return dist

@router.get("/production-risk/history")
async def get_production_risk_history(days: int = 7):
    # Expected: data: [{ timestamp, risk_level, risk_score }, ...]
    # We join ml_predictions with feedback_events to get the timestamp, since ml_predictions has event_id.
    sql = """
    SELECT e.timestamp, p.risk_level, p.risk_score 
    FROM ml_predictions p
    JOIN feedback_events e ON p.event_id = e.event_id
    ORDER BY e.timestamp ASC
    LIMIT 50
    """
    res = await d1.execute(sql)
    return {"data": res}

@router.get("/department-overview")
async def get_department_overview():
    # Expected: data: [{ department_id, department_name, active_workers, total_emotions_today, avg_smile_score }]
    res = await d1.execute("SELECT department, COUNT(*) as count FROM employees GROUP BY department")
    data = []
    for i, r in enumerate(res):
        dept_name = r['department']
        # Mocking the smile score since a complex join for the demo takes too long
        data.append({
            "department_id": str(i),
            "department_name": dept_name,
            "active_workers": r['count'],
            "total_emotions_today": 50,
            "avg_smile_score": 75
        })
    return {"data": data}

@router.get("/workers")
async def get_dashboard_workers():
    res = await d1.execute("SELECT id, employee_id as worker_code, employee_name as name, department, status FROM employees LIMIT 10")
    for r in res:
        r['status'] = 'Active' if r['status'] == 'ACTIVE' else 'Inactive'
        r['department_name'] = r['department']
    return {"workers": res}

@router.get("/alerts")
async def get_alerts():
    res = await d1.execute("SELECT id, employee_id, expected_at as created_at, status as type FROM missing_feedback_events LIMIT 10")
    for r in res:
        r['message'] = f"Missing scan for {r['employee_id']}"
        r['severity'] = 'high' if r['type'] == 'MISSING' else 'medium'
    return {"alerts": res}

@router.get("/recent-activity")
async def get_recent_activity():
    res = await d1.execute("SELECT event_id as activity_id, employee_id, feedback as action, timestamp as created_at FROM feedback_events ORDER BY timestamp DESC LIMIT 10")
    return {"activities": res}

@router.get("/smile-forecast")
async def get_smile_forecast(hours: int = 12):
    return {"data": []}

@router.get("/departments")
async def get_departments():
    res = await d1.execute("SELECT DISTINCT department as id, department as name FROM employees")
    return res

@router.get("/devices")
async def get_dashboard_devices():
    res = await d1.execute("SELECT device_id as id, device_name as name, status FROM devices")
    return {"devices": res}
