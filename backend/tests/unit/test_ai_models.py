import pytest
import pandas as pd
from app.ai_models.emotion_classifier import EmotionClassifier
from app.ai_models.multi_anomaly import MultiSignalAnomalyDetector

@pytest.mark.asyncio
async def test_emotion_classifier():
    classifier = EmotionClassifier()
    assert not classifier.is_trained
    res = await classifier.classify({"heart_rate": 80})
    assert res == "OK"  # Fallback

@pytest.mark.asyncio
async def test_multi_anomaly():
    detector = MultiSignalAnomalyDetector()
    assert not detector.is_trained
    df = pd.DataFrame({"temp": [22.0, 23.0], "vibration": [0.1, 0.2]})
    detector.train(df)
    assert detector.is_trained
    res = await detector.detect({"temp": 24.0, "vibration": 0.5})
    assert res is False  # Placeholder
