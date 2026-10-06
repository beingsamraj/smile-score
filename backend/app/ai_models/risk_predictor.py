import os
import logging
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import asyncio
from sklearn.preprocessing import LabelEncoder

# Environment configuration
MODEL_PATH = os.getenv("RISK_MODEL_PATH", "backend/models/risk_predictor.joblib")
LABEL_ENCODER_PATH = os.getenv("RISK_LABEL_ENCODER_PATH", "backend/models/risk_label_encoder.joblib")

logger = logging.getLogger(__name__)

class ProductionRiskPredictor:
    """Production‑ready risk predictor using XGBoost.

    * Lazy loads a persisted model and label encoder if they exist.
    * Falls back to a synthetic baseline model when no trained model is present.
    * All public methods are guarded by an ``asyncio.Lock`` for thread safety.
    * Configurable via environment variables for model persistence paths.
    """

    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.is_trained = False
        self._lock = asyncio.Lock()
        self._load_or_initialize()

    def _load_or_initialize(self):
        """Attempt to load persisted XGBoost model and label encoder; otherwise create fresh instances.
        """
        try:
            if os.path.exists(MODEL_PATH) and os.path.exists(LABEL_ENCODER_PATH):
                self.model = joblib.load(MODEL_PATH)
                self.label_encoder = joblib.load(LABEL_ENCODER_PATH)
                self.is_trained = True
                logger.info(
                    "Risk predictor model loaded from disk",
                    extra={"event": "ml_model_loaded", "model": "risk_predictor", "path": MODEL_PATH},
                )
            else:
                raise FileNotFoundError
        except Exception as e:
            logger.warning(
                f"Failed to load persisted risk model ({e}); initializing fresh model",
                extra={"event": "ml_model_load_failed", "model": "risk_predictor"},
            )
            # Fresh untrained model & label encoder
            self.model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
            self.label_encoder = LabelEncoder()
            self.label_encoder.fit(["LOW", "MEDIUM", "HIGH"])  # deterministic order
            self.is_trained = False

    def _extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return the feature matrix in deterministic column order.
        Expected columns: avg_smile_score, sad_ratio, happy_ratio, active_workers, hour
        """
        required = ["avg_smile_score", "sad_ratio", "happy_ratio", "active_workers", "hour"]
        if not set(required).issubset(df.columns):
            raise ValueError(f"Missing required feature columns: {set(required) - set(df.columns)}")
        return df[required]

    async def _ensure_trained(self):
        """Train a minimal synthetic baseline if the model is not yet trained.
        This mirrors original behaviour but emits a warning.
        """
        if not self.is_trained:
            logger.warning(
                "Risk predictor used without real training data – training synthetic baseline",
                extra={"event": "ml_synthetic_training", "model": "risk_predictor"},
            )
            synthetic = pd.DataFrame({
                "avg_smile_score": [85, 90, 70, 45, 30, 20, 80, 50],
                "sad_ratio": [0.05, 0.02, 0.20, 0.40, 0.60, 0.80, 0.10, 0.30],
                "happy_ratio": [0.80, 0.90, 0.50, 0.20, 0.10, 0.05, 0.70, 0.30],
                "active_workers": [50, 50, 50, 50, 50, 50, 10, 10],
                "hour": [9, 10, 14, 16, 23, 2, 8, 15],
                "risk_level": ["LOW", "LOW", "MEDIUM", "HIGH", "HIGH", "HIGH", "LOW", "MEDIUM"],
            })
            X = self._extract_features(synthetic)
            y = self.label_encoder.transform(synthetic["risk_level"])
            self.model.fit(X, y)
            self.is_trained = True
            # Persist model and encoder
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, MODEL_PATH)
            joblib.dump(self.label_encoder, LABEL_ENCODER_PATH)
            logger.info(
                "Risk predictor synthetic model persisted",
                extra={"event": "ml_model_trained", "model": "risk_predictor", "path": MODEL_PATH},
            )

    async def train(self, df: pd.DataFrame, target_column: str = "risk_level"):
        """Train the predictor on real data.
        * ``df`` must contain the required feature columns plus the ``target_column``.
        * ``target_column`` values must be one of ``LOW``, ``MEDIUM``, ``HIGH``.
        """
        async with self._lock:
            if df.empty:
                raise ValueError("Training DataFrame is empty")
            X = self._extract_features(df)
            if target_column not in df.columns:
                raise ValueError(f"Target column '{target_column}' missing from training data")
            y_raw = df[target_column]
            if not set(y_raw.unique()).issubset({"LOW", "MEDIUM", "HIGH"}):
                raise ValueError("Target column contains invalid risk levels")
            y = self.label_encoder.transform(y_raw)
            self.model.fit(X, y)
            self.is_trained = True
            # Persist both model and encoder
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, MODEL_PATH)
            joblib.dump(self.label_encoder, LABEL_ENCODER_PATH)
            logger.info(
                "Risk predictor model trained on real data and persisted",
                extra={"event": "ml_model_trained", "model": "risk_predictor", "path": MODEL_PATH},
            )

    async def predict(self, avg_smile_score: float, sad_ratio: float, happy_ratio: float, active_workers: int, hour: int) -> dict:
        """Predict risk level and confidence.
        Returns ``{"risk_level": <str>, "confidence": <float>, "model_version": "v1"}``.
        """
        # Simple input validation
        for name, val in {
            "avg_smile_score": avg_smile_score,
            "sad_ratio": sad_ratio,
            "happy_ratio": happy_ratio,
            "active_workers": active_workers,
            "hour": hour,
        }.items():
            if val is None:
                raise ValueError(f"{name} must be provided")
        await self._ensure_trained()
        async with self._lock:
            df = pd.DataFrame([{"avg_smile_score": avg_smile_score,
                               "sad_ratio": sad_ratio,
                               "happy_ratio": happy_ratio,
                               "active_workers": active_workers,
                               "hour": hour}])
            X = self._extract_features(df)
            pred_idx = self.model.predict(X)[0]
            risk_level = self.label_encoder.inverse_transform([pred_idx])[0]
            probs = self.model.predict_proba(X)[0]
            confidence = round(float(np.max(probs)) * 100, 1)
            result = {"risk_level": risk_level, "confidence": confidence, "model_version": "v1"}
            logger.info(
                "Risk predictor produced prediction",
                extra={"event": "model_prediction", "model": "risk_predictor", "result": result},
            )
            return result

# Singleton instance for FastAPI
predictor = ProductionRiskPredictor()
