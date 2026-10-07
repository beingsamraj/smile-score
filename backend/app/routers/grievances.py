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
    res = await d1.execute("SELECT status, COUNT(*) as c FROM grievances GROUP BY status")
    metrics = {"TOTAL": 0, "NEW": 0, "UNDER REVIEW": 0, "RESOLVED": 0}
    for r in res:
        st = r['status'].upper()
        metrics[st] = r['c']
        metrics["TOTAL"] += r['c']
        
    return {"data": metrics}

@router.get("/detect")
async def detect_grievances():
    # Helper to scan for repeated SADs and open new grievances.
    # 1. Find all employees who don't have an active (NEW/UNDER REVIEW) grievance
    # 2. Check their last 7 days of feedback
    
    now = datetime.now(timezone.utc)
    week_ago = (now - timedelta(days=7)).isoformat()
    
    # Employees with active grievances
    active_res = await d1.execute("SELECT employee_id FROM grievances WHERE status IN ('NEW', 'UNDER REVIEW')")
    active_ids = {r['employee_id'] for r in active_res}
    
    # Get recent feedback
    recent_feedbacks = await d1.execute("SELECT employee_id, feedback, timestamp FROM feedback_events WHERE timestamp >= ? ORDER BY timestamp ASC", [week_ago])
    
    employee_history = {}
    for f in recent_feedbacks:
        eid = f['employee_id']
        if eid in active_ids:
            continue
        if eid not in employee_history:
            employee_history[eid] = []
        employee_history[eid].append(f['feedback'])
        
    new_grievances = []
    
    for eid, feedbacks in employee_history.items():
        sad_count = sum(1 for fb in feedbacks if fb.upper() == 'SAD')
        
        # Check consecutive SADs
        consecutive_sad = 0
        max_consecutive = 0
        for fb in feedbacks:
            if fb.upper() == 'SAD':
                consecutive_sad += 1
                max_consecutive = max(max_consecutive, consecutive_sad)
            else:
                consecutive_sad = 0
                
        reason = None
        if max_consecutive >= 2:
            reason = f"Detected {max_consecutive} consecutive SAD feedbacks."
        elif sad_count >= 3:
            reason = f"Detected {sad_count} SAD feedbacks in the last 7 days."
            
        if reason:
            gid = f"GRV-{str(uuid.uuid4())[:8].upper()}"
            await d1.execute(
                "INSERT INTO grievances (grievance_id, employee_id, status, trigger_reason, detected_at) VALUES (?, ?, 'NEW', ?, ?)",
                [gid, eid, reason, now.isoformat()]
            )
            new_grievances.append(gid)
            
    return {"message": f"Detected {len(new_grievances)} new grievances", "new_grievances": new_grievances}

@router.get("")
async def get_grievances(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    date_filter: Optional[str] = Query("all"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    offset = (page - 1) * limit
    where_clauses = []
    params = []
    
    if status and status.upper() != "ALL":
        where_clauses.append("g.status = ?")
        params.append(status.upper())
    if department and department.upper() != "ALL":
        where_clauses.append("e.department = ?")
        params.append(department)
        
    if date_filter and date_filter.lower() != 'all':
        # If user picks a date like '2026-10-07', we match dates starting with that
        where_clauses.append("g.detected_at LIKE ?")
        params.append(f"{date_filter}%")

        
    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    
    count_sql = f"""
        SELECT COUNT(*) as c 
        FROM grievances g 
        JOIN employees e ON g.employee_id = e.employee_id 
        {where_sql}
    """
    count_res = await d1.execute(count_sql, params)
    total = count_res[0]['c'] if count_res else 0
    
    sql = f"""
        SELECT 
            g.grievance_id, g.employee_id, g.status as grievance_status, g.trigger_reason, g.detected_at,
            e.employee_name, e.department, e.workstation,
            (SELECT feedback FROM feedback_events f WHERE f.employee_id = g.employee_id ORDER BY timestamp DESC LIMIT 1) as latest_feedback,
            (SELECT COUNT(*) FROM feedback_events f WHERE f.employee_id = g.employee_id AND f.feedback = 'SAD') as total_sad_count,
            (SELECT timestamp FROM feedback_events f WHERE f.employee_id = g.employee_id AND f.feedback = 'SAD' ORDER BY timestamp DESC LIMIT 1) as last_sad_time,
            (SELECT risk_level FROM ml_predictions m WHERE m.employee_id = g.employee_id ORDER BY created_at DESC LIMIT 1) as risk_level,
            (SELECT risk_score FROM ml_predictions m WHERE m.employee_id = g.employee_id ORDER BY created_at DESC LIMIT 1) as risk_score
        FROM grievances g
        JOIN employees e ON g.employee_id = e.employee_id
        {where_sql}
        ORDER BY g.detected_at DESC
        LIMIT ? OFFSET ?
    """
    
    res = await d1.execute(sql, params + [limit, offset])
    return {"data": res, "total": total, "page": page, "limit": limit}

@router.get("/{grievance_id}")
async def get_grievance(grievance_id: str):
    res = await d1.execute("""
        SELECT g.*, e.employee_name, e.department, e.workstation
        FROM grievances g
        JOIN employees e ON g.employee_id = e.employee_id
        WHERE g.grievance_id = ?
    """, [grievance_id])
    
    if not res:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    grievance = res[0]
    
    notes = await d1.execute("SELECT * FROM grievance_notes WHERE grievance_id = ? ORDER BY created_at DESC", [grievance_id])
    history = await d1.execute("SELECT * FROM grievance_history WHERE grievance_id = ? ORDER BY created_at DESC", [grievance_id])
    
    # recent feedbacks
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
    curr = await d1.execute("SELECT status FROM grievances WHERE grievance_id = ?", [grievance_id])
    if not curr:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    old_status = curr[0]['status']
    new_status = data.status.upper()
    
    if old_status == new_status:
        return {"success": True}
        
    resolved_at = datetime.now(timezone.utc).isoformat() if new_status == 'RESOLVED' else None
    
    if resolved_at:
        await d1.execute("UPDATE grievances SET status = ?, resolved_at = ? WHERE grievance_id = ?", [new_status, resolved_at, grievance_id])
    else:
        await d1.execute("UPDATE grievances SET status = ? WHERE grievance_id = ?", [new_status, grievance_id])
        
    await d1.execute(
        "INSERT INTO grievance_history (grievance_id, old_status, new_status, changed_by) VALUES (?, ?, ?, ?)",
        [grievance_id, old_status, new_status, data.changed_by]
    )
    return {"success": True, "new_status": new_status}

@router.post("/{grievance_id}/notes")
async def add_note(grievance_id: str, data: NoteCreate):
    curr = await d1.execute("SELECT status FROM grievances WHERE grievance_id = ?", [grievance_id])
    if not curr:
        raise HTTPException(status_code=404, detail="Grievance not found")
        
    await d1.execute(
        "INSERT INTO grievance_notes (grievance_id, note, added_by) VALUES (?, ?, ?)",
        [grievance_id, data.note, data.added_by]
    )
    return {"success": True}

