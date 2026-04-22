"""
Graph Neural Network for Topology-Aware Anomaly Detection
FIXED: Now detects anomalies based on spike ratio + neighbor influence
"""

import numpy as np
from typing import Dict, List, Tuple, Set
import networkx as nx
from collections import defaultdict


class SimpleGNN:
    """
    Lightweight Graph Neural Network for anomaly detection
    Uses spike ratio and neighbor influence detection
    """
    
    def __init__(self, spike_threshold: float = 1.5, neighbor_threshold: float = 1.2):
        """
        Initialize GNN with detection thresholds
        
        Args:
            spike_threshold: Minimum spike ratio to consider device anomalous
            neighbor_threshold: Minimum average neighbor spike to consider propagation
        """
        self.spike_threshold = spike_threshold
        self.neighbor_threshold = neighbor_threshold
        self.anomaly_history = []
    
    def compute_spike_ratio(self, current: float, baseline: float) -> float:
        """Calculate spike ratio (current / baseline)"""
        if baseline == 0:
            return 1.0
        return current / baseline
    
    def get_neighbor_avg_spike(self, device_id: str, graph: nx.Graph, 
                                spike_ratios: Dict[str, float]) -> float:
        """
        Calculate average spike ratio of neighboring devices
        
        This captures anomaly propagation through the network
        """
        if not graph.has_node(device_id):
            return 1.0
        
        neighbors = list(graph.neighbors(device_id))
        if not neighbors:
            return 1.0
        
        neighbor_spikes = []
        for neighbor in neighbors:
            if neighbor in spike_ratios:
                neighbor_spikes.append(spike_ratios[neighbor])
        
        if not neighbor_spikes:
            return 1.0
        
        return np.mean(neighbor_spikes)
    
    def detect_anomalies(self, graph: nx.Graph, devices: Dict,
                         current_metrics: Dict) -> List[Dict]:
        """
        Detect anomalies using GNN logic:
        - Device has high spike ratio
        - AND neighbors also show elevated activity (propagation)
        
        This captures attack propagation patterns through the network
        """
        if not graph or graph.number_of_nodes() == 0:
            return []
        
        anomalies = []
        
        # First, compute spike ratios for all devices
        spike_ratios = {}
        for device_id in graph.nodes():
            device = devices.get(device_id)
            if not device:
                continue
            
            current = current_metrics.get(device_id, {}).get('current', device.baseline_traffic)
            baseline = device.baseline_traffic
            
            spike_ratio = self.compute_spike_ratio(current, baseline)
            spike_ratios[device_id] = spike_ratio
        
        # Now detect anomalies based on spike ratio + neighbor influence
        for device_id in graph.nodes():
            spike_ratio = spike_ratios.get(device_id, 1.0)
            
            # Skip if spike ratio is below threshold
            if spike_ratio < self.spike_threshold:
                continue
            
            # Get average neighbor spike ratio
            neighbor_avg = self.get_neighbor_avg_spike(device_id, graph, spike_ratios)
            
            # Check if neighbor influence indicates propagation
            if neighbor_avg >= self.neighbor_threshold:
                device = devices.get(device_id)
                
                # Determine severity based on spike ratio
                if spike_ratio >= 4.0:
                    severity = "CRITICAL"
                elif spike_ratio >= 3.0:
                    severity = "HIGH"
                elif spike_ratio >= 2.0:
                    severity = "MEDIUM"
                else:
                    severity = "LOW"
                
                # Generate explanation
                reason = self._generate_reason(spike_ratio, neighbor_avg)
                
                anomalies.append({
                    'device_id': device_id,
                    'device_name': device.name if device else device_id,
                    'layer': device.layer.value if device and hasattr(device, 'layer') else 'unknown',
                    'spike_ratio': round(spike_ratio, 2),
                    'neighbor_avg_spike': round(neighbor_avg, 2),
                    'severity': severity,
                    'detection_method': 'GNN',
                    'reason': reason,
                    'gnn_score': round((spike_ratio + neighbor_avg) / 2, 3)
                })
        
        self.anomaly_history.extend(anomalies)
        return anomalies
    
    def _generate_reason(self, spike_ratio: float, neighbor_avg: float) -> str:
        """Generate human-readable explanation for GNN detection"""
        return f"High spike ({spike_ratio:.1f}x) + neighbors elevated ({neighbor_avg:.1f}x) - Possible attack propagation"


class GNNAnomalyDetector:
    """
    Wrapper for GNN anomaly detection
    Integrates with existing system without breaking anything
    """
    
    def __init__(self, spike_threshold: float = 1.5, neighbor_threshold: float = 1.2):
        self.gnn = SimpleGNN(spike_threshold, neighbor_threshold)
        self.anomaly_history = []
    
    def detect(self, graph: nx.Graph, devices: Dict,
               current_metrics: Dict) -> List[Dict]:
        """
        Detect anomalies using GNN
        Returns list of anomalies with GNN-specific information
        """
        if not graph or graph.number_of_nodes() == 0:
            return []
        
        anomalies = self.gnn.detect_anomalies(graph, devices, current_metrics)
        self.anomaly_history.extend(anomalies)
        
        return anomalies
    
    def get_gnn_summary(self) -> Dict:
        """Get summary of GNN detections"""
        if not self.anomaly_history:
            return {'total_gnn_anomalies': 0}
        
        return {
            'total_gnn_anomalies': len(self.anomaly_history),
            'recent': self.anomaly_history[-5:]
        }