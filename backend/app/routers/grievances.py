from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from app.services.d1_client import d1
import uuid
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/grievances", tags=["Grievances"])

class NoteCreate(BaseModel):
    note: str
    added_by: str

class StatusUpdate(BaseModel):
    status: str
    changed_by: str

@router.get("/metrics")
async def get_metrics():
    # Count SAD events directly from feedback_events
    res = await d1.execute("SELECT COUNT(*) as c FROM feedback_events WHERE feedback = 'SAD'")
    total_sad = res[0]['c'] if res else 0
    
    # In this dynamic mode, all are effectively 'NEW'.
    metrics = {"TOTAL": total_sad, "NEW": total_sad, "UNDER REVIEW": 0, "RESOLVED": 0}
    return {"data": metrics}

@router.get("/detect")
async def detect_grievances():
    # No longer needed since we fetch dynamically!
    return {"message": "Dynamic mode enabled. No cron needed.", "new_grievances": []}

@router.get("")
async def get_grievances(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    date_filter: Optional[str] = Query("all"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    offset = (page - 1) * limit
    where_clauses = ["f.feedback = 'SAD'"]
    params = []
    
    if department and department.upper() != "ALL":
        where_clauses.append("e.department = ?")
        params.append(department)
        
    if date_filter and date_filter.lower() != 'all':
        where_clauses.append("f.timestamp LIKE ?")
        params.append(f"{date_filter}%")
        
    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    count_sql = f"""
        SELECT COUNT(DISTINCT f.employee_id) as c 
        FROM feedback_events f 
        JOIN employees e ON f.employee_id = e.employee_id 
        {where_sql}
    """
    count_res = await d1.execute(count_sql, params)
    total = count_res[0]['c'] if count_res else 0
    
    # Group by employee to show SAD *people*, using the most recent SAD event as the grievance_id
    sql = f"""
        SELECT 
            MAX(f.event_id) as grievance_id, 
            f.employee_id, 
            'NEW' as grievance_status, 
            'Direct SAD Feedback' as trigger_reason, 
            MAX(f.timestamp) as detected_at,
            e.employee_name, 
            e.department, 
            e.workstation,
            'SAD' as latest_feedback,
            COUNT(f.event_id) as total_sad_count,
            MAX(f.timestamp) as last_sad_time,
            (SELECT risk_level FROM ml_predictions m WHERE m.employee_id = f.employee_id ORDER BY created_at DESC LIMIT 1) as risk_level,
            (SELECT risk_score FROM ml_predictions m WHERE m.employee_id = f.employee_id ORDER BY created_at DESC LIMIT 1) as risk_score
        FROM feedback_events f
        JOIN employees e ON f.employee_id = e.employee_id
        {where_sql}
        GROUP BY f.employee_id
        ORDER BY MAX(f.timestamp) DESC
        LIMIT ? OFFSET ?
    """
    
    res = await d1.execute(sql, params + [limit, offset])
    return {"data": res, "total": total, "page": page, "limit": limit}

@router.get("/{grievance_id}")
async def get_grievance(grievance_id: str):
    res = await d1.execute("""
        SELECT f.event_id as grievance_id, f.employee_id, 'NEW' as status, 'Direct SAD Feedback' as trigger_reason, f.timestamp as detected_at, e.employee_name, e.department, e.workstation
        FROM feedback_events f
        JOIN employees e ON f.employee_id = e.employee_id
        WHERE f.event_id = ?
    """, [grievance_id])
    
    if not res:
        raise HTTPException(status_code=404, detail="SAD event not found")
        
    grievance = res[0]
    
    notes = await d1.execute("SELECT * FROM grievance_notes WHERE grievance_id = ? ORDER BY created_at DESC", [grievance_id])
    history = []
    
    feedbacks = await d1.execute("SELECT feedback, timestamp FROM feedback_events WHERE employee_id = ? ORDER BY timestamp DESC LIMIT 20", [grievance['employee_id']])
    
    return {
        "data": {
            "grievance": grievance,
            "notes": notes,
            "history": history,
            "recent_feedbacks": feedbacks
        }
    }

@router.put("/{grievance_id}/status")
async def update_status(grievance_id: str, data: StatusUpdate):
    return {"success": True, "new_status": data.status.upper()}

@router.post("/{grievance_id}/notes")
async def add_note(grievance_id: str, data: NoteCreate):
    await d1.execute(
        "INSERT INTO grievance_notes (grievance_id, note, added_by) VALUES (?, ?, ?)",
        [grievance_id, data.note, data.added_by]
    )
    return {"success": True}
