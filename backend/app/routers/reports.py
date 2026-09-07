from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.database import supabase
from collections import defaultdict
import uuid

router = APIRouter(prefix="/api/reports", tags=["reports"])

def get_date_range(start_date: str, end_date: str):
    if not start_date:
        start = datetime.utcnow() - timedelta(days=30)
    else:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
    if not end_date:
        end = datetime.utcnow()
    else:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
    return start.isoformat(), end.isoformat()

def build_query(table: str, start_date: str, end_date: str, factory_id: str = None, department_id: str = None, worker_id: str = None):
    # mood_logs uses recorded_at
    query = supabase.table(table).select("*").gte("recorded_at", start_date).lte("recorded_at", end_date)
    if factory_id:
        query = query.eq("factory_id", factory_id)
    if department_id:
        query = query.eq("department_id", department_id)
    if worker_id:
        query = query.eq("worker_id", worker_id)
    return query

def get_score_from_mood(mood: str) -> float:
    if mood == 'happy': return 100.0
    if mood == 'ok': return 50.0
    return 0.0

@router.get("/summary")
def get_summary(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    factory_id: Optional[str] = None,
    department_id: Optional[str] = None
):
    try:
        start, end = get_date_range(start_date, end_date)
        try:
            res = build_query("mood_logs", start, end, factory_id, department_id).execute()
            data = res.data or []
        except Exception as e:
            data = []
            
        total = len(data)
        if total == 0:
            return {
                "average_smile_score": 0,
                "happy_percentage": 0,
                "ok_percentage": 0,
                "sad_percentage": 0,
                "happy_count": 0,
                "ok_count": 0,
                "sad_count": 0,
                "active_workers": 0,
                "at_risk_workers": 0,
                "total_responses": 0,
                "has_data": False
            }
            
        happy = sum(1 for e in data if e.get("mood") == "happy")
        ok = sum(1 for e in data if e.get("mood") == "ok")
        sad = sum(1 for e in data if e.get("mood") == "sad")
        
        scores = [get_score_from_mood(e.get("mood")) for e in data if e.get("mood")]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        unique_workers = set(e.get("worker_id") for e in data if e.get("worker_id"))
        
        worker_stats = defaultdict(lambda: {"total": 0, "sad": 0, "scores": []})
        for e in data:
            wid = e.get("worker_id")
            if wid:
                worker_stats[wid]["total"] += 1
                if e.get("mood") == "sad":
                    worker_stats[wid]["sad"] += 1
                if e.get("mood"):
                    worker_stats[wid]["scores"].append(get_score_from_mood(e.get("mood")))
                    
        at_risk = 0
        for wid, stats in worker_stats.items():
            avg_w = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 100
            if avg_w < 50 or (stats["sad"] / stats["total"]) > 0.5:
                at_risk += 1
        
        return {
            "average_smile_score": round(avg_score, 1),
            "happy_percentage": round((happy / total) * 100),
            "ok_percentage": round((ok / total) * 100),
            "sad_percentage": round((sad / total) * 100),
            "happy_count": happy,
            "ok_count": ok,
            "sad_count": sad,
            "active_workers": len(unique_workers),
            "at_risk_workers": at_risk,
            "total_responses": total,
            "has_data": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/smile-score-trend")
def get_smile_score_trend(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    factory_id: Optional[str] = None,
    department_id: Optional[str] = None,
    aggregation: str = "daily"
):
    try:
        start, end = get_date_range(start_date, end_date)
        try:
            res = build_query("mood_logs", start, end, factory_id, department_id).order("recorded_at").execute()
            data = res.data or []
        except Exception:
            data = []
            
        if not data:
            return {"trend": []}
            
        trend_dict = defaultdict(lambda: {"count": 0, "score_sum": 0.0, "min": 100.0, "max": 0.0})
        
        for e in data:
            if not e.get("mood") or not e.get("recorded_at"):
                continue
                
            dt = datetime.fromisoformat(e.get("recorded_at").replace('Z', '+00:00'))
            
            if aggregation == "hourly":
                key = dt.strftime("%Y-%m-%d %H:00")
            elif aggregation == "weekly":
                start_of_week = dt - timedelta(days=dt.weekday())
                key = start_of_week.strftime("%Y-%m-%d")
            elif aggregation == "monthly":
                key = dt.strftime("%Y-%m")
            else:
                key = dt.strftime("%Y-%m-%d")
                
            score = get_score_from_mood(e.get("mood"))
            trend_dict[key]["count"] += 1
            trend_dict[key]["score_sum"] += score
            trend_dict[key]["min"] = min(trend_dict[key]["min"], score)
            trend_dict[key]["max"] = max(trend_dict[key]["max"], score)
            
        result = []
        for key in sorted(trend_dict.keys()):
            val = trend_dict[key]
            result.append({
                "date": key,
                "average_score": round(val["score_sum"] / val["count"], 1),
                "responses": val["count"],
                "min": round(val["min"], 1),
                "max": round(val["max"], 1)
            })
            
        return {"trend": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emotion-distribution")
def get_emotion_distribution(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    factory_id: Optional[str] = None,
    department_id: Optional[str] = None
):
    try:
        start, end = get_date_range(start_date, end_date)
        try:
            res = build_query("mood_logs", start, end, factory_id, department_id).execute()
            data = res.data or []
        except Exception:
            data = []
            
        total = len(data)
        happy = sum(1 for e in data if e.get("mood") == "happy")
        ok = sum(1 for e in data if e.get("mood") == "ok")
        sad = sum(1 for e in data if e.get("mood") == "sad")
        
        return {
            "happy": happy,
            "ok": ok,
            "sad": sad,
            "total": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/departments")
def get_department_analysis(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    factory_id: Optional[str] = None
):
    try:
        start, end = get_date_range(start_date, end_date)
        
        try:
            deps_query = supabase.table("departments").select("*")
            if factory_id:
                deps_query = deps_query.eq("factory_id", factory_id)
            deps_data = deps_query.execute().data or []
        except Exception:
            deps_data = []
            
        try:
            logs_data = build_query("mood_logs", start, end, factory_id).execute().data or []
        except Exception:
            logs_data = []
            
        dept_stats = defaultdict(lambda: {"total": 0, "happy": 0, "ok": 0, "sad": 0, "score_sum": 0, "score_count": 0, "workers": set()})
        
        for e in logs_data:
            did = e.get("department_id")
            if did:
                dept_stats[did]["total"] += 1
                if e.get("mood") == "happy": dept_stats[did]["happy"] += 1
                elif e.get("mood") == "ok": dept_stats[did]["ok"] += 1
                elif e.get("mood") == "sad": dept_stats[did]["sad"] += 1
                
                if e.get("mood"):
                    dept_stats[did]["score_sum"] += get_score_from_mood(e.get("mood"))
                    dept_stats[did]["score_count"] += 1
                    
                if e.get("worker_id"):
                    dept_stats[did]["workers"].add(e.get("worker_id"))
                    
        result = []
        for d in deps_data:
            did = d.get("department_id")
            stats = dept_stats.get(did, {"total": 0, "happy": 0, "ok": 0, "sad": 0, "score_sum": 0, "score_count": 0, "workers": set()})
            
            total = stats["total"]
            avg_score = stats["score_sum"] / stats["score_count"] if stats["score_count"] > 0 else 0
            
            risk = "Healthy"
            if total > 0:
                sad_pct = stats["sad"] / total
                if avg_score < 50 or sad_pct > 0.4:
                    risk = "High Risk"
                elif avg_score < 70 or sad_pct > 0.2:
                    risk = "Attention Required"
                elif avg_score < 80:
                    risk = "Moderate"
            
            result.append({
                "department_id": did,
                "department_name": d.get("department_name"),
                "factory_id": d.get("factory_id"),
                "responses": total,
                "workers": len(stats["workers"]),
                "average_smile_score": round(avg_score, 1),
                "happy_percentage": round((stats["happy"] / total * 100) if total > 0 else 0),
                "ok_percentage": round((stats["ok"] / total * 100) if total > 0 else 0),
                "sad_percentage": round((stats["sad"] / total * 100) if total > 0 else 0),
                "risk_status": risk if total > 0 else "No Data"
            })
            
        return {"departments": sorted(result, key=lambda x: x["average_smile_score"] if x["responses"]>0 else -1, reverse=True)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/factories")
def get_factory_analysis(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
):
    try:
        start, end = get_date_range(start_date, end_date)
        
        try:
            facs_data = supabase.table("factories").select("*").execute().data or []
            logs_data = build_query("mood_logs", start, end).execute().data or []
        except Exception:
            facs_data = []
            logs_data = []
            
        fac_stats = defaultdict(lambda: {"total": 0, "happy": 0, "ok": 0, "sad": 0, "score_sum": 0, "score_count": 0, "workers": set()})
        
        for e in logs_data:
            fid = e.get("factory_id")
            if fid:
                fac_stats[fid]["total"] += 1
                if e.get("mood") == "happy": fac_stats[fid]["happy"] += 1
                elif e.get("mood") == "ok": fac_stats[fid]["ok"] += 1
                elif e.get("mood") == "sad": fac_stats[fid]["sad"] += 1
                
                if e.get("mood"):
                    fac_stats[fid]["score_sum"] += get_score_from_mood(e.get("mood"))
                    fac_stats[fid]["score_count"] += 1
                    
                if e.get("worker_id"):
                    fac_stats[fid]["workers"].add(e.get("worker_id"))
                    
        result = []
        for f in facs_data:
            fid = f.get("factory_id")
            stats = fac_stats.get(fid, {"total": 0, "happy": 0, "ok": 0, "sad": 0, "score_sum": 0, "score_count": 0, "workers": set()})
            
            total = stats["total"]
            avg_score = stats["score_sum"] / stats["score_count"] if stats["score_count"] > 0 else 0
            
            risk = "Healthy"
            if total > 0:
                sad_pct = stats["sad"] / total
                if avg_score < 60 or sad_pct > 0.3:
                    risk = "High Risk"
                elif avg_score < 75 or sad_pct > 0.15:
                    risk = "Attention Required"
                    
            result.append({
                "factory_id": fid,
                "factory_name": f.get("factory_name"),
                "responses": total,
                "workers": len(stats["workers"]),
                "average_smile_score": round(avg_score, 1),
                "happy_percentage": round((stats["happy"] / total * 100) if total > 0 else 0),
                "ok_percentage": round((stats["ok"] / total * 100) if total > 0 else 0),
                "sad_percentage": round((stats["sad"] / total * 100) if total > 0 else 0),
                "risk_status": risk if total > 0 else "No Data"
            })
            
        return {"factories": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workers")
def get_workers_analysis(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    factory_id: Optional[str] = None,
    department_id: Optional[str] = None
):
    try:
        start, end = get_date_range(start_date, end_date)
        
        try:
            workers_query = supabase.table("workers").select("*")
            if factory_id: workers_query = workers_query.eq("factory_id", factory_id)
            if department_id: workers_query = workers_query.eq("department_id", department_id)
            workers_data = workers_query.execute().data or []
            
            deps_data = supabase.table("departments").select("department_id, department_name").execute().data or []
            deps_map = {d["department_id"]: d["department_name"] for d in deps_data}
            
            logs_data = build_query("mood_logs", start, end, factory_id, department_id).order("recorded_at").execute().data or []
        except Exception:
            workers_data = []
            deps_map = {}
            logs_data = []
            
        worker_stats = defaultdict(lambda: {"total": 0, "happy": 0, "ok": 0, "sad": 0, "score_sum": 0, "score_count": 0, "latest": None, "latest_time": None})
        
        for e in logs_data:
            wid = e.get("worker_id")
            if wid:
                worker_stats[wid]["total"] += 1
                if e.get("mood") == "happy": worker_stats[wid]["happy"] += 1
                elif e.get("mood") == "ok": worker_stats[wid]["ok"] += 1
                elif e.get("mood") == "sad": worker_stats[wid]["sad"] += 1
                
                if e.get("mood"):
                    worker_stats[wid]["score_sum"] += get_score_from_mood(e.get("mood"))
                    worker_stats[wid]["score_count"] += 1
                    
                worker_stats[wid]["latest"] = e.get("mood")
                worker_stats[wid]["latest_time"] = e.get("recorded_at")
                
        result = []
        for w in workers_data:
            wid = w.get("worker_id")
            stats = worker_stats.get(wid)
            if not stats and start_date: 
                continue # optionally skip workers with no data
                
            stats = stats or {"total": 0, "happy": 0, "ok": 0, "sad": 0, "score_sum": 0, "score_count": 0, "latest": None, "latest_time": None}
            total = stats["total"]
            avg_score = stats["score_sum"] / stats["score_count"] if stats["score_count"] > 0 else 0
            
            status = "Stable"
            if total > 0:
                sad_pct = stats["sad"] / total
                if avg_score >= 85: status = "Excellent"
                elif avg_score >= 70: status = "Good"
                elif avg_score < 50 or sad_pct > 0.5: status = "High Risk"
                elif avg_score < 65 or sad_pct > 0.2: status = "Needs Attention"
            else:
                status = "No Data"
                
            result.append({
                "worker_id": wid,
                "employee_id": w.get("employee_id"),
                "name": w.get("name"),
                "department_name": deps_map.get(w.get("department_id"), "Unknown"),
                "responses": total,
                "average_smile_score": round(avg_score, 1),
                "happy_percentage": round((stats["happy"] / total * 100) if total > 0 else 0),
                "ok_percentage": round((stats["ok"] / total * 100) if total > 0 else 0),
                "sad_percentage": round((stats["sad"] / total * 100) if total > 0 else 0),
                "latest_feedback": stats["latest"],
                "latest_feedback_time": stats["latest_time"],
                "status": status
            })
            
        return {"workers": sorted(result, key=lambda x: x["average_smile_score"] if x["responses"] > 0 else 999)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workers/{worker_id}")
def get_individual_worker_report(worker_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    try:
        start, end = get_date_range(start_date, end_date)
        try:
            worker_res = supabase.table("workers").select("*").eq("worker_id", worker_id).execute()
            if not worker_res.data:
                raise HTTPException(status_code=404, detail="Worker not found")
            worker = worker_res.data[0]
            
            dept_res = supabase.table("departments").select("department_name").eq("department_id", worker.get("department_id")).execute()
            dept_name = dept_res.data[0].get("department_name") if dept_res.data else "Unknown"
            
            logs_res = build_query("mood_logs", start, end, worker_id=worker_id).order("recorded_at", desc=True).execute()
            logs = logs_res.data or []
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
        total = len(logs)
        happy = sum(1 for e in logs if e.get("mood") == "happy")
        ok = sum(1 for e in logs if e.get("mood") == "ok")
        sad = sum(1 for e in logs if e.get("mood") == "sad")
        
        scores = [get_score_from_mood(e.get("mood")) for e in logs if e.get("mood")]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        history = []
        for e in logs:
            history.append({
                "date": e.get("recorded_at"),
                "mood": e.get("mood"),
                "smile_score": get_score_from_mood(e.get("mood")),
                "device_id": e.get("device_id")
            })
            
        # Reverse history for chart (oldest to newest)
        chart_data = [{"date": h["date"], "score": h["smile_score"]} for h in reversed(history)]
        
        return {
            "worker": {
                "worker_id": worker.get("worker_id"),
                "employee_id": worker.get("employee_id"),
                "name": worker.get("name"),
                "department": dept_name,
                "designation": worker.get("designation"),
                "rfid_uid": worker.get("rfid_uid"),
                "status": "ACTIVE" if worker.get("status") else "INACTIVE"
            },
            "stats": {
                "average_smile_score": round(avg_score, 1),
                "total_responses": total,
                "happy": happy,
                "ok": ok,
                "sad": sad,
                "latest_feedback": logs[0].get("mood") if logs else None
            },
            "history": history,
            "chart_data": chart_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-analysis")
def get_risk_analysis(
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None,
    factory_id: Optional[str] = None,
    department_id: Optional[str] = None
):
    try:
        start, end = get_date_range(start_date, end_date)
        
        try:
            deps_data = supabase.table("departments").select("department_id, department_name").execute().data or []
            deps_map = {d["department_id"]: d["department_name"] for d in deps_data}
            
            logs_data = build_query("mood_logs", start, end, factory_id, department_id).execute().data or []
        except Exception:
            deps_map = {}
            logs_data = []
            
        dept_stats = defaultdict(lambda: {"total": 0, "sad": 0, "score_sum": 0, "score_count": 0})
        for e in logs_data:
            did = e.get("department_id")
            if did:
                dept_stats[did]["total"] += 1
                if e.get("mood") == "sad": dept_stats[did]["sad"] += 1
                if e.get("mood"):
                    dept_stats[did]["score_sum"] += get_score_from_mood(e.get("mood"))
                    dept_stats[did]["score_count"] += 1
                    
        alerts = []
        for did, stats in dept_stats.items():
            total = stats["total"]
            if total > 5: 
                avg_score = stats["score_sum"] / stats["score_count"] if stats["score_count"] > 0 else 100
                sad_pct = stats["sad"] / total
                d_name = deps_map.get(did, f"Dept {did}")
                
                if avg_score < 60:
                    alerts.append({
                        "type": "Wellbeing Decline",
                        "severity": "High Risk",
                        "entity_type": "Department",
                        "entity_name": d_name,
                        "description": f"Average Smile Score is critically low ({round(avg_score, 1)}%).",
                        "recommended_action": "Schedule department-wide meeting to assess concerns.",
                        "current_score": round(avg_score, 1)
                    })
                if sad_pct > 0.3:
                    alerts.append({
                        "type": "High Negative Feedback",
                        "severity": "Attention Required",
                        "entity_type": "Department",
                        "entity_name": d_name,
                        "description": f"Unusually high sad responses ({round(sad_pct * 100)}%).",
                        "recommended_action": "Investigate recent changes in work conditions.",
                        "current_score": round(avg_score, 1)
                    })
                    
        return {"alerts": sorted(alerts, key=lambda x: 0 if x["severity"] == "High Risk" else 1)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
