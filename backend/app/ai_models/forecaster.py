import pandas as pd
from datetime import datetime, timedelta

class SmileForecaster:
    def __init__(self):
        self.is_trained = False
        self.model = None

    def _lazy_init(self):
        """Lazy load Prophet to save startup time if not needed immediately"""
        if self.model is None:
            from prophet import Prophet
            self.model = Prophet(daily_seasonality=True, yearly_seasonality=False, weekly_seasonality=False)

    def train_model(self, historical_data):
        """
        historical_data should be a list of dicts: [{'timestamp': '2023-01-01T10:00:00', 'smile_score': 85}]
        Prophet expects 'ds' (datestamp) and 'y' (value).
        """
        self._lazy_init()
        df = pd.DataFrame(historical_data)
        
        if df.empty or len(df) < 2:
            return False # Not enough data
            
        df = df.rename(columns={'timestamp': 'ds', 'smile_score': 'y'})
        df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None) # Prophet doesn't like tz-aware
        
        self.model.fit(df)
        self.is_trained = True
        return True

    def forecast_next_n_hours(self, hours: int = 4):
        """Returns predictions for the next N hours."""
        if not self.is_trained:
            # Fallback if no data: just predict a flat line of 50
            now = datetime.now()
            return [{"timestamp": (now + timedelta(hours=i)).isoformat(), "smile_score": 50.0} for i in range(1, hours+1)]
            
        future = self.model.make_future_dataframe(periods=hours, freq='H')
        forecast = self.model.predict(future)
        
        # Get only the future predictions (tail)
        future_forecast = forecast.tail(hours)
        
        results = []
        for _, row in future_forecast.iterrows():
            results.append({
                "timestamp": row['ds'].isoformat() + "Z", # naive to fake UTC
                "smile_score": round(max(0, min(100, float(row['yhat']))), 1) # cap between 0-100
            })
            
        return results

forecaster = SmileForecaster()
