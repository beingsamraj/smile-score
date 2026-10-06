from fastapi import Depends, APIRouter
from app.ai_models.anomaly_detector import anomaly_detector
from app.ai_models.forecaster import forecaster
from app.ai_models.risk_predictor import predictor

router = APIRouter(prefix="/api/ml", tags=["ML"])

@router.get("/anomaly/status")
def anomaly_status(detector = Depends(lambda: anomaly_detector)):
    return {"model": "anomaly_detector", "trained": detector.is_trained}

@router.get("/forecaster/status")
def forecaster_status(f = Depends(lambda: forecaster)):
    return {"model": "forecaster", "trained": f.is_trained}

@router.get("/risk/status")
def risk_status(r = Depends(lambda: predictor)):
    return {"model": "risk_predictor", "trained": r.is_trained}

# Optional training endpoints (POST) – accept JSON payloads
@router.post("/forecaster/train")
async def forecaster_train(data: list, f = Depends(lambda: forecaster)):
    """Train the forecaster with a list of historical records.
    Expected format: [{"timestamp": "...", "smile_score": <float>}, ...]
    """
    await f.train(data)
    return {"status": "trained", "model": "forecaster"}

@router.post("/risk/train")
async def risk_train(df: list, r = Depends(lambda: predictor)):
    """Train risk predictor with a list of dicts containing required features and ``risk_level``.
    """
    import pandas as pd
    df_pd = pd.DataFrame(df)
    await r.train(df_pd)
    return {"status": "trained", "model": "risk_predictor"}
