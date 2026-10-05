import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    def __init__(self):
        # We configure the Isolation Forest to expect ~5% anomalies
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_trained = False

    def train_initial_model(self):
        """
        Trains a baseline Isolation Forest.
        Features: ['smile_score', 'hour_of_day']
        """
        # Create some baseline synthetic data (normal days + a few anomalies)
        data = {
            "smile_score": [80, 82, 85, 78, 81, 79, 90, 83, 10, 80, 77, 85, 82, 20, 81],
            "hour_of_day": [9, 10, 11, 12, 13, 14, 15, 16, 17, 9, 10, 11, 12, 13, 14]
        }
        df = pd.DataFrame(data)
        self.model.fit(df)
        self.is_trained = True

    def detect_anomaly(self, smile_score: float, hour_of_day: int):
        if not self.is_trained:
            self.train_initial_model()
            
        df = pd.DataFrame([{
            "smile_score": smile_score,
            "hour_of_day": hour_of_day
        }])
        
        # predict returns 1 for normal, -1 for anomaly
        prediction = self.model.predict(df)[0]
        
        # decision_function gives an anomaly score. Lower (negative) means more anomalous.
        score = self.model.decision_function(df)[0]
        
        is_anomaly = (prediction == -1)
        
        severity = "INFO"
        if is_anomaly:
            if score < -0.15:
                severity = "CRITICAL"
            else:
                severity = "WARNING"
                
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(float(score), 3),
            "severity": severity
        }

anomaly_detector = AnomalyDetector()
