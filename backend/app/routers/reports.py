from fastapi import APIRouter
from app.services.d1_client import d1

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/summary")
async def get_report_summary(): return {}

@router.get("/smile-score-trend")
async def get_smile_trend(): return []

@router.get("/emotion-distribution")
async def get_emotion_dist(): return []

@router.get("/departments")
async def get_dept_analysis(): return []

@router.get("/factories")
async def get_fact_analysis(): return []

@router.get("/workers")
async def get_work_analysis(): return []

@router.get("/risk-analysis")
async def get_risk_analysis(): return []

@router.get("/logs")
async def get_report_logs(start_date: str = None, end_date: str = None):
    sql = """
    SELECT 
        s.employee_id as worker_id,
        e.employee_name as worker_name,
        e.department as department,
        f.feedback as mood,
        s.skin_temperature as temp,
        s.heart_rate as hr,
        s.spo2 as spo2,
        s.gsr as gsr,
        s.timestamp as recorded_at
    FROM sensor_readings s
    LEFT JOIN employees e ON s.employee_id = e.employee_id
    LEFT JOIN feedback_events f ON s.event_id = f.event_id
    """
    
    where_clauses = []
    params = []
    
    if start_date:
        where_clauses.append("s.timestamp >= ?")
        params.append(start_date)
    if end_date:
        where_clauses.append("s.timestamp <= ?")
        params.append(end_date)
        
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
        
    sql += " ORDER BY s.timestamp DESC LIMIT 100"
    
    res = await d1.execute(sql, params)
    return {"data": res, "total": len(res), "page": 1, "limit": 100}

@router.get("/workers/{worker_id}")
async def get_worker_report(worker_id: str): return {}
