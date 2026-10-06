import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EmotionClassifier:
    """Baseline architecture for a real-time emotion classifier.
    
    This is currently marked as UNTRAINED. It serves as the architecture stub
    to plug in a real computer-vision or signal-based model later without
    rewriting the rest of the application.
    """
    
    def __init__(self):
        self.is_trained = False
        self.model_version = "baseline-untrained"
        
    async def classify(self, raw_features: Dict[str, Any]) -> str:
        """Classifies raw signals into HAPPY, OK, or SAD.
        
        Args:
            raw_features: dict containing raw signals (e.g., facial landmarks, 
                          heart rate variability, etc.)
                          
        Returns:
            str: "HAPPY", "OK", or "SAD"
        """
        if not self.is_trained:
            logger.warning("EmotionClassifier is currently UNTRAINED. Falling back to default.")
            return "OK"
            
        # Real model inference logic goes here in the future
        return "OK"

emotion_classifier = EmotionClassifier()
