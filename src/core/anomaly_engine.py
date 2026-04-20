"""
Anomaly Detection Engine - Identifies abnormal network behavior
Compares current traffic against baselines with severity classification
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from collections import deque


class Severity(Enum):
    """Anomaly severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyType(Enum):
    """Types of anomalies that can be detected"""
    TRAFFIC_SPIKE = "traffic_spike"
    TRAFFIC_DROP = "traffic_drop"
    DEVIATION = "deviation"


class AnomalyEngine:
    """
    Detects behavioral anomalies by comparing current metrics against baselines
    
    Detection logic:
    - Traffic > 2x baseline → MEDIUM
    - Traffic > 3x baseline → HIGH  
    - Traffic > 4x baseline → CRITICAL
    - Traffic < 0.3x baseline → LOW (potential failure)
    """
    
    # Thresholds for anomaly detection
    SPIKE_THRESHOLD_MEDIUM = 2.0   # 2x baseline
    SPIKE_THRESHOLD_HIGH = 3.0     # 3x baseline
    SPIKE_THRESHOLD_CRITICAL = 4.0 # 4x baseline
    DROP_THRESHOLD = 0.3           # 0.3x baseline (70% drop)
    
    def __init__(self, devices: Dict):
        """
        Initialize anomaly detection engine
        
        Args:
            devices: Dictionary of device objects (id -> Device)
        """
        self.devices = devices
        self.anomaly_history: List[Dict] = []
        self.baseline_history: Dict[str, deque] = {}  # Track baseline over time
        
        # Initialize baseline tracking
        for device_id in devices:
            self.baseline_history[device_id] = deque(maxlen=100)
    
    def detect_anomalies(self, current_metrics: Dict[str, Dict]) -> List[Dict]:
        """
        Detect anomalies in current telemetry data
        
        Args:
            current_metrics: Dictionary mapping device_id to metric data
                           (includes current, baseline, is_anomaly, anomaly_reason)
        
        Returns:
            List of anomaly dictionaries with full details
        """
        anomalies = []
        
        for device_id, metric_data in current_metrics.items():
            device = self.devices.get(device_id)
            if not device:
                continue
            
            current_traffic = metric_data['current']
            baseline = metric_data['baseline']
            telemetry_reason = metric_data.get('anomaly_reason')
            
            # Update baseline history
            self.baseline_history[device_id].append(current_traffic)
            
            # Detect anomalies
            anomaly = self._analyze_device(device, current_traffic, baseline, telemetry_reason)
            if anomaly:
                anomalies.append(anomaly)
                self.anomaly_history.append(anomaly)
        
        return anomalies
    
    def _analyze_device(self, device, current_traffic: float, baseline: float, telemetry_reason: str = None) -> Optional[Dict]:
        """
        Analyze single device for anomalies
        
        Returns:
            Anomaly dictionary or None if normal
        """
        # Calculate ratios
        spike_ratio = current_traffic / baseline if baseline > 0 else 0
        drop_ratio = current_traffic / baseline if baseline > 0 else 1.0
        
        # Determine anomaly type and severity
        if spike_ratio >= self.SPIKE_THRESHOLD_CRITICAL:
            severity = Severity.CRITICAL
            anomaly_type = AnomalyType.TRAFFIC_SPIKE
            description = f"Massive traffic spike - {spike_ratio:.1f}x baseline"
            short_reason = f"Critical: {spike_ratio:.0f}x spike"
            
        elif spike_ratio >= self.SPIKE_THRESHOLD_HIGH:
            severity = Severity.HIGH
            anomaly_type = AnomalyType.TRAFFIC_SPIKE
            description = f"High traffic spike - {spike_ratio:.1f}x baseline"
            short_reason = f"High: {spike_ratio:.0f}x spike"
            
        elif spike_ratio >= self.SPIKE_THRESHOLD_MEDIUM:
            severity = Severity.MEDIUM
            anomaly_type = AnomalyType.TRAFFIC_SPIKE
            description = f"Moderate traffic spike - {spike_ratio:.1f}x baseline"
            short_reason = f"Medium: {spike_ratio:.0f}x spike"
            
        elif drop_ratio <= self.DROP_THRESHOLD:
            severity = Severity.LOW
            anomaly_type = AnomalyType.TRAFFIC_DROP
            description = f"Traffic drop - device at {drop_ratio:.1%} of baseline"
            short_reason = f"Drop: {drop_ratio:.0%} of baseline"
            
        else:
            # No anomaly detected
            return None
        
        # Build anomaly object with full context
        anomaly = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'device_id': device.id,
            'device_name': device.name,
            'device_type': device.device_type.value if hasattr(device, 'device_type') else 'unknown',
            'layer': self._get_layer_value(device),
            'baseline_traffic': round(baseline, 2),
            'current_traffic': round(current_traffic, 2),
            'spike_ratio': round(spike_ratio, 2),
            'severity': severity.value,
            'anomaly_type': anomaly_type.value,
            'description': description,
            'short_reason': short_reason,  # NEW: Short reason for display
            'telemetry_reason': telemetry_reason,  # NEW: Reason from telemetry engine
            'recommendation': self._get_recommendation(severity, anomaly_type, device)
        }
        
        return anomaly
    
    def _get_layer_value(self, device) -> str:
        """Get layer value as string"""
        if hasattr(device, 'layer'):
            if hasattr(device.layer, 'value'):
                return device.layer.value
            return str(device.layer)
        return 'unknown'
    
    def _get_recommendation(self, severity: Severity, anomaly_type: AnomalyType, device) -> str:
        """Generate actionable recommendation based on anomaly"""
        
        if anomaly_type == AnomalyType.TRAFFIC_SPIKE:
            if severity == Severity.CRITICAL:
                return "URGENT: Investigate immediately - Possible DDoS attack or data breach"
            elif severity == Severity.HIGH:
                return "High priority: Check for malware, large file transfers, or misconfiguration"
            else:
                return "Review device logs and recent changes - Unexpected traffic increase"
        
        elif anomaly_type == AnomalyType.TRAFFIC_DROP:
            return "Check device connectivity - Possible failure, disconnect, or power issue"
        
        return "Monitor device behavior and review recent changes"
    
    def get_anomaly_summary(self) -> Dict:
        """Get summary of all detected anomalies"""
        if not self.anomaly_history:
            return {
                'total_anomalies': 0,
                'by_severity': {},
                'by_layer': {},
                'by_type': {},
                'recent': []
            }
        
        # Count by severity
        by_severity = {}
        by_layer = {}
        by_type = {}
        
        for anomaly in self.anomaly_history:
            severity = anomaly['severity']
            layer = anomaly['layer']
            atype = anomaly['anomaly_type']
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_layer[layer] = by_layer.get(layer, 0) + 1
            by_type[atype] = by_type.get(atype, 0) + 1
        
        return {
            'total_anomalies': len(self.anomaly_history),
            'by_severity': by_severity,
            'by_layer': by_layer,
            'by_type': by_type,
            'recent': self.anomaly_history[-10:]  # Last 10 anomalies
        }
    
    def print_anomalies(self, anomalies: List[Dict], limit: int = 20):
        """Pretty print detected anomalies with timestamps and short reasons"""
        if not anomalies:
            print("\n" + "=" * 80)
            print("✅ NO ANOMALIES DETECTED")
            print("=" * 80)
            print("\n   All devices operating within normal parameters")
            return
        
        print("\n" + "=" * 80)
        print(f"🚨 ANOMALIES DETECTED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        for i, anomaly in enumerate(anomalies[:limit], 1):
            # Severity icon
            severity_icon = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🔵'
            }.get(anomaly['severity'], '⚪')
            
            print(f"\n{severity_icon} Anomaly #{i}: {anomaly['device_name']} [{anomaly['short_reason']}]")
            print(f"   {'─' * 70}")
            print(f"   🕐 Timestamp:    {anomaly['timestamp']}")
            print(f"   📍 Layer:        {anomaly['layer'].upper()}")
            print(f"   📊 Type:         {anomaly['anomaly_type'].replace('_', ' ').title()}")
            print(f"   ⚠️  Severity:     {anomaly['severity'].upper()}")
            print(f"   📈 Baseline:     {anomaly['baseline_traffic']} pkts/sec")
            print(f"   📉 Current:      {anomaly['current_traffic']} pkts/sec")
            print(f"   🔥 Spike Ratio:  {anomaly['spike_ratio']}x baseline")
            print(f"   📝 Description:  {anomaly['description']}")
            
            # Show telemetry reason if available
            if anomaly.get('telemetry_reason'):
                print(f"   🔍 Root Cause:   {anomaly['telemetry_reason']}")
            
            print(f"   💡 Recommendation: {anomaly['recommendation']}")
        
        if len(anomalies) > limit:
            print(f"\n   ... and {len(anomalies) - limit} more anomalies")
    
    def get_layer_risk_assessment(self, anomalies: List[Dict]) -> Dict:
        """
        Assess risk per network layer based on anomalies
        
        Returns:
            Dictionary with risk scores per layer
        """
        risk_scores = {
            'edge': 0,
            'core': 0,
            'access': 0,
            'endpoint': 0
        }
        
        severity_weights = {
            'critical': 10,
            'high': 5,
            'medium': 2,
            'low': 1
        }
        
        for anomaly in anomalies:
            layer = anomaly['layer']
            severity = anomaly['severity']
            if layer in risk_scores:
                risk_scores[layer] += severity_weights.get(severity, 1)
        
        return risk_scores
    
    def get_statistical_analysis(self, device_id: str) -> Dict:
        """
        Get statistical analysis of device behavior over time
        
        Returns:
            Dictionary with statistics (mean, std, etc.)
        """
        history = list(self.baseline_history.get(device_id, []))
        
        if len(history) < 2:
            return {'error': 'Insufficient data for analysis'}
        
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        std_dev = variance ** 0.5
        
        return {
            'sample_size': len(history),
            'mean': round(mean, 2),
            'std_dev': round(std_dev, 2),
            'min': round(min(history), 2),
            'max': round(max(history), 2),
            'current': round(history[-1], 2) if history else 0,
            'is_stable': std_dev / mean < 0.3 if mean > 0 else False
        }