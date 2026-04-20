"""
Telemetry Engine - Simulates real-time network traffic monitoring
Generates realistic traffic patterns with optional anomalies
"""

import random
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class TrafficPattern(Enum):
    """Normal traffic variation patterns"""
    NORMAL = "normal"
    SPIKE = "spike"
    DROP = "drop"
    OSCILLATING = "oscillating"


class TelemetryEngine:
    """
    Simulates real-time network telemetry data
    Generates traffic metrics based on device baselines with realistic variations
    """
    
    def __init__(self, devices: Dict):
        """
        Initialize telemetry engine
        
        Args:
            devices: Dictionary of device objects (id -> Device)
        """
        self.devices = devices
        self.current_metrics: Dict[str, float] = {}
        self.metrics_history: Dict[str, List[float]] = {}
        self.timestamp = datetime.now()
        
    def generate_telemetry(self, inject_anomalies: bool = True, anomaly_rate: float = 0.1) -> Dict[str, float]:
        """
        Generate current traffic metrics for all devices
        
        Args:
            inject_anomalies: Whether to inject anomalous behavior
            anomaly_rate: Probability of anomaly per device (0.0 to 1.0)
        
        Returns:
            Dictionary mapping device_id to current traffic value
        """
        self.current_metrics = {}
        self.timestamp = datetime.now()
        
        for device_id, device in self.devices.items():
            baseline = device.baseline_traffic
            
            # Determine if this device should have anomaly
            is_anomaly = inject_anomalies and random.random() < anomaly_rate
            
            if is_anomaly:
                current, anomaly_reason = self._generate_anomalous_traffic(device)
            else:
                current, anomaly_reason = self._generate_normal_traffic(device)
            
            self.current_metrics[device_id] = {
                'current': round(current, 2),
                'baseline': round(baseline, 2),  # NORMALIZED baseline
                'is_anomaly': is_anomaly,
                'anomaly_reason': anomaly_reason if is_anomaly else None
            }
            
            # Store in history (keep last 100 values)
            if device_id not in self.metrics_history:
                self.metrics_history[device_id] = []
            self.metrics_history[device_id].append(current)
            if len(self.metrics_history[device_id]) > 100:
                self.metrics_history[device_id].pop(0)
        
        return self.current_metrics
    
    def _generate_normal_traffic(self, device) -> tuple:
        """
        Generate normal traffic pattern based on baseline
        
        Returns:
            (current_traffic, anomaly_reason) - anomaly_reason is None for normal
        """
        baseline = device.baseline_traffic
        
        # Choose random traffic pattern for realism
        pattern = random.choice(list(TrafficPattern))
        
        if pattern == TrafficPattern.NORMAL:
            # Standard variation: ±30%
            variation = random.uniform(0.7, 1.3)
            reason = None
            
        elif pattern == TrafficPattern.OSCILLATING:
            # Oscillating pattern (like business hours)
            hour_factor = 1.0
            if hasattr(self, 'timestamp'):
                # Simulate time-of-day effect
                hour = self.timestamp.hour
                if 9 <= hour <= 17:  # Business hours
                    hour_factor = random.uniform(1.1, 1.4)
                    reason = "Business hours traffic increase"
                elif 22 <= hour or hour <= 5:  # Night
                    hour_factor = random.uniform(0.3, 0.7)
                    reason = "Off-hours traffic reduction"
                else:
                    reason = None
            variation = random.uniform(0.6, 1.2) * hour_factor
            
        else:  # NORMAL fallback
            variation = random.uniform(0.7, 1.3)
            reason = None
        
        current = baseline * variation
        
        # Add small random noise
        noise = random.uniform(0.95, 1.05)
        current *= noise
        
        return current, reason
    
    def _generate_anomalous_traffic(self, device) -> tuple:
        """
        Generate anomalous traffic pattern with specific reasons
        
        Returns:
            (current_traffic, anomaly_reason)
        """
        baseline = device.baseline_traffic
        
        # Choose anomaly type
        anomaly_type = random.choice(['spike', 'drop', 'ramp', 'burst'])
        
        if anomaly_type == 'spike':
            # Sudden traffic increase (DDoS, data exfiltration)
            multiplier = random.uniform(2.5, 5.0)
            current = baseline * multiplier
            reason = f"Sudden traffic spike ({multiplier:.1f}x baseline) - Possible DDoS or data exfiltration"
            
        elif anomaly_type == 'drop':
            # Sudden traffic drop (device failure, disconnect)
            multiplier = random.uniform(0, 0.3)
            current = baseline * multiplier
            reason = f"Traffic drop to {multiplier:.0%} of baseline - Possible device failure or disconnect"
            
        elif anomaly_type == 'burst':
            # Short burst of high traffic
            multiplier = random.uniform(3.0, 6.0)
            current = baseline * multiplier
            reason = f"Traffic burst ({multiplier:.1f}x baseline) - Unusual communication pattern"
            
        else:  # ramp
            # Gradually increasing (slow attack, worm propagation)
            # Check history for trend
            history = self.metrics_history.get(device.id, [])
            if len(history) > 5:
                # Increase by 20-50% over previous value
                last_value = history[-1]
                current = last_value * random.uniform(1.2, 1.5)
                increase_pct = ((current - last_value) / last_value) * 100
                reason = f"Gradual traffic increase ({increase_pct:.0f}% rise) - Potential worm or slow attack"
            else:
                multiplier = random.uniform(1.5, 3.0)
                current = baseline * multiplier
                reason = f"Rapid traffic growth ({multiplier:.1f}x baseline) - Suspicious activity"
        
        return current, reason
    
    def get_device_metric(self, device_id: str) -> Optional[Dict]:
        """Get current metric for specific device"""
        return self.current_metrics.get(device_id)
    
    def get_metric_history(self, device_id: str, limit: int = 10) -> List[float]:
        """Get historical metrics for a device"""
        history = self.metrics_history.get(device_id, [])
        return history[-limit:] if history else []
    
    def get_layer_summary(self) -> Dict[str, Dict]:
        """
        Get telemetry summary by network layer
        
        Returns:
            Dictionary with layer statistics
        """
        layer_stats = {}
        
        for device_id, metric_data in self.current_metrics.items():
            device = self.devices.get(device_id)
            if not device or not hasattr(device, 'layer'):
                continue
            
            layer = device.layer.value if hasattr(device.layer, 'value') else str(device.layer)
            current = metric_data['current']
            
            if layer not in layer_stats:
                layer_stats[layer] = {
                    'total_devices': 0,
                    'total_traffic': 0,
                    'avg_traffic': 0,
                    'anomaly_count': 0,
                    'devices': []
                }
            
            layer_stats[layer]['total_devices'] += 1
            layer_stats[layer]['total_traffic'] += current
            if metric_data['is_anomaly']:
                layer_stats[layer]['anomaly_count'] += 1
            layer_stats[layer]['devices'].append({
                'name': device.name,
                'traffic': current,
                'baseline': metric_data['baseline'],
                'is_anomaly': metric_data['is_anomaly']
            })
        
        # Calculate averages
        for layer in layer_stats:
            if layer_stats[layer]['total_devices'] > 0:
                layer_stats[layer]['avg_traffic'] = round(
                    layer_stats[layer]['total_traffic'] / layer_stats[layer]['total_devices'], 2
                )
        
        return layer_stats
    
    def print_telemetry_sample(self, limit: int = 10):
        """Print sample telemetry data with normalized baselines"""
        print("\n" + "=" * 95)
        print(f"📊 CURRENT TELEMETRY SAMPLE - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 95)
        
        print(f"\n{'Device Name':<35} {'Layer':<12} {'Baseline':<12} {'Current':<12} {'Status':<12} {'Anomaly Reason'}")
        print("-" * 95)
        
        # Get first N devices
        devices_list = list(self.current_metrics.items())[:limit]
        
        for device_id, metric_data in devices_list:
            device = self.devices.get(device_id)
            if device:
                layer = device.layer.value if hasattr(device.layer, 'value') else str(device.layer)
                baseline = metric_data['baseline']  # Already rounded
                current = metric_data['current']
                
                # Determine status
                if metric_data['is_anomaly']:
                    status = "⚠️ ANOMALY"
                elif current > baseline * 1.3:
                    status = "🔺 HIGH"
                elif current < baseline * 0.5:
                    status = "🔻 LOW"
                else:
                    status = "✅ NORMAL"
                
                # Truncate reason if too long
                reason = metric_data.get('anomaly_reason', '')
                if reason and len(reason) > 40:
                    reason = reason[:37] + "..."
                
                print(f"{device.name:<35} {layer:<12} {baseline:<12} {current:<12} {status:<12} {reason}")
        
        # Show layer summary
        print("\n" + "-" * 95)
        print("📊 LAYER SUMMARY:")
        layer_stats = self.get_layer_summary()
        for layer, stats in layer_stats.items():
            anomaly_indicator = f" | {stats['anomaly_count']} anomalies" if stats['anomaly_count'] > 0 else ""
            print(f"   {layer.upper()}: {stats['total_devices']} devices | Avg Traffic: {stats['avg_traffic']} pkts/sec{anomaly_indicator}")
    
    def get_anomaly_candidates(self) -> List[tuple]:
        """
        Identify devices that might be anomalous (for detection engine)
        
        Returns:
            List of (device_id, current_traffic, baseline_traffic, anomaly_reason)
        """
        candidates = []
        
        for device_id, metric_data in self.current_metrics.items():
            if metric_data['is_anomaly']:
                device = self.devices.get(device_id)
                if device:
                    candidates.append((
                        device_id, 
                        metric_data['current'], 
                        metric_data['baseline'],
                        metric_data['anomaly_reason']
                    ))
        
        return candidates


class TelemetrySimulator:
    """
    Simulates continuous telemetry streaming over time
    Useful for testing anomaly detection over time windows
    """
    
    def __init__(self, devices: Dict, telemetry_engine: TelemetryEngine):
        self.devices = devices
        self.engine = telemetry_engine
        self.time_step = 0
        
    def simulate_time_window(self, steps: int = 10, anomaly_rate: float = 0.1) -> List[Dict]:
        """
        Simulate multiple time steps of telemetry
        
        Args:
            steps: Number of time steps to simulate
            anomaly_rate: Probability of anomaly per device per step
        
        Returns:
            List of telemetry snapshots
        """
        snapshots = []
        
        for step in range(steps):
            self.time_step = step
            telemetry = self.engine.generate_telemetry(
                inject_anomalies=True,
                anomaly_rate=anomaly_rate
            )
            snapshots.append({
                'step': step,
                'timestamp': self.engine.timestamp,
                'telemetry': telemetry.copy()
            })
        
        return snapshots