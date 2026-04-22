"""
NetGraphIQ - Complete Integrated Dashboard
Combines existing features with ML, GNN, Fingerprinting, and Attack Simulation
All existing functionality preserved - new features added as extensions
"""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
from datetime import datetime
import random
import time
import sys
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network_generator import NetworkGenerator
from src.core.telemetry_engine import TelemetryEngine
from src.core.anomaly_engine import AnomalyEngine

# NEW IMPORTS - Added without breaking existing code
from src.storage.telemetry_storage import TelemetryStorage
from src.ml.ml_anomaly import MLAnomalyDetector
from src.ml.gnn_model import GNNAnomalyDetector
from src.fingerprint.device_fingerprint import DeviceFingerprinter
from src.core.attack_simulator import AttackSimulator, AttackType


class PacketFlowSimulator:
    """Simulates live packet flow through the network with enhanced visualization"""
    
    def __init__(self, graph: nx.Graph, anomaly_ids: set = None):
        self.graph = graph
        self.anomaly_ids = anomaly_ids or set()
        self.active_edges = {}
        self.edge_flow_count = {}
        self.flow_counter = 0
        self.packet_positions = {}
        self.flow_history = []
        
        for edge in self.graph.edges():
            self.edge_flow_count[edge] = 0
            self.edge_flow_count[(edge[1], edge[0])] = 0
    
    def update_flows(self, attack_mode: bool = False):
        """Update active packet flows with enhanced simulation"""
        if not self.graph or self.graph.number_of_edges() == 0:
            return
        
        num_flows = random.randint(5, 12) if attack_mode else random.randint(3, 8)
        
        for _ in range(num_flows):
            edge = random.choice(list(self.graph.edges()))
            
            self.edge_flow_count[edge] = self.edge_flow_count.get(edge, 0) + 1
            self.flow_counter += 1
            
            is_anomaly_edge = (edge[0] in self.anomaly_ids or edge[1] in self.anomaly_ids)
            
            if is_anomaly_edge:
                intensity = random.uniform(0.8, 1.0)
                duration = 0.8 if attack_mode else 0.6
                packet_size = random.randint(100, 500)
            else:
                intensity = random.uniform(0.3, 0.7)
                duration = 0.4 if attack_mode else 0.3
                packet_size = random.randint(50, 200)
            
            self.active_edges[edge] = {
                'intensity': intensity,
                'start_time': time.time(),
                'duration': duration,
                'packet_size': packet_size,
                'flow_id': self.flow_counter
            }
            
            self.packet_positions[self.flow_counter] = {
                'edge': edge,
                'progress': 0.0,
                'speed': random.uniform(0.5, 1.5)
            }
        
        current_time = time.time()
        expired = []
        
        for flow_id, flow_data in self.active_edges.items():
            if current_time - flow_data['start_time'] >= flow_data['duration']:
                expired.append(flow_id)
        
        for edge in expired:
            del self.active_edges[edge]
            to_remove = [fid for fid, pos in self.packet_positions.items() 
                        if pos['edge'] == edge]
            for fid in to_remove:
                del self.packet_positions[fid]
        
        for flow_id, pos in self.packet_positions.items():
            pos['progress'] += pos['speed'] * 0.05
            if pos['progress'] >= 1.0:
                pos['progress'] = 0.0
    
    def get_edge_style(self, edge: Tuple) -> Tuple[str, float, float, int]:
        """Get edge style based on active flows and anomalies"""
        if edge in self.active_edges or (edge[1], edge[0]) in self.active_edges:
            flow_count = self.edge_flow_count.get(edge, 0)
            
            if flow_count > 10:
                return '#FF4500', 5.0, 0.95, flow_count
            elif flow_count > 5:
                return '#FF8C00', 4.0, 0.9, flow_count
            else:
                return '#FFA500', 3.5, 0.85, flow_count
        
        if edge[0] in self.anomaly_ids or edge[1] in self.anomaly_ids:
            return '#E74C3C', 2.5, 0.8, 0
        
        return '#95A5A6', 1.2, 0.5, 0
    
    def get_flow_statistics(self) -> Dict:
        return {
            'total_flows': self.flow_counter,
            'active_flows': len(self.active_edges),
            'animated_packets': len(self.packet_positions),
            'most_active_edge': max(self.edge_flow_count.items(), key=lambda x: x[1])[0] if self.edge_flow_count else None,
            'total_packets': sum(self.edge_flow_count.values())
        }


class IntegratedDashboard:
    """Complete integrated dashboard with all features preserved and enhanced"""
    
    def __init__(self):
        self._init_session_state()
    
    def _init_session_state(self):
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            
            # Existing state
            st.session_state.devices = None
            st.session_state.connections = None
            st.session_state.anomalies = []
            st.session_state.telemetry = None
            st.session_state.anomaly_engine = None
            st.session_state.graph = None
            st.session_state.packet_simulator = None
            st.session_state.network_generated = False
            st.session_state.attack_mode = False
            st.session_state.last_update = datetime.now()
            st.session_state.root_cause = None
            
            # NEW state for enhanced features
            st.session_state.storage = None
            st.session_state.ml_detector = None
            st.session_state.gnn_detector = None
            st.session_state.fingerprinter = None
            st.session_state.attack_sim = None
            st.session_state.ml_anomalies = []
            st.session_state.gnn_anomalies = []
            st.session_state.simulate_attack = False
            st.session_state.attack_type = AttackType.NONE
    
    def generate_network(self):
        """Generate complete network topology with all components"""
        with st.spinner("🌐 Generating enterprise network topology..."):
            generator = NetworkGenerator()
            devices, connections = generator.generate_enterprise_network()
            
            # Build graph
            graph = nx.Graph()
            for device_id, device in devices.items():
                layer_value = device.layer.value if hasattr(device, 'layer') else 'unknown'
                graph.add_node(
                    device_id,
                    name=device.name,
                    type=device.device_type.value,
                    layer=layer_value
                )
            for conn in connections:
                graph.add_edge(conn.source_id, conn.target_id)
            
            # Initialize existing engines
            telemetry = TelemetryEngine(devices)
            anomaly_engine = AnomalyEngine(devices)
            packet_simulator = PacketFlowSimulator(graph, set())
            
            # Initialize NEW components
            storage = TelemetryStorage()
            ml_detector = MLAnomalyDetector()
            gnn_detector = GNNAnomalyDetector()
            fingerprinter = DeviceFingerprinter(devices)
            attack_sim = AttackSimulator(devices)
            
            # Train ML detector with initial data
            initial_metrics = telemetry.generate_telemetry(inject_anomalies=False, anomaly_rate=0)
            ml_detector.train(initial_metrics)
            
            st.session_state.devices = devices
            st.session_state.connections = connections
            st.session_state.graph = graph
            st.session_state.telemetry = telemetry
            st.session_state.anomaly_engine = anomaly_engine
            st.session_state.packet_simulator = packet_simulator
            st.session_state.storage = storage
            st.session_state.ml_detector = ml_detector
            st.session_state.gnn_detector = gnn_detector
            st.session_state.fingerprinter = fingerprinter
            st.session_state.attack_sim = attack_sim
            st.session_state.network_generated = True
            
            return True
        return False
    
    def update_network_state(self, attack_mode: bool):
        """Update telemetry and detect anomalies using ALL methods"""
        if not st.session_state.devices:
            return
        
        # Adjust anomaly rate based on attack mode
        anomaly_rate = 0.30 if attack_mode else 0.12
        
        # Generate telemetry
        current_metrics = st.session_state.telemetry.generate_telemetry(
            inject_anomalies=True,
            anomaly_rate=anomaly_rate
        )
        
        # Apply attack if enabled
        if st.session_state.simulate_attack:
            current_metrics = st.session_state.attack_sim.apply_attack(
                st.session_state.attack_type, current_metrics, simulate_attack=True
            )
        
        # EXISTING: Rule-based anomalies
        rule_anomalies = st.session_state.anomaly_engine.detect_anomalies(current_metrics)
        
        # NEW: ML anomalies (Isolation Forest)
        ml_anomalies = st.session_state.ml_detector.detect_anomalies(current_metrics)
        
        # NEW: GNN anomalies (Graph Neural Network) - FIXED VERSION
        gnn_anomalies = st.session_state.gnn_detector.detect(
            st.session_state.graph, st.session_state.devices, current_metrics
        )
        
        # Store telemetry to CSV (NEW)
        for device_id, data in current_metrics.items():
            device = st.session_state.devices.get(device_id)
            if device:
                st.session_state.storage.save_telemetry(
                    device_id, device.name,
                    data['baseline'], data['current'],
                    data['is_anomaly']
                )
        
        # Update packet simulator with anomaly IDs (from all detection methods)
        all_anomaly_ids = set()
        for a in rule_anomalies:
            all_anomaly_ids.add(a['device_id'])
        for a in ml_anomalies:
            all_anomaly_ids.add(a['device_id'])
        for a in gnn_anomalies:
            all_anomaly_ids.add(a['device_id'])
        
        st.session_state.packet_simulator.anomaly_ids = all_anomaly_ids
        
        # Store all anomalies
        st.session_state.anomalies = rule_anomalies
        st.session_state.ml_anomalies = ml_anomalies
        st.session_state.gnn_anomalies = gnn_anomalies
        
        # Find root cause using rule-based anomalies (existing logic)
        if st.session_state.graph and rule_anomalies:
            st.session_state.root_cause = st.session_state.anomaly_engine.find_root_cause(
                rule_anomalies, st.session_state.graph
            )
        else:
            st.session_state.root_cause = None
        
        st.session_state.last_update = datetime.now()
        st.session_state.attack_mode = attack_mode
        
        return rule_anomalies, ml_anomalies, gnn_anomalies
    
    def draw_network_graph(self):
        """Draw network topology with anomaly highlighting (preserved from original)"""
        if not st.session_state.graph:
            return None
        
        fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
        pos = nx.spring_layout(st.session_state.graph, k=2, iterations=50, seed=42)
        
        # Get all anomaly IDs from all detection methods
        rule_anomaly_ids = {a['device_id'] for a in st.session_state.anomalies}
        ml_anomaly_ids = {a['device_id'] for a in st.session_state.ml_anomalies}
        gnn_anomaly_ids = {a['device_id'] for a in st.session_state.gnn_anomalies}
        
        # Draw edges with styles based on packet flow
        for edge in st.session_state.graph.edges():
            color, width, alpha, flow_count = st.session_state.packet_simulator.get_edge_style(edge)
            
            if flow_count > 5:
                nx.draw_networkx_edges(
                    st.session_state.graph, pos,
                    edgelist=[edge],
                    edge_color=color,
                    width=width + 2,
                    alpha=0.3,
                    ax=ax
                )
            
            nx.draw_networkx_edges(
                st.session_state.graph, pos,
                edgelist=[edge],
                edge_color=color,
                width=width,
                alpha=alpha,
                ax=ax
            )
            
            # Draw animated packets
            if edge in st.session_state.packet_simulator.active_edges or \
               (edge[1], edge[0]) in st.session_state.packet_simulator.active_edges:
                
                for flow_id, packet in st.session_state.packet_simulator.packet_positions.items():
                    if packet['edge'] == edge or packet['edge'] == (edge[1], edge[0]):
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        t = packet['progress']
                        px = x0 + t * (x1 - x0)
                        py = y0 + t * (y1 - y0)
                        ax.scatter(px, py, c='#FFD700', s=50, zorder=5, 
                                  edgecolors='black', linewidths=1)
        
        # Draw nodes with different colors based on detection method
        for node in st.session_state.graph.nodes():
            if node in rule_anomaly_ids:
                color, size, edgecolor = '#E74C3C', 600, 'darkred'  # Red - Rule anomaly
            elif node in ml_anomaly_ids:
                color, size, edgecolor = '#9B59B6', 550, 'purple'   # Purple - ML anomaly
            elif node in gnn_anomaly_ids:
                color, size, edgecolor = '#FF8C00', 550, 'darkorange'  # Orange - GNN anomaly
            else:
                color, size, edgecolor = '#4A90E2', 450, 'black'   # Blue - Normal
            
            # Outer glow for anomalies
            if node in rule_anomaly_ids or node in ml_anomaly_ids or node in gnn_anomaly_ids:
                nx.draw_networkx_nodes(
                    st.session_state.graph, pos,
                    nodelist=[node],
                    node_color=color,
                    node_size=size + 100,
                    alpha=0.3,
                    ax=ax
                )
            
            nx.draw_networkx_nodes(
                st.session_state.graph, pos,
                nodelist=[node],
                node_color=color,
                node_size=size,
                alpha=0.95,
                edgecolors=edgecolor,
                linewidths=2.5,
                ax=ax
            )
        
        # Draw labels
        labels = {}
        for node in st.session_state.graph.nodes():
            name = st.session_state.graph.nodes[node].get('name', node)
            if len(name) > 15:
                name = name[:12] + '..'
            
            # Add indicator based on detection type
            if node in rule_anomaly_ids:
                name = f"🔴 {name}"
            elif node in ml_anomaly_ids:
                name = f"🤖 {name}"
            elif node in gnn_anomaly_ids:
                name = f"🕸️ {name}"
            
            labels[node] = name
        
        nx.draw_networkx_labels(
            st.session_state.graph, pos,
            labels=labels,
            font_size=8,
            font_weight='bold',
            ax=ax
        )
        
        ax.set_title("🌐 Network Topology with Multi-Layer Anomaly Detection", 
                    fontsize=14, fontweight='bold')
        ax.axis('off')
        
        # Enhanced Legend
        legend_elements = [
            Patch(facecolor='#4A90E2', edgecolor='black', label='Normal Device'),
            Patch(facecolor='#E74C3C', edgecolor='darkred', label='🔴 Rule-based Anomaly'),
            Patch(facecolor='#9B59B6', edgecolor='purple', label='🤖 ML Anomaly (Isolation Forest)'),
            Patch(facecolor='#FF8C00', edgecolor='darkorange', label='🕸️ GNN Anomaly (Graph Neural Network)'),
            plt.Line2D([0], [0], color='#95A5A6', linewidth=2, label='Normal Connection'),
            plt.Line2D([0], [0], color='#FFA500', linewidth=3.5, label='📡 Active Packet Flow'),
            plt.Line2D([0], [0], color='#FF4500', linewidth=5, label='🔥 High Traffic Flow'),
            plt.Line2D([0], [0], color='#E74C3C', linewidth=2.5, label='Connection to Anomaly'),
            plt.Line2D([0], [0], color='#FFD700', marker='o', markersize=8, linestyle='None',
                      label='💫 Moving Packets')
        ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
        
        plt.tight_layout()
        return fig
    
    def draw_packet_flow_metrics(self):
        """Draw enhanced packet flow metrics panel (preserved from original)"""
        if not st.session_state.packet_simulator:
            return None
        
        stats = st.session_state.packet_simulator.get_flow_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Total Packets Sent", stats['total_packets'],
                     delta=f"+{stats['active_flows']} active")
        
        with col2:
            st.metric("⚡ Active Flows", stats['active_flows'],
                     delta="🔴 High" if st.session_state.attack_mode else "🟢 Normal")
        
        with col3:
            st.metric("✨ Animated Packets", stats['animated_packets'], delta="Moving")
        
        with col4:
            if stats['most_active_edge']:
                edge = stats['most_active_edge']
                st.metric("🔥 Busiest Link", f"{edge[0][:8]}→{edge[1][:8]}",
                         delta=f"{stats['total_flows']} flows")
            else:
                st.metric("🔥 Busiest Link", "None", delta="No traffic")
        
        st.progress(min(1.0, stats['active_flows'] / 20), 
                   text=f"📊 Network Traffic Intensity: {stats['active_flows']} active flows")
    
    def draw_traffic_heatmap(self):
        """Draw real-time traffic heatmap by layer (preserved from original)"""
        if not st.session_state.devices:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 4))
        
        layer_traffic = {'edge': 0, 'core': 0, 'access': 0, 'endpoint': 0}
        layer_counts = {'edge': 0, 'core': 0, 'access': 0, 'endpoint': 0}
        
        for device_id, device in st.session_state.devices.items():
            layer = device.layer.value if hasattr(device, 'layer') else 'unknown'
            if layer in layer_traffic:
                baseline = device.baseline_traffic
                layer_traffic[layer] += baseline
                layer_counts[layer] += 1
        
        for layer in layer_traffic:
            if layer_counts[layer] > 0:
                layer_traffic[layer] /= layer_counts[layer]
        
        layers = ['EDGE', 'CORE', 'ACCESS', 'ENDPOINT']
        values = [layer_traffic['edge'], layer_traffic['core'], 
                  layer_traffic['access'], layer_traffic['endpoint']]
        
        anomaly_layers = {a['layer'] for a in st.session_state.anomalies}
        colors = ['#E74C3C' if layer.lower() in anomaly_layers else '#4A90E2' 
                  for layer in layers]
        
        bars = ax.bar(layers, values, color=colors, alpha=0.8)
        ax.set_ylabel('Avg Traffic (pkts/sec)')
        ax.set_title('Network Layer Traffic Distribution')
        
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 5,
                   f'{value:.0f}', ha='center', va='bottom', fontsize=9)
        
        flow_stats = st.session_state.packet_simulator.get_flow_statistics()
        ax.text(0.98, 0.95, f"📡 Active Flows: {flow_stats['active_flows']}", 
               transform=ax.transAxes, ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def render_sidebar(self):
        """Render sidebar controls with new attack simulation options"""
        st.sidebar.title("🎮 NetGraphIQ Controls")
        
        if st.sidebar.button("🔄 Generate Network", use_container_width=True, type="primary"):
            self.generate_network()
            st.rerun()
        
        st.sidebar.divider()
        
        st.sidebar.subheader("⚙️ Display Settings")
        show_anomalies = st.sidebar.toggle("🔴 Show Anomalies", value=True)
        show_animation = st.sidebar.toggle("✨ Live Packet Animation", value=True)
        
        st.sidebar.divider()
        
        # NEW: Attack Simulation Controls
        st.sidebar.subheader("🎯 Attack Simulation")
        simulate_attack = st.sidebar.toggle(
            "⚠️ Simulate Attack Mode",
            value=False,
            help="Increases anomaly probability (30%) and traffic intensity (3.5-6x baseline)"
        )
        
        if simulate_attack:
            attack_type = st.sidebar.selectbox(
                "Attack Type",
                ["DDoS", "MAC Spoofing", "Device Failure"]
            )
            attack_map = {
                "DDoS": AttackType.DDOS,
                "MAC Spoofing": AttackType.MAC_SPOOFING,
                "Device Failure": AttackType.DEVICE_FAILURE
            }
            st.session_state.attack_type = attack_map[attack_type]
            
            st.sidebar.warning("🔴 **ATTACK MODE ACTIVE**\n\n• 30% anomaly probability\n• 3.5-6x traffic spikes\n• Simulating attack behavior")
        else:
            st.session_state.attack_type = AttackType.NONE
        
        st.session_state.simulate_attack = simulate_attack
        
        st.sidebar.divider()
        
        auto_refresh = st.sidebar.toggle("🔄 Auto Refresh", value=True)
        
        if auto_refresh:
            refresh_rate = st.sidebar.select_slider(
                "Refresh Rate (seconds)",
                options=[2, 3, 5, 10],
                value=3
            )
        else:
            refresh_rate = None
        
        return show_anomalies, show_animation, simulate_attack, auto_refresh, refresh_rate
    
    def render_metrics(self):
        """Render enhanced metrics panel with all detection methods"""
        st.markdown("### 📊 System Metrics")
        
        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
        
        with col1:
            st.metric("🖥️ Devices", len(st.session_state.devices) if st.session_state.devices else 0)
        
        with col2:
            st.metric("🔗 Connections", len(st.session_state.connections) if st.session_state.connections else 0)
        
        with col3:
            st.metric("⚠️ Rule", len(st.session_state.anomalies))
        
        with col4:
            st.metric("🤖 ML", len(st.session_state.ml_anomalies))
        
        with col5:
            st.metric("🕸️ GNN", len(st.session_state.gnn_anomalies))
        
        with col6:
            active_flows = len(st.session_state.packet_simulator.active_edges) if st.session_state.packet_simulator else 0
            st.metric("📡 Active Flows", active_flows)
        
        with col7:
            if st.session_state.simulate_attack:
                st.metric("⚠️ Attack", "ACTIVE", delta=st.session_state.attack_type.value.upper())
            else:
                st.metric("✅ Attack", "Inactive")
        
        # Second row - Additional metrics
        st.markdown("---")
        col8, col9, col10, col11 = st.columns(4)
        
        with col8:
            severity_counts = {}
            for a in st.session_state.anomalies:
                severity_counts[a['severity']] = severity_counts.get(a['severity'], 0) + 1
            critical_count = severity_counts.get('critical', 0)
            st.metric("🔴 Critical Alerts", critical_count, delta="URGENT" if critical_count > 0 else None)
        
        with col9:
            if st.session_state.root_cause:
                st.metric("🎯 Root Cause", st.session_state.root_cause['device_name'][:20])
            else:
                st.metric("🎯 Root Cause", "None Detected")
        
        with col10:
            total_devices = len(st.session_state.devices) if st.session_state.devices else 1
            total_anomalies = len(st.session_state.anomalies) + len(st.session_state.ml_anomalies) + len(st.session_state.gnn_anomalies)
            health_percent = max(0, 100 - (total_anomalies * 3))
            st.metric("💚 Network Health", f"{health_percent}%")
        
        with col11:
            gnn_count = len(st.session_state.gnn_anomalies)
            if gnn_count > 0:
                st.metric("🕸️ GNN Active", f"{gnn_count} detections", delta="Working")
            else:
                st.metric("🕸️ GNN Status", "Standby", delta="Waiting")
    
    def render_fingerprint_insights(self):
        """Display device fingerprinting insights (NEW)"""
        if not st.session_state.fingerprinter:
            return
        
        st.subheader("🔍 Device Fingerprinting (Behavior-Based Classification)")
        
        insights = st.session_state.fingerprinter.get_category_insights()
        
        cols = st.columns(len(insights))
        for i, (category, count) in enumerate(insights.items()):
            with cols[i]:
                st.metric(category.replace('_', ' ').title(), count)
        
        # Category risk assessment
        if st.session_state.anomalies:
            risk = st.session_state.fingerprinter.get_category_risk_assessment(
                st.session_state.anomalies
            )
            high_risk_categories = [f"{k}: {v}" for k, v in risk.items() if v > 0]
            if high_risk_categories:
                st.caption("🎯 Risk by Category: " + ", ".join(high_risk_categories))
    
    def render_detection_summary(self):
        """Render summary of all detection methods (NEW)"""
        st.subheader("📊 Multi-Layer Detection Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Rule-Based Detection**\n\n• {len(st.session_state.anomalies)} anomalies\n• Threshold-based\n• Immediate detection")
        
        with col2:
            st.info(f"**ML Detection (Isolation Forest)**\n\n• {len(st.session_state.ml_anomalies)} anomalies\n• Statistical outlier detection\n• Unsupervised learning")
        
        with col3:
            st.info(f"**GNN Detection**\n\n• {len(st.session_state.gnn_anomalies)} anomalies\n• Graph-aware detection\n• Captures propagation patterns")
    
    def render_root_cause(self):
        """Render root cause detection panel (preserved from original)"""
        if st.session_state.root_cause:
            rc = st.session_state.root_cause
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 20px; border-radius: 10px; margin: 10px 0;">
                <h3 style="color: white; margin: 0;">🎯 ROOT CAUSE ANALYSIS</h3>
                <hr style="background: white; margin: 10px 0;">
                <p style="color: white; margin: 5px 0 0 0; font-size: 18px;">
                    <strong>🚨 Primary Source:</strong> {rc['device_name']}
                </p>
                <p style="color: white; margin: 5px 0;">
                    <strong>📍 Layer:</strong> {rc['layer'].upper()} | 
                    <strong>⚠️ Severity:</strong> {rc['severity'].upper()} |
                    <strong>📊 Spike Ratio:</strong> {rc['spike_ratio']}x |
                    <strong>🔗 Connections:</strong> {rc.get('connection_count', 'N/A')}
                </p>
                <p style="color: #FFE66D; margin: 10px 0 0 0; font-size: 14px;">
                    <strong>💡 Impact Analysis:</strong> {rc.get('impact_analysis', 'Device is primary anomaly source')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.session_state.network_generated:
                st.success("✅ **No root cause detected** - Network operating within normal parameters")
    
    def render_telemetry_storage(self):
        """Render collapsible telemetry storage section (NEW)"""
        if not st.session_state.storage:
            return
        
        with st.expander("📁 Telemetry Storage (Recent Data)"):
            # Get telemetry data
            df = st.session_state.storage.get_telemetry_history(limit=50)
            
            if not df.empty:
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Records", len(df))
                with col2:
                    st.metric("🖥️ Unique Devices", df['device_id'].nunique())
                with col3:
                    if 'timestamp' in df.columns:
                        last_time = df['timestamp'].iloc[-1][:19] if len(df) > 0 else "N/A"
                        st.metric("⏱️ Last Updated", last_time)
                
                # Display recent data
                st.subheader("Recent Telemetry Records")
                display_df = df.tail(10)[['timestamp', 'device_name', 'baseline_traffic', 
                                           'current_traffic', 'is_anomaly']]
                display_df.columns = ['Timestamp', 'Device', 'Baseline', 'Current', 'Anomaly']
                st.dataframe(display_df, use_container_width=True)
                
                # Quick stats
                anomaly_count = df['is_anomaly'].sum()
                st.caption(f"📈 Summary: {anomaly_count} anomalous readings out of {len(df)} total records")
            else:
                st.info("No telemetry data available yet. Generate network and wait for updates.")
    
    def render_anomaly_table(self):
        """Render enhanced anomalies table with detection method, category, and reason"""
        if not st.session_state.anomalies and not st.session_state.ml_anomalies and not st.session_state.gnn_anomalies:
            st.info("✅ No anomalies detected - All devices operating normally")
            return
        
        anomaly_data = []
        
        # Rule-based anomalies
        for anomaly in st.session_state.anomalies:
            category = st.session_state.fingerprinter.get_device_category(anomaly['device_id']) if st.session_state.fingerprinter else "unknown"
            anomaly_data.append({
                "Device": anomaly['device_name'],
                "Layer": anomaly['layer'].upper(),
                "Category": category.replace('_', ' ').title(),
                "Severity": anomaly['severity'].upper(),
                "Detection": "🔴 Rule",
                "Details": anomaly['description'][:50],
                "Reason": "Threshold exceeded"
            })
        
        # ML anomalies
        for anomaly in st.session_state.ml_anomalies:
            category = st.session_state.fingerprinter.get_device_category(anomaly['device_id']) if st.session_state.fingerprinter else "unknown"
            anomaly_data.append({
                "Device": anomaly['device_name'],
                "Layer": "N/A",
                "Category": category.replace('_', ' ').title(),
                "Severity": "ML",
                "Detection": "🤖 ML",
                "Details": f"Score: {anomaly.get('anomaly_score', 0):.2f}",
                "Reason": "Isolation Forest outlier detection"
            })
        
        # GNN anomalies (with detailed reason)
        for anomaly in st.session_state.gnn_anomalies:
            category = st.session_state.fingerprinter.get_device_category(anomaly['device_id']) if st.session_state.fingerprinter else "unknown"
            anomaly_data.append({
                "Device": anomaly['device_name'],
                "Layer": anomaly.get('layer', 'N/A').upper(),
                "Category": category.replace('_', ' ').title(),
                "Severity": anomaly.get('severity', 'MEDIUM'),
                "Detection": "🕸️ GNN",
                "Details": f"Spike: {anomaly.get('spike_ratio', 0)}x | Neighbor: {anomaly.get('neighbor_avg_spike', 0)}x",
                "Reason": anomaly.get('reason', 'GNN detection')
            })
        
        df = pd.DataFrame(anomaly_data)
        
        def color_detection(val):
            if 'Rule' in str(val):
                return 'background-color: #ffcccc'
            elif 'ML' in str(val):
                return 'background-color: #e6ccff'
            elif 'GNN' in str(val):
                return 'background-color: #ffe6cc'
            return ''
        
        st.dataframe(
            df.style.applymap(color_detection, subset=['Detection']),
            use_container_width=True,
            height=400
        )
    
    def run(self):
        """Main dashboard loop"""
        st.set_page_config(
            page_title="NetGraphIQ - Complete Network Intelligence",
            page_icon="📡",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("📡 NetGraphIQ: Complete Network Intelligence Platform")
        st.markdown("*Multi-Layer Detection: Rule-Based · ML (Isolation Forest) · GNN (Graph Neural Network) · Live Packet Flow*")
        st.divider()
        
        if not st.session_state.network_generated:
            with st.spinner("Initializing network intelligence system..."):
                self.generate_network()
        
        show_anomalies, show_animation, attack_mode, auto_refresh, refresh_rate = self.render_sidebar()
        
        # Update network state
        rule_anomalies, ml_anomalies, gnn_anomalies = self.update_network_state(attack_mode)
        
        # Update packet flows
        if show_animation and st.session_state.packet_simulator:
            st.session_state.packet_simulator.update_flows(attack_mode)
        
        # Main content - 2 columns
        col_left, col_right = st.columns([1.2, 0.8])
        
        with col_left:
            st.subheader("🌐 Network Topology with Live Packet Flow")
            fig_graph = self.draw_network_graph()
            if fig_graph:
                st.pyplot(fig_graph)
        
        with col_right:
            st.subheader("📡 Live Packet Flow Metrics")
            self.draw_packet_flow_metrics()
            
            st.subheader("📊 Real-time Traffic Analysis")
            fig_traffic = self.draw_traffic_heatmap()
            if fig_traffic:
                st.pyplot(fig_traffic)
        
        # Metrics row
        st.divider()
        self.render_metrics()
        
        # Fingerprinting insights (NEW)
        self.render_fingerprint_insights()
        
        # Detection summary (NEW)
        self.render_detection_summary()
        
        # Root cause section
        st.divider()
        self.render_root_cause()
        
        # Anomaly table
        st.subheader("🚨 Multi-Layer Anomaly Detection Results")
        self.render_anomaly_table()
        
        # Telemetry Storage Section (NEW)
        self.render_telemetry_storage()
        
        # Footer
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"📡 NetGraphIQ v4.0 | Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")
        with col2:
            if attack_mode:
                st.caption("⚠️ Attack Mode: ACTIVE")
            else:
                st.caption("✅ Attack Mode: Inactive")
        with col3:
            total_anomalies = len(rule_anomalies) + len(ml_anomalies) + len(gnn_anomalies)
            st.caption(f"🚨 Total Alerts: {total_anomalies} (Rule: {len(rule_anomalies)}, ML: {len(ml_anomalies)}, GNN: {len(gnn_anomalies)})")
        
        if auto_refresh and refresh_rate:
            time.sleep(refresh_rate)
            st.rerun()


def main():
    dashboard = IntegratedDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()