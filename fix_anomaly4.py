import os

with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
old_text = text[text.find('async def run_anomaly_detection():'):text.find('from pydantic import BaseModel\nfrom fastapi import HTTPException')]

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
                    try:
                        new_alert = {
                            "severity": result["severity"].lower(),
                            "message": f"Anomalous emotion drop detected for worker {e.get('worker_id', e.get('employee_id', 'UNKNOWN'))}. Anomaly Score: {result['anomaly_score']}",
                            "worker_id": e.get("worker_id", e.get("employee_id", "UNKNOWN")),
                            "alert_type": "ANOMALY",
                            "status": "open"
                        }
                        await d1.execute(
                            "INSERT INTO alerts (alert_id, severity, message, worker_id, alert_type, status) VALUES (?, ?, ?, ?, ?, ?)",
                            [alert_id, new_alert["severity"], new_alert["message"], new_alert["worker_id"], new_alert["alert_type"], new_alert["status"]]
                        )
                        # Push via WebSocket
                        await manager.broadcast({
                            "type": "new_alert",
                            "data": new_alert
                        })
                    except Exception as inner_e:
                        logging.warning(f"Failed to insert alert: {inner_e}")
                    
    except Exception as e:
        logging.error(f"Error in run_anomaly_detection: {e}")

"""

text = text.replace(old_text, new_func)

with open('backend/app/main.py', 'w', encoding='utf-8') as f:
    f.write(text)
