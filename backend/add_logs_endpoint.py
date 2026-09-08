import sys

with open("e:/smile-score/backend/app/routers/reports.py", "r", encoding="utf-8") as f:
    content = f.read()

new_endpoint = """
@router.get("/logs")
def get_report_logs(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    factory_id: Optional[str] = None
):
    try:
        start, end = get_date_range(start_date, end_date)
        
        try:
            # We fetch manually to avoid complex join issues if foreign keys are not perfectly set
            query = supabase.table("mood_logs").select("*")
            query = query.gte("recorded_at", start).lte("recorded_at", end)
            if factory_id:
                query = query.eq("factory_id", factory_id)
                
            res = query.order("recorded_at", desc=True).limit(2000).execute()
            logs = res.data or []
            
            # Fetch relational data to map IDs to Names
            workers_data = supabase.table("workers").select("worker_id, name").execute().data or []
            deps_data = supabase.table("departments").select("department_id, department_name").execute().data or []
            facs_data = supabase.table("factories").select("factory_id, factory_name").execute().data or []
            
            workers_map = {w["worker_id"]: w["name"] for w in workers_data}
            deps_map = {d["department_id"]: d["department_name"] for d in deps_data}
            facs_map = {f["factory_id"]: f["factory_name"] for f in facs_data}
            
        except Exception as e:
            logs = []
            workers_map = {}
            deps_map = {}
            facs_map = {}
            
        result = []
        for d in logs:
            result.append({
                "worker_id": d.get("worker_id"),
                "worker_name": workers_map.get(d.get("worker_id"), "Unknown"),
                "mood": d.get("mood"),
                "department": deps_map.get(d.get("department_id"), "Unknown"),
                "factory": facs_map.get(d.get("factory_id"), "Unknown"),
                "recorded_at": d.get("recorded_at")
            })
            
        return {"logs": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""

if 'def get_report_logs' not in content:
    content += "\n" + new_endpoint
    with open("e:/smile-score/backend/app/routers/reports.py", "w", encoding="utf-8") as f:
        f.write(content)
