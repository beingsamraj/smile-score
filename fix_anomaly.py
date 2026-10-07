import os

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_func = """async def run_anomaly_detection():
    try:
        # Get emotions from the last 15 minutes
        since = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        res = supabase.table("emotions").select("emotion_id, worker_id, smile_score, created_at").gte("created_at", since).execute()
        recent_emotions = res.data or []
        
        for e in recent_emotions:
            if e.get("smile_score") is not None:
                # Basic hour of day
                hour = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).hour
                score = float(e["smile_score"])
                
                result = await anomaly_detector.detect_anomaly(score, hour)
                
                if result["is_anomaly"] and result["severity"] in ["WARNING", "CRITICAL"]:
                    # Create an alert
                    new_alert = {
                        "severity": result["severity"].lower(),
                        "message": f"Anomalous emotion drop detected for worker {e['worker_id']}. Anomaly Score: {result['anomaly_score']}",
                        "worker_id": e["worker_id"],
                        "alert_type": "ANOMALY",
                        "status": "open"
                    }
                    supabase.table("alerts").insert(new_alert).execute()
                    
    except Exception as e:
        logger.error(f"Error in run_anomaly_detection: {e}")"""

new_func = """async def run_anomaly_detection():
    try:
        from app.services.d1_client import d1
        # Get emotions from the last 15 minutes
        since = (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat()
        
        # Use d1 instead of supabase
        recent_emotions = await d1.execute("SELECT * FROM emotions WHERE created_at >= ?", [since])
        recent_emotions = recent_emotions or []
        
        for e in recent_emotions:
            if e.get("smile_score") is not None:
                # Basic hour of day
                try:
                    hour = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")).hour
                except:
                    hour = 12
                score = float(e["smile_score"])
                
                result = await anomaly_detector.detect_anomaly(score, hour)
                
                if result.get("is_anomaly") and result.get("severity") in ["WARNING", "CRITICAL"]:
                    import uuid
                    alert_id = f"ALT-{str(uuid.uuid4())[:8].upper()}"
                    # Create an alert
                    # Note: You may need to create an 'alerts' table if it does not exist
                    try:
                        await d1.execute(
                            "INSERT INTO alerts (alert_id, severity, message, worker_id, alert_type, status) VALUES (?, ?, ?, ?, ?, ?)",
                            [alert_id, result["severity"].lower(), f"Anomalous emotion drop detected for worker {e['worker_id']}. Anomaly Score: {result['anomaly_score']}", e["worker_id"], "ANOMALY", "open"]
                        )
                    except Exception as inner_e:
                        logger.warning(f"Failed to insert alert (perhaps missing alerts table): {inner_e}")
                    
    except Exception as e:
        logger.error(f"Error in run_anomaly_detection: {e}")"""

text = text.replace(old_func, new_func)

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
