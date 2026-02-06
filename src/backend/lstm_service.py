"""
NetPulse - Professional LSTM Service Module
Hybrid ensemble model with confidence scoring and trend analysis
"""
import numpy as np
from collections import deque
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    from tensorflow.keras.models import load_model
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    
import joblib

logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Standardized prediction result"""
    model_name: str
    prediction_class: int
    confidence: float
    probabilities: List[float]
    timestamp: datetime

@dataclass
class TrendAnalysis:
    """LSTM trend analysis result"""
    current_risk: float  # 0.0 - 1.0
    trend_direction: str  # "stable", "rising", "falling"
    forecast_30min: float
    risk_chart: List[float]  # Son 12 ölçümün risk skorları
    recommendation: str

class LSTMPredictionService:
    """
    Professional LSTM Service with:
    - Rolling window management
    - Confidence scoring
    - Trend detection
    - Graceful degradation
    """
    
    def __init__(self, model_path: str, scaler_path: str, encoder_path: str, 
                 window_size: int = 12):
        self.window_size = window_size
        self.model = None
        self.scaler = None
        self.encoder = None
        self.is_available = False
        
        # In-memory cache for rolling windows
        self.measurement_cache: Dict[int, deque] = {}
        
        self._load_models(model_path, scaler_path, encoder_path)
    
    def _load_models(self, model_path: str, scaler_path: str, encoder_path: str):
        """Load LSTM model with error handling"""
        try:
            if not TENSORFLOW_AVAILABLE:
                logger.warning("TensorFlow not available. LSTM disabled.")
                return
                
            self.model = load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            self.encoder = joblib.load(encoder_path)
            self.is_available = True
            logger.info("✅ LSTM model loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ LSTM model load failed: {e}")
            self.is_available = False
    
    def add_measurement(self, subscriber_id: int, metrics: Dict[str, float]):
        """
        Add new measurement to rolling window
        
        Args:
            subscriber_id: Customer ID
            metrics: Dict with keys: latency_ms, packet_loss_ratio, 
                     snr_margin_db, download_usage_mbps
        """
        if subscriber_id not in self.measurement_cache:
            self.measurement_cache[subscriber_id] = deque(maxlen=self.window_size)
        
        # Extract features in correct order
        features = [
            metrics.get('latency_ms', 0),
            metrics.get('packet_loss_ratio', 0),
            metrics.get('snr_margin_db', 0),
            metrics.get('download_usage_mbps', 0)
        ]
        
        self.measurement_cache[subscriber_id].append(features)
    
    def predict(self, subscriber_id: int) -> Optional[PredictionResult]:
        """
        Make LSTM prediction if enough data available
        
        Returns:
            PredictionResult or None if not enough data
        """
        if not self.is_available:
            logger.warning("LSTM not available")
            return None
        
        if subscriber_id not in self.measurement_cache:
            logger.debug(f"No cache for subscriber {subscriber_id}")
            return None
        
        window = self.measurement_cache[subscriber_id]
        
        if len(window) < self.window_size:
            logger.debug(f"Not enough data: {len(window)}/{self.window_size}")
            return None
        
        try:
            # Prepare input
            X = np.array(list(window)).reshape(1, self.window_size, 4)
            X_scaled = self.scaler.transform(X.reshape(-1, 4)).reshape(1, self.window_size, 4)
            
            # Predict
            probs = self.model.predict(X_scaled, verbose=0)[0]
            pred_class = int(np.argmax(probs))
            confidence = float(np.max(probs))
            
            return PredictionResult(
                model_name="LSTM",
                prediction_class=pred_class,
                confidence=confidence,
                probabilities=probs.tolist(),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"LSTM prediction failed: {e}")
            return None
    
    def analyze_trend(self, subscriber_id: int) -> Optional[TrendAnalysis]:
        """
        Analyze trend from rolling window
        
        Returns:
            TrendAnalysis with risk assessment
        """
        result = self.predict(subscriber_id)
        if not result:
            return None
        
        window = list(self.measurement_cache[subscriber_id])
        
        # Calculate risk trend (simple: packet loss + latency composite)
        risk_scores = []
        for measurement in window:
            latency, packet_loss, snr, speed = measurement
            risk = (latency / 200.0) + (packet_loss / 10.0) + max(0, (10 - snr) / 10.0)
            risk_scores.append(min(1.0, risk))
        
        current_risk = risk_scores[-1] if risk_scores else 0.0
        
        # Trend detection
        if len(risk_scores) >= 6:
            recent_avg = np.mean(risk_scores[-3:])
            older_avg = np.mean(risk_scores[-6:-3])
            
            if recent_avg > older_avg * 1.2:
                trend = "rising"
            elif recent_avg < older_avg * 0.8:
                trend = "falling"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Forecast (simple linear extrapolation)
        if trend == "rising" and len(risk_scores) >= 3:
            slope = (risk_scores[-1] - risk_scores[-3]) / 2
            forecast_30min = min(1.0, risk_scores[-1] + slope * 6)
        else:
            forecast_30min = current_risk
        
        # Recommendation
        if forecast_30min > 0.7:
            recommendation = "🔴 Acil müdahale gerekli - 30 dk içinde kritik seviye"
        elif forecast_30min > 0.4:
            recommendation = "🟡 Proaktif müdahale önerilir - Trend kötüye gidiyor"
        elif trend == "rising":
            recommendation = "🟡 İzlemeye alınmalı - Risk artıyor"
        else:
            recommendation = "🟢 Durum stabil"
        
        return TrendAnalysis(
            current_risk=current_risk,
            trend_direction=trend,
            forecast_30min=forecast_30min,
            risk_chart=risk_scores,
            recommendation=recommendation
        )


class HybridEnsembleModel:
    """
    Combines Random Forest (snapshot) + LSTM (trend) predictions
    with confidence-weighted voting
    """
    
    def __init__(self, rf_weight: float = 0.6, lstm_weight: float = 0.4):
        self.rf_weight = rf_weight
        self.lstm_weight = lstm_weight
    
    def combine_predictions(
        self, 
        rf_result: Optional[PredictionResult],
        lstm_result: Optional[PredictionResult]
    ) -> Tuple[float, str, str]:
        """
        Ensemble logic with confidence weighting
        
        Returns:
            (risk_score, segment, reason)
        """
        
        # Case 1: Both models available
        if rf_result and lstm_result:
            # Normalize predictions to risk scores (0-1)
            rf_risk = rf_result.prediction_class / 3.0  # Classes: 0,1,2,3
            lstm_risk = lstm_result.prediction_class / 3.0
            
            # Weighted average
            final_risk = (
                rf_risk * rf_result.confidence * self.rf_weight +
                lstm_risk * lstm_result.confidence * self.lstm_weight
            )
            
            # Classification
            if final_risk > 0.6:
                segment = "RED"
                reason = f"Hem anlık hem trend kritik (RF:{rf_result.confidence:.2f}, LSTM:{lstm_result.confidence:.2f})"
            elif final_risk > 0.3:
                segment = "YELLOW"
                if lstm_risk > rf_risk:
                    reason = "LSTM artan trend tespit etti (Predictive Maintenance)"
                else:
                    reason = "Anlık metrikler riskli seviyede"
            else:
                segment = "GREEN"
                reason = "Her iki model de stabil durumu onayladı"
        
        # Case 2: Only RF available (LSTM failed)
        elif rf_result:
            final_risk = rf_result.prediction_class / 3.0
            segment = "RED" if final_risk > 0.6 else ("YELLOW" if final_risk > 0.3 else "GREEN")
            reason = "LSTM kullanılamadı, sadece anlık analiz (RF güven: {:.2f})".format(rf_result.confidence)
        
        # Case 3: Only LSTM available (unlikely)
        elif lstm_result:
            final_risk = lstm_result.prediction_class / 3.0
            segment = "RED" if final_risk > 0.6 else ("YELLOW" if final_risk > 0.3 else "GREEN")
            reason = "Sadece trend analizi mevcut"
        
        # Case 4: Both failed
        else:
            final_risk = 0.0
            segment = "GREEN"
            reason = "⚠️ Model tahminleri kullanılamadı, varsayılan durum"
        
        return final_risk, segment, reason


# Global service instances (initialized in main.py)
lstm_service: Optional[LSTMPredictionService] = None
hybrid_model: Optional[HybridEnsembleModel] = None
