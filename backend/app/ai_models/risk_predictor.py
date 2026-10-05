import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

class ProductionRiskPredictor:
    def __init__(self):
        # In a real scenario, this would be loaded from a saved .model file.
        # Since we are starting fresh, we will initialize a basic model.
        self.model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
        self.is_trained = False
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(["LOW", "MEDIUM", "HIGH"])
        
    def _extract_features(self, df):
        """
        Expects a DataFrame with columns:
        avg_smile_score, sad_ratio, happy_ratio, active_workers, hour
        """
        features = ["avg_smile_score", "sad_ratio", "happy_ratio", "active_workers", "hour"]
        return df[features]

    def train_initial_model(self):
        """
        Trains a dummy baseline model so we have something working immediately.
        In production, replace this with a model trained on historical data.
        """
        # Create some synthetic baseline data
        data = {
            "avg_smile_score": [85, 90, 70, 45, 30, 20, 80, 50],
            "sad_ratio": [0.05, 0.02, 0.20, 0.40, 0.60, 0.80, 0.10, 0.30],
            "happy_ratio": [0.80, 0.90, 0.50, 0.20, 0.10, 0.05, 0.70, 0.30],
            "active_workers": [50, 50, 50, 50, 50, 50, 10, 10],
            "hour": [9, 10, 14, 16, 23, 2, 8, 15],
            "risk_level": ["LOW", "LOW", "MEDIUM", "HIGH", "HIGH", "HIGH", "LOW", "MEDIUM"]
        }
        df = pd.DataFrame(data)
        X = self._extract_features(df)
        y = self.label_encoder.transform(df["risk_level"])
        
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, avg_smile_score: float, sad_ratio: float, happy_ratio: float, active_workers: int, hour: int):
        if not self.is_trained:
            self.train_initial_model()
            
        df = pd.DataFrame([{
            "avg_smile_score": avg_smile_score,
            "sad_ratio": sad_ratio,
            "happy_ratio": happy_ratio,
            "active_workers": active_workers,
            "hour": hour
        }])
        
        X = self._extract_features(df)
        
        # Predict class
        pred_idx = self.model.predict(X)[0]
        predicted_risk = self.label_encoder.inverse_transform([pred_idx])[0]
        
        # Get probability (confidence)
        probs = self.model.predict_proba(X)[0]
        confidence = round(float(np.max(probs)) * 100, 1)
        
        return {
            "risk_level": predicted_risk,
            "confidence": confidence
        }

predictor = ProductionRiskPredictor()
