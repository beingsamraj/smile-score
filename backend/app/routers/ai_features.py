from fastapi import APIRouter, HTTPException, Query
from app.services.d1_client import d1
from app.ai_models.forecaster import forecaster
from app.ai_models.risk_predictor import ProductionRiskPredictor
from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["AI Features"])
risk_predictor = ProductionRiskPredictor()

@router.get("/forecast/factory/{factory_id}")
async def get_factory_forecast(factory_id: str, hours: int = Query(8, ge=1, le=48)):
    # Validate factory
    factory_res = await d1.execute("SELECT factory_id FROM factories WHERE factory_id = ?", [factory_id])
    if not factory_res:
        raise HTTPException(status_code=404, detail="Factory not found")

    # Fetch historical data (last 24 hours of smile scores)
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    emotions = await d1.execute(
        "SELECT created_at as timestamp, smile_score FROM emotions WHERE factory_id = ? AND created_at >= ? ORDER BY created_at ASC",
        [factory_id, since]
    )

    if len(emotions) < 2:
        # Fallback or error based on spec
        raise HTTPException(status_code=400, detail={"error": "Insufficient historical data for forecasting", "code": "INSUFFICIENT_DATA"})

    # Prepare for training
    historical_data = []
    for e in emotions:
        if e.get("smile_score") is not None:
            historical_data.append({"timestamp": e["timestamp"], "smile_score": float(e["smile_score"])})

    if len(historical_data) < 2:
        raise HTTPException(status_code=400, detail={"error": "Insufficient numerical historical data for forecasting", "code": "INSUFFICIENT_DATA"})

    try:
        await forecaster.train(historical_data)
        forecast_results = await forecaster.forecast_next_n_hours(hours)
    except Exception as e:
        logger.exception("Forecaster failed")
        raise HTTPException(status_code=500, detail={"error": "Model prediction failure", "code": "MODEL_FAILURE", "detail": str(e)})

    # Format exactly as requested
    formatted_forecast = [
        {"timestamp": f["timestamp"], "predicted_smile_score": f["smile_score"]}
        for f in forecast_results
    ]

    return {
        "factory_id": factory_id,
        "forecast_hours": hours,
        "forecast": formatted_forecast,
        "model": "prophet",
        "model_version": "forecast-v1"
    }

async def _get_factory_features(factory_id: str):
    # Calculate real features for risk prediction
    now = datetime.now(timezone.utc)
    hour = now.hour
    
    since = (now - timedelta(hours=1)).isoformat()
    emotions = await d1.execute(
        "SELECT emotion, smile_score FROM emotions WHERE factory_id = ? AND created_at >= ?",
        [factory_id, since]
    )
    
    workers_res = await d1.execute(
        "SELECT COUNT(*) as c FROM workers WHERE factory_id = ? AND status = 1",
        [factory_id]
    )
    active_workers = int(workers_res[0]["c"]) if workers_res else 0

    if not emotions:
        return None

    scores = [float(e["smile_score"]) for e in emotions if e.get("smile_score") is not None]
    avg_score = sum(scores) / len(scores) if scores else 50.0
    
    total_emotions = len(emotions)
    sad_count = sum(1 for e in emotions if str(e.get("emotion")).upper() == "SAD")
    happy_count = sum(1 for e in emotions if str(e.get("emotion")).upper() == "HAPPY")
    
    sad_ratio = sad_count / total_emotions if total_emotions else 0.0
    happy_ratio = happy_count / total_emotions if total_emotions else 0.0
    
    return {
        "average_smile_score": round(avg_score, 1),
        "sad_ratio": round(sad_ratio, 2),
        "happy_ratio": round(happy_ratio, 2),
        "active_workers": active_workers,
        "hour": hour
    }

@router.get("/risk/factory/{factory_id}")
async def get_factory_risk(factory_id: str):
    factory_res = await d1.execute("SELECT factory_id FROM factories WHERE factory_id = ?", [factory_id])
    if not factory_res:
        raise HTTPException(status_code=404, detail="Factory not found")

    features = await _get_factory_features(factory_id)
    if not features:
        raise HTTPException(status_code=400, detail={"error": "Insufficient recent data for risk prediction", "code": "INSUFFICIENT_DATA"})

    try:
        prediction = await risk_predictor.predict(**features)
    except Exception as e:
        logger.exception("Risk predictor failed")
        raise HTTPException(status_code=500, detail={"error": "Model prediction failure", "code": "MODEL_FAILURE", "detail": str(e)})

    return {
        "factory_id": factory_id,
        "risk_level": prediction["risk_level"],
        "confidence": round(prediction["confidence"], 2),
        "features": features,
        "model_version": prediction.get("model_version", "risk-v1")
    }

@router.get("/risk/factories")
async def get_all_factories_risk(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    offset = (page - 1) * limit
    
    count_res = await d1.execute("SELECT COUNT(*) as c FROM factories")
    total = count_res[0]['c'] if count_res else 0
    
    factories = await d1.execute("SELECT factory_id FROM factories ORDER BY factory_id ASC LIMIT ? OFFSET ?", [limit, offset])
    
    items = []
    for f in factories:
        fid = f["factory_id"]
        features = await _get_factory_features(fid)
        if features:
            try:
                pred = await risk_predictor.predict(**features)
                items.append({
                    "factory_id": fid,
                    "risk_level": pred["risk_level"],
                    "confidence": round(pred["confidence"], 2),
                    "last_calculated": datetime.now(timezone.utc).isoformat()
                })
            except Exception:
                pass
                
    return {
        "items": items,
        "page": page,
        "limit": limit,
        "total": total
    }

@router.get("/recommendations/factory/{factory_id}")
async def get_recommendations(factory_id: str):
    factory_res = await d1.execute("SELECT factory_id FROM factories WHERE factory_id = ?", [factory_id])
    if not factory_res:
        raise HTTPException(status_code=404, detail="Factory not found")

    features = await _get_factory_features(factory_id)
    if not features:
        raise HTTPException(status_code=400, detail={"error": "Insufficient data to generate recommendations", "code": "INSUFFICIENT_DATA"})
        
    try:
        prediction = await risk_predictor.predict(**features)
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Model failure", "code": "MODEL_FAILURE"})

    risk_level = prediction["risk_level"]
    avg = features["average_smile_score"]
    sad = features["sad_ratio"]
    
    recommendations = []
    
    if risk_level == "HIGH":
        recommendations.append({
            "priority": "HIGH",
            "action": "Review current worker wellbeing conditions immediately",
            "reason": "Production risk model detected high stress indicators"
        })
    elif risk_level == "MEDIUM":
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Monitor factory floor for emerging bottlenecks",
            "reason": "Elevated risk patterns detected"
        })
        
    if sad > 0.2:
        recommendations.append({
            "priority": "HIGH",
            "action": "Dispatch supervisor to check on worker morale",
            "reason": f"High sad expression ratio ({sad*100:.1f}%)"
        })
        
    if not recommendations:
        recommendations.append({
            "priority": "LOW",
            "action": "Maintain current operational cadence",
            "reason": "All metrics are within nominal ranges"
        })

    return {
        "factory_id": factory_id,
        "risk_level": risk_level,
        "recommendations": recommendations
    }
