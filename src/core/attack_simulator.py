"""
Attack Simulator - Simulates various cyber-attack scenarios
This is a NEW module that extends functionality without modifying existing code
"""

import random
from typing import Dict
from enum import Enum


class AttackType(Enum):
    """Types of attacks that can be simulated"""
    DDOS = "ddos"
    MAC_SPOOFING = "mac_spoofing"
    DEVICE_FAILURE = "device_failure"
    NONE = "none"


class AttackSimulator:
    """
    Simulates real-world attack behavior on the network
    Can be optionally enabled without affecting default behavior
    """
    
    def __init__(self, devices: Dict):
        """
        Initialize attack simulator
        
        Args:
            devices: Dictionary of device objects (id -> Device)
        """
        self.devices = devices
        self.active_attack = AttackType.NONE
        self.attack_history = []
    
    def apply_attack(self, attack_type: AttackType, metrics: Dict, 
                     simulate_attack: bool = False) -> Dict:
        """
        Apply attack simulation to telemetry metrics
        
        Args:
            attack_type: Type of attack to simulate
            metrics: Current telemetry metrics
            simulate_attack: Flag to enable/disable (default False)
        
        Returns:
            Modified metrics with attack effects (or unchanged if simulate_attack=False)
        """
        # Default behavior: no modification
        if not simulate_attack:
            return metrics
        
        self.active_attack = attack_type
        
        if attack_type == AttackType.DDOS:
            return self._simulate_ddos(metrics)
        elif attack_type == AttackType.MAC_SPOOFING:
            return self._simulate_mac_spoofing(metrics)
        elif attack_type == AttackType.DEVICE_FAILURE:
            return self._simulate_device_failure(metrics)
        
        return metrics
    
    def _simulate_ddos(self, metrics: Dict) -> Dict:
        """
        Simulate DDoS attack:
        - Multiple devices affected
        - High traffic spikes (3-6x)
        """
        affected_count = random.randint(3, 8)
        device_ids = list(metrics.keys())
        affected = random.sample(device_ids, min(affected_count, len(device_ids)))
        
        for device_id in affected:
            if device_id in metrics:
                current = metrics[device_id].get('current', 0)
                multiplier = random.uniform(3, 6)
                metrics[device_id]['current'] = round(current * multiplier, 2)
                metrics[device_id]['is_anomaly'] = True
                metrics[device_id]['anomaly_reason'] = f"DDoS Attack: {multiplier:.1f}x traffic spike"
        
        self.attack_history.append({
            'type': 'ddos',
            'affected_devices': len(affected),
            'timestamp': 'now'
        })
        
        return metrics
    
    def _simulate_mac_spoofing(self, metrics: Dict) -> Dict:
        """
        Simulate MAC Spoofing attack:
        - Single device affected
        - Suspicious behavior detected
        """
        device_ids = list(metrics.keys())
        if device_ids:
            target = random.choice(device_ids)
            if target in metrics:
                metrics[target]['is_anomaly'] = True
                metrics[target]['anomaly_reason'] = "MAC Spoofing: Suspicious MAC address detected"
                current = metrics[target].get('current', 0)
                metrics[target]['current'] = round(current * 1.5, 2)
        
        return metrics
    
    def _simulate_device_failure(self, metrics: Dict) -> Dict:
        """
        Simulate Device Failure:
        - Single device goes offline
        - Traffic drops to zero
        """
        device_ids = list(metrics.keys())
        if device_ids:
            target = random.choice(device_ids)
            if target in metrics:
                metrics[target]['current'] = 0
                metrics[target]['is_anomaly'] = True
                metrics[target]['anomaly_reason'] = "Device Failure: Device is offline"
        
        return metrics
    
    def get_attack_description(self) -> str:
        """Get description of active attack"""
        descriptions = {
            AttackType.DDOS: "DDoS Attack: High-volume traffic spikes affecting multiple devices",
            AttackType.MAC_SPOOFING: "MAC Spoofing: Suspicious MAC address impersonation detected",
            AttackType.DEVICE_FAILURE: "Device Failure: Critical device has gone offline",
            AttackType.NONE: "No active attack simulation"
        }
        return descriptions.get(self.active_attack, "Unknown attack type")
    
    def reset_attack(self):
        """Reset attack simulation"""
        self.active_attack = AttackType.NONE