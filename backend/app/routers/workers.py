from fastapi import APIRouter, HTTPException, Query
from app.services.d1_client import d1
from typing import Optional

router = APIRouter(prefix="/api/workers", tags=["Workers"])

@router.get("")
async def get_workers(
    search: Optional[str] = Query(None), 
    factory_id: Optional[str] = Query(None), 
    department_id: Optional[str] = Query(None), 
    status: Optional[str] = Query(None), 
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100)
):
    offset = (page - 1) * limit
    where_clauses = []
    params = []
    
    if search:
        where_clauses.append("(employee_name LIKE ? OR employee_id LIKE ?)")
        params.extend([f"%{search}%", f"%{search}%"])
    if department_id:
        where_clauses.append("department = ?")
        params.append(department_id)
    if status is not None and status.lower() != "all":
        # Usually frontend sends boolean or true/false, DB has ACTIVE/INACTIVE
        if status.lower() == "true":
            where_clauses.append("status = 'ACTIVE'")
        elif status.lower() == "false":
            where_clauses.append("status = 'INACTIVE'")
            
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    count_res = await d1.execute(f"SELECT COUNT(*) as c FROM employees{where_sql}", params)
    total = count_res[0]['c'] if count_res else 0
    
    sql = f"SELECT id, employee_id as worker_id, employee_name as name, department as department_name, status FROM employees{where_sql} LIMIT ? OFFSET ?"
    res = await d1.execute(sql, params + [limit, offset])
    
    for r in res:
        r['status'] = True if r['status'] == 'ACTIVE' else False
        
    return {"data": res, "total": total, "page": page, "limit": limit}

@router.get("/{worker_id}")
async def get_worker(worker_id: str):
    res = await d1.execute("SELECT id, employee_id as worker_id, employee_name as name, department as department_name, status FROM employees WHERE employee_id = ?", [worker_id])
    if not res:
        raise HTTPException(status_code=404, detail="Worker not found")
    r = res[0]
    r['status'] = True if r['status'] == 'ACTIVE' else False
    return {"data": r}
