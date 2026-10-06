import os
import logging
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import joblib

# Environment configuration
MODEL_PATH = os.getenv("FORECASTER_MODEL_PATH", "backend/models/forecaster.joblib")

logger = logging.getLogger(__name__)

class SmileForecaster:
    """Production‑ready time‑series forecaster using Prophet.

    * Lazy loads Prophet only when needed.
    * Persists the trained model to disk and reloads on startup.
    * Validates historical data (timestamps, duplicates, missing values).
    * Thread‑safe via ``asyncio.Lock``.
    """

    def __init__(self):
        self.model = None
        self.is_trained = False
        self._lock = asyncio.Lock()
        self._load_or_initialize()

    def _load_or_initialize(self):
        """Load a persisted Prophet model if present; otherwise keep ``self.model`` = ``None``.
        """
        try:
            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                self.is_trained = True
                logger.info(
                    "Forecaster model loaded from disk",
                    extra={"event": "ml_model_loaded", "model": "forecaster", "path": MODEL_PATH},
                )
            else:
                logger.info(
                    "Forecaster model file not found – will initialize on first training",
                    extra={"event": "ml_model_missing", "model": "forecaster"},
                )
        except Exception as e:
            logger.warning(
                f"Failed to load persisted forecaster model ({e}) – will re‑initialize",
                extra={"event": "ml_model_load_failed", "model": "forecaster"},
            )
            self.model = None
            self.is_trained = False

    def _lazy_init(self):
        """Import Prophet lazily to avoid heavy import at startup.
        """
        if self.model is None:
            from prophet import Prophet
            self.model = Prophet(daily_seasonality=True, yearly_seasonality=False, weekly_seasonality=False)

    def _validate_historical(self, data: list) -> pd.DataFrame:
        """Validate and clean historical data.
        Expected format: ``[{"timestamp": "...", "smile_score": <float>}...]``.
        Returns a pandas DataFrame with columns ``ds`` (datetime) and ``y`` (float).
        """
        if not isinstance(data, list) or len(data) == 0:
            raise ValueError("Historical data must be a non‑empty list of dicts.")
        df = pd.DataFrame(data)
        if not {'timestamp', 'smile_score'}.issubset(df.columns):
            raise ValueError("Each record must contain 'timestamp' and 'smile_score'.")
        # Convert timestamps, drop NaNs, sort, remove duplicates
        df['ds'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['ds', 'smile_score'])
        df = df.drop_duplicates(subset='ds')
        df = df.sort_values('ds')
        df = df.rename(columns={'smile_score': 'y'})
        df = df[['ds', 'y']]
        if len(df) < 2:
            raise ValueError("At least two valid observations are required for training.")
        return df

    async def train(self, historical_data: list):
        """Train (or re‑train) the Prophet model on supplied historical data.
        """
        async with self._lock:
            df = self._validate_historical(historical_data)
            self._lazy_init()
            self.model.fit(df)
            self.is_trained = True
            # Persist model
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump(self.model, MODEL_PATH)
            logger.info(
                "Forecaster model trained and persisted",
                extra={"event": "ml_model_trained", "model": "forecaster", "path": MODEL_PATH},
            )

    async def forecast_next_n_hours(self, hours: int = 4) -> list:
        """Return a list of forecasts for the next *hours* hours.
        Each element: ``{"timestamp": <ISO‑string>, "smile_score": <float>}``.
        """
        async with self._lock:
            if not self.is_trained:
                # Return a deterministic fallback when no model is available
                now = datetime.now()
                logger.warning(
                    "Forecaster requested without a trained model – returning flat fallback",
                    extra={"event": "ml_fallback", "model": "forecaster"},
                )
                return [
                    {"timestamp": (now + timedelta(hours=i)).isoformat(), "smile_score": 50.0}
                    for i in range(1, hours + 1)
                ]
            # Create future dataframe and generate forecast
            future = self.model.make_future_dataframe(periods=hours, freq='H')
            forecast = self.model.predict(future)
            future_forecast = forecast.tail(hours)
            results = []
            for _, row in future_forecast.iterrows():
                results.append({
                    "timestamp": row['ds'].isoformat() + "Z",  # naive UTC marker
                    "smile_score": round(max(0, min(100, float(row['yhat']))), 1),
                })
            logger.info(
                "Forecaster produced forecast",
                extra={"event": "model_prediction", "model": "forecaster", "hours": hours},
            )
            return results

# Singleton instance for FastAPI dependency injection
forecaster = SmileForecaster()
