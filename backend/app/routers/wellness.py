from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Optional, List
from pydantic import BaseModel
from app.services.d1_client import d1
import io
import csv
from datetime import datetime, timezone

router = APIRouter(prefix="/api/wellness", tags=["Wellness"])

class NoteCreate(BaseModel):
    note: str
    added_by: str

class StatusUpdate(BaseModel):
    status: str
    changed_by: str

def get_wellness_sql(where_clauses, order_sql):
    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    # A worker is flagged for wellness if they have an anomaly in predictions OR their raw vitals cross thresholds
    # We will just fetch employees who have anomalous readings (either flagged by AI or medical thresholds)
    return f"""
        WITH anomalous_vitals AS (
            SELECT 
                s.employee_id,
                COUNT(s.id) as total_alerts,
                AVG(s.heart_rate) as avg_hr,
                AVG(s.spo2) as avg_spo2,
                AVG(s.skin_temperature) as avg_temp,
                MAX(s.timestamp) as latest_alert_time
            FROM sensor_readings s
            WHERE s.heart_rate > 100 OR s.heart_rate < 60 OR s.spo2 < 95 OR s.skin_temperature > 37.5
               OR s.event_id IN (SELECT event_id FROM ml_predictions WHERE prediction = 1)
            GROUP BY s.employee_id
        )
        SELECT 
            v.employee_id,
            COALESCE(ws.status, 'NEW') as status,
            v.total_alerts,
            v.avg_hr,
            v.avg_spo2,
            v.avg_temp,
            v.latest_alert_time as detected_at,
            e.employee_name,
            e.department,
            e.workstation,
            (SELECT risk_level FROM ml_predictions m WHERE m.employee_id = v.employee_id ORDER BY created_at DESC LIMIT 1) as risk_level
        FROM anomalous_vitals v
        JOIN employees e ON v.employee_id = e.employee_id
        LEFT JOIN wellness_status ws ON v.employee_id = ws.employee_id
        {where_sql}
        {order_sql}
    """

@router.get("/metrics")
async def get_metrics():
    # Simple metrics
    res = await d1.execute("""
        SELECT COUNT(DISTINCT s.employee_id) as total
        FROM sensor_readings s
        WHERE s.heart_rate > 100 OR s.heart_rate < 60 OR s.spo2 < 95 OR s.skin_temperature > 37.5
           OR s.event_id IN (SELECT event_id FROM ml_predictions WHERE prediction = 1)
    """)
    total = res[0]['total'] if res else 0
    return {"data": {"TOTAL": total, "NURSE_REFERRED": 0}}

@router.get("")
async def get_wellness(
    status: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    date_filter: Optional[str] = Query("all"),
    sort_by: Optional[str] = Query("detected_desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    offset = (page - 1) * limit
    where_clauses = []
    params = []
    
    if department and department.upper() != "ALL":
        where_clauses.append("e.department = ?")
        params.append(department)
    if status and status.upper() != "ALL":
        where_clauses.append("COALESCE(ws.status, 'NEW') = ?")
        params.append(status.upper())
    if date_filter and date_filter.lower() != 'all':
        where_clauses.append("v.latest_alert_time LIKE ?")
        params.append(f"{date_filter}%")
        
    order_sql = "ORDER BY v.latest_alert_time DESC"
    if sort_by == 'detected_asc': order_sql = "ORDER BY v.latest_alert_time ASC"
    elif sort_by == 'hr_desc': order_sql = "ORDER BY v.avg_hr DESC"
    elif sort_by == 'spo2_asc': order_sql = "ORDER BY v.avg_spo2 ASC"
    
    base_sql = get_wellness_sql(where_clauses, order_sql)
    
    # Count total
    count_sql = f"SELECT COUNT(*) as c FROM ({base_sql})"
    count_res = await d1.execute(count_sql, params)
    total = count_res[0]['c'] if count_res else 0
    
    # Paginated
    sql = base_sql + " LIMIT ? OFFSET ?"
    res = await d1.execute(sql, params + [limit, offset])
    
    return {"data": res, "total": total, "page": page, "limit": limit}

@router.get("/export")
async def export_report():
    sql = get_wellness_sql([], "ORDER BY v.latest_alert_time DESC")
    res = await d1.execute(sql)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Employee ID', 'Name', 'Department', 'Workstation', 'Status', 'Total Alerts', 'Avg HR', 'Avg SpO2', 'Avg Temp', 'Detected At', 'Risk Level'])
    
    for row in res:
        writer.writerow([
            row['employee_id'], row['employee_name'], row['department'], row['workstation'], 
            row['status'], row['total_alerts'], round(row['avg_hr'], 1), round(row['avg_spo2'], 1), 
            round(row['avg_temp'], 1), row['detected_at'], row['risk_level']
        ])
        
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]), 
        media_type="text/csv", 
        headers={"Content-Disposition": "attachment; filename=wellness_report.csv"}
    )

@router.get("/{employee_id}")
async def get_wellness_detail(employee_id: str):
    sql = get_wellness_sql(["v.employee_id = ?"], "")
    res = await d1.execute(sql, [employee_id])
    if not res:
        raise HTTPException(status_code=404, detail="Wellness record not found")
        
    record = res[0]
    notes = await d1.execute("SELECT * FROM wellness_notes WHERE employee_id = ? ORDER BY created_at DESC", [employee_id])
    
    # Get last 20 anomalous readings
    readings = await d1.execute("""
        SELECT timestamp, heart_rate, spo2, skin_temperature 
        FROM sensor_readings 
        WHERE employee_id = ? 
        ORDER BY timestamp DESC LIMIT 20
    """, [employee_id])
    
    return {"data": {"record": record, "notes": notes, "readings": readings}}

@router.put("/{employee_id}/status")
async def update_status(employee_id: str, data: StatusUpdate):
    await d1.execute("""
        INSERT INTO wellness_status (employee_id, status) VALUES (?, ?)
        ON CONFLICT(employee_id) DO UPDATE SET status = excluded.status, updated_at = CURRENT_TIMESTAMP
    """, [employee_id, data.status.upper()])
    return {"success": True}

@router.post("/{employee_id}/notes")
async def add_note(employee_id: str, data: NoteCreate):
    await d1.execute(
        "INSERT INTO wellness_notes (employee_id, note, added_by) VALUES (?, ?, ?)",
        [employee_id, data.note, data.added_by]
    )
    return {"success": True}
