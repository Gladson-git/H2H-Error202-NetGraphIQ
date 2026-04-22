"""
Device Fingerprinting - Behavior-based device classification
Does not modify existing device models
"""

from typing import Dict, List
from enum import Enum


class DeviceCategory(Enum):
    CAMERA = "camera"
    SMART_DEVICE = "smart_device"
    SENSOR = "sensor"
    LOW_POWER_IOT = "low_power_iot"
    NETWORK_DEVICE = "network_device"


class DeviceFingerprinter:
    """
    Classifies devices based on baseline traffic behavior
    Adds intelligence without modifying existing models
    """
    
    # Classification thresholds
    CAMERA_THRESHOLD = 800
    SMART_DEVICE_THRESHOLD = 300
    SENSOR_THRESHOLD = 100
    
    def __init__(self, devices: Dict):
        self.devices = devices
        self.classifications: Dict[str, DeviceCategory] = {}
        self._classify_all()
    
    def _classify_all(self):
        """Classify all devices based on baseline traffic"""
        for device_id, device in self.devices.items():
            self.classifications[device_id] = self.classify_device(device.baseline_traffic)
    
    def classify_device(self, baseline_traffic: float) -> DeviceCategory:
        """
        Classify device type based on baseline traffic patterns
        
        Rules:
        - >800 → Camera (high bandwidth)
        - >300 → Smart Device (medium bandwidth)
        - >100 → Sensor (low bandwidth)
        - else → Low-power IoT (very low bandwidth)
        """
        if baseline_traffic > self.CAMERA_THRESHOLD:
            return DeviceCategory.CAMERA
        elif baseline_traffic > self.SMART_DEVICE_THRESHOLD:
            return DeviceCategory.SMART_DEVICE
        elif baseline_traffic > self.SENSOR_THRESHOLD:
            return DeviceCategory.SENSOR
        else:
            return DeviceCategory.LOW_POWER_IOT
    
    def get_category_insights(self) -> Dict:
        """Get distribution of device categories"""
        category_counts = {}
        for category in self.classifications.values():
            category_counts[category.value] = category_counts.get(category.value, 0) + 1
        return category_counts
    
    def get_anomaly_by_category(self, anomalies: List[Dict]) -> Dict:
        """
        Analyze anomalies by device category
        Helps understand which device types are most affected
        """
        category_anomalies = defaultdict(list)
        
        for anomaly in anomalies:
            device_id = anomaly.get('device_id')
            if device_id and device_id in self.classifications:
                category = self.classifications[device_id].value
                category_anomalies[category].append(anomaly)
        
        return dict(category_anomalies)
    
    def get_device_category(self, device_id: str) -> str:
        """Get category for a specific device"""
        if device_id in self.classifications:
            return self.classifications[device_id].value
        return "unknown"
    
    def get_category_risk_assessment(self, anomalies: List[Dict]) -> Dict:
        """
        Assess risk per device category based on anomalies
        """
        risk_scores = {
            'camera': 0,
            'smart_device': 0,
            'sensor': 0,
            'low_power_iot': 0,
            'network_device': 0
        }
        
        severity_weights = {
            'critical': 10,
            'high': 5,
            'medium': 2,
            'low': 1
        }
        
        for anomaly in anomalies:
            device_id = anomaly.get('device_id')
            if device_id in self.classifications:
                category = self.classifications[device_id].value
                severity = anomaly.get('severity', 'low')
                risk_scores[category] += severity_weights.get(severity, 1)
        
        return risk_scores