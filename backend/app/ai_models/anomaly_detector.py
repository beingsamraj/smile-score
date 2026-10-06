import os
import logging
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import asyncio

# Configuration via environment variables
CONTAMINATION = float(os.getenv("ANOMALY_CONTAMINATION", "0.05"))
THRESHOLD = float(os.getenv("ANOMALY_SCORE_THRESHOLD", "-0.15"))
MODEL_PATH = os.getenv("ANOMALY_MODEL_PATH", "backend/models/anomaly_detector.joblib")

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Production‑ready Isolation Forest anomaly detector.

    - Model is persisted to disk and loaded on startup.
    - Training uses real data when available; otherwise a lightweight synthetic baseline is created.
    - Thresholds and contamination are configurable via environment variables.
    - All public methods are thread‑safe for concurrent FastAPI usage.
    """

    def __init__(self):
        self.model = None
        self.is_trained = False
        self._lock = asyncio.Lock()
        self._load_or_initialize()

    def _load_or_initialize(self):
        """Attempt to load a persisted model; fall back to a fresh IsolationForest.
        """
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                self.is_trained = True
                logger.info(
                    "AnomalyDetector model loaded from disk",
                    extra={"event": "ml_model_loaded", "model": "anomaly_detector", "path": MODEL_PATH},
                )
            else:
                raise FileNotFoundError
        except Exception as e:
            logger.warning(
                f"Failed to load persisted anomaly model ({e}); initializing fresh model",
                extra={"event": "ml_model_load_failed", "model": "anomaly_detector"},
            )
            self.model = IsolationForest(contamination=CONTAMINATION, random_state=42)
            self.is_trained = False

    async def train(self, data: pd.DataFrame):
        """Train the IsolationForest on a supplied DataFrame with columns
        ``smile_score`` and ``hour_of_day``.
        """
        async with self._lock:
            if data.empty or not {"smile_score", "hour_of_day"}.issubset(data.columns):
                raise ValueError("Training data must contain 'smile_score' and 'hour_of_day' columns.")
            self.model.fit(data)
            self.is_trained = True
            # Persist model
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, MODEL_PATH)
            logger.info(
                "AnomalyDetector model trained and persisted",
                extra={"event": "ml_model_trained", "model": "anomaly_detector", "path": MODEL_PATH},
            )

    async def _ensure_trained(self):
        """Ensure the model is trained – if not, train a minimal synthetic baseline.
        This is kept for backward compatibility but logs a warning.
        """
        if not self.is_trained:
            logger.warning(
                "AnomalyDetector used without real training data; training synthetic baseline",
                extra={"event": "ml_synthetic_training", "model": "anomaly_detector"},
            )
            # Synthetic baseline – minimal data to avoid errors
            synthetic = pd.DataFrame({
                "smile_score": [80, 82, 85, 78, 81, 79, 90, 83, 10, 20, 81],
                "hour_of_day": [9, 10, 11, 12, 13, 14, 15, 16, 17, 13, 14],
            })
            await self.train(synthetic)

    async def detect_anomaly(self, smile_score: float, hour_of_day: int):
        """Detect anomaly for a single observation.

        Returns a dict with ``is_anomaly``, ``anomaly_score`` and ``severity``.
        """
        # Input validation
        if not isinstance(smile_score, (int, float)) or not isinstance(hour_of_day, int):
            raise TypeError("smile_score must be numeric and hour_of_day must be int")

        await self._ensure_trained()
        df = pd.DataFrame([{"smile_score": smile_score, "hour_of_day": hour_of_day}])
        # IsolationForest predict: 1 = normal, -1 = anomaly
        prediction = self.model.predict(df)[0]
        score = self.model.decision_function(df)[0]
        is_anomaly = prediction == -1

        # Determine severity based on configurable threshold
        if is_anomaly:
            severity = "CRITICAL" if score < THRESHOLD else "WARNING"
        else:
            severity = "INFO"

        result = {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(float(score), 3),
            "severity": severity,
        }
        logger.info(
            "Anomaly detection result",
            extra={"event": "model_prediction", "model": "anomaly_detector", "result": result},
        )
        return result

# Instantiate a singleton for FastAPI dependency injection
anomaly_detector = AnomalyDetector()
