with open('backend/app/main.py', 'r', encoding='utf-8') as f:
    text = f.read()

task = """
async def compute_factory_risks():
    try:
        from app.routers.ai_features import _get_factory_features, risk_predictor
        from app.services.d1_client import d1
        
        factories = await d1.execute("SELECT factory_id FROM factories")
        for f in factories:
            fid = f["factory_id"]
            features = await _get_factory_features(fid)
            if features:
                pred = await risk_predictor.predict(**features)
                now = datetime.now(timezone.utc).isoformat()
                await d1.execute(
                    "INSERT INTO factory_risk (factory_id, risk_level, confidence, average_smile_score, sad_ratio, happy_ratio, active_workers, calculated_at, model_version) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [fid, pred["risk_level"], pred["confidence"], features["average_smile_score"], features["sad_ratio"], features["happy_ratio"], features["active_workers"], now, pred.get("model_version", "risk-v1")]
                )
                
                # Broadcast via WebSocket
                await manager.broadcast({
                    "type": "factory_risk_update",
                    "data": {
                        "factory_id": fid,
                        "risk_level": pred["risk_level"],
                        "confidence": pred["confidence"]
                    }
                })
    except Exception as e:
        logger.exception("compute_factory_risks failed")
"""

if 'compute_factory_risks' not in text:
    text = text.replace('async def run_anomaly_detection():', task + '\nasync def run_anomaly_detection():')
    text = text.replace('scheduler.start()', 'scheduler.add_job(compute_factory_risks, \'interval\', minutes=60, coalesce=True, max_instances=1)\n    scheduler.start()')
    with open('backend/app/main.py', 'w', encoding='utf-8') as f:
        f.write(text)
