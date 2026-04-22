"""
Machine Learning Anomaly Detection - Isolation Forest
Separate module that does NOT replace rule-based detection
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class MLAnomalyDetector:
    """
    Isolation Forest based anomaly detection
    Works alongside rule-based detection
    """
    
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.is_trained = False
        self.training_data = []
    
    def train(self, telemetry_data: Dict[str, Dict]):
        """
        Train Isolation Forest on historical telemetry
        """
        features = []
        for device_id, data in telemetry_data.items():
            features.append([
                data.get('baseline', 0),
                data.get('current', 0)
            ])
        
        if len(features) > 10:
            X = np.array(features)
            self.model.fit(X)
            self.is_trained = True
            self.training_data = features
    
    def detect_anomalies(self, current_metrics: Dict[str, Dict]) -> List[Dict]:
        """
        Detect anomalies using Isolation Forest
        
        Returns:
            List of anomalous devices with ML-specific info
        """
        if not self.is_trained:
            return []
        
        anomalies = []
        
        for device_id, data in current_metrics.items():
            features = np.array([[data.get('baseline', 0), data.get('current', 0)]])
            prediction = self.model.predict(features)
            
            if prediction[0] == -1:  # Anomaly detected by ML
                anomaly_score = self.model.score_samples(features)[0]
                anomalies.append({
                    'device_id': device_id,
                    'device_name': data.get('device_name', device_id),
                    'baseline': data.get('baseline', 0),
                    'current': data.get('current', 0),
                    'anomaly_score': float(anomaly_score),
                    'detection_method': 'Isolation Forest'
                })
        
        return anomalies
    
    def incremental_train(self, new_data: Dict[str, Dict]):
        """
        Incrementally update training
        """
        features = []
        for device_id, data in new_data.items():
            features.append([
                data.get('baseline', 0),
                data.get('current', 0)
            ])
        
        if features:
            self.training_data.extend(features)
            if len(self.training_data) > 10:
                X = np.array(self.training_data[-500:])
                self.model.fit(X)