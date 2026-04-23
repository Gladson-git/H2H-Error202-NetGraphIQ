"""
NetGraphIQ - Complete Integrated Dashboard with Hierarchical Visualization
Industry-grade UI with root cause propagation and modern styling
"""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import random
import time
import sys
import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from collections import deque

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network_generator import NetworkGenerator
from src.core.telemetry_engine import TelemetryEngine
from src.core.anomaly_engine import AnomalyEngine
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
        
        current_time = time.time()
        expired_packets = [
            flow_id for flow_id, pos in self.packet_positions.items()
            if current_time - pos['start_time'] >= pos['duration']
        ]
        for flow_id in expired_packets:
            del self.packet_positions[flow_id]

        self.active_edges = {
            edge: data for edge, data in self.active_edges.items()
            if current_time - data['start_time'] < data['duration']
            and any(pos['edge'] == edge for pos in self.packet_positions.values())
        }

        num_flows = random.randint(4, 8) if attack_mode else random.randint(2, 5)
        
        for _ in range(num_flows):
            edge = random.choice(list(self.graph.edges()))
            
            self.edge_flow_count[edge] = self.edge_flow_count.get(edge, 0) + 1
            self.flow_counter += 1
            
            is_anomaly_edge = (edge[0] in self.anomaly_ids or edge[1] in self.anomaly_ids)
            
            if is_anomaly_edge:
                intensity = random.uniform(0.8, 1.0)
                duration = random.uniform(7.0, 10.0) if attack_mode else random.uniform(8.0, 12.0)
                packet_size = random.randint(100, 500)
            else:
                intensity = random.uniform(0.3, 0.7)
                duration = random.uniform(7.0, 10.5) if attack_mode else random.uniform(8.5, 13.0)
                packet_size = random.randint(50, 200)
            
            self.active_edges[edge] = {
                'intensity': intensity,
                'start_time': current_time,
                'duration': duration,
                'packet_size': packet_size,
                'flow_id': self.flow_counter
            }
            
            self.packet_positions[self.flow_counter] = {
                'edge': edge,
                'progress': 0.0,
                'speed': random.uniform(0.72, 1.08),
                'start_time': current_time,
                'duration': duration,
                'start_offset': random.uniform(0.0, 0.78)
            }

        for flow_id, pos in self.packet_positions.items():
            elapsed = current_time - pos['start_time']
            pos['progress'] = (pos['start_offset'] + (elapsed / pos['duration']) * pos['speed']) % 1.0
    
    def get_edge_style(self, edge: Tuple) -> Tuple[str, float, float, int]:
        """Get edge style based on active flows and anomalies"""
        if edge in self.active_edges or (edge[1], edge[0]) in self.active_edges:
            flow_count = self.edge_flow_count.get(edge, 0)
            
            if flow_count > 10:
                return '#DC2626', 4.0, 0.9, flow_count
            elif flow_count > 5:
                return '#D97706', 3.2, 0.85, flow_count
            else:
                return '#2563EB', 2.6, 0.78, flow_count
        
        if edge[0] in self.anomaly_ids or edge[1] in self.anomaly_ids:
            return '#DC2626', 2.2, 0.78, 0
        
        return '#4B5563', 1.1, 0.55, 0
    
    def get_flow_statistics(self) -> Dict:
        return {
            'total_flows': self.flow_counter,
            'active_flows': len(self.active_edges),
            'animated_packets': len(self.packet_positions),
            'most_active_edge': max(self.edge_flow_count.items(), key=lambda x: x[1])[0] if self.edge_flow_count else None,
            'total_packets': sum(self.edge_flow_count.values())
        }


class IntegratedDashboard:
    """Complete integrated dashboard with hierarchical visualization and modern UI"""
    
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
            st.session_state.propagation_path = []
            st.session_state.impact_devices = 0
            
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
            st.session_state.sidebar_collapsed = False
            st.session_state.show_anomalies = True
            st.session_state.show_animation = True
            st.session_state.auto_refresh = True
            st.session_state.refresh_rate = 3
    
    def _get_layer_level(self, layer: str) -> int:
        """Get vertical level for hierarchical layout"""
        layer_levels = {
            'edge': 3,
            'core': 2,
            'access': 1,
            'endpoint': 0
        }
        return layer_levels.get(layer.lower(), 1)
    
    def _calculate_hierarchical_positions(self, graph: nx.Graph) -> Dict:
        """Calculate positions for hierarchical layout (layers stacked vertically)"""
        pos = {}
        
        # Group nodes by layer
        layer_nodes = defaultdict(list)
        for node, attrs in graph.nodes(data=True):
            layer = attrs.get('layer', 'endpoint')
            layer_nodes[layer].append(node)
        
        # Define layer Y positions (higher Y = higher in graph)
        y_positions = {
            'edge': 3.0,
            'core': 2.0,
            'access': 1.0,
            'endpoint': 0.0
        }
        
        # Position nodes within each layer
        for layer, nodes in layer_nodes.items():
            y = y_positions.get(layer, 1.0)
            num_nodes = len(nodes)
            
            for i, node in enumerate(nodes):
                # Spread nodes horizontally
                x = (i - (num_nodes - 1) / 2) * 1.5
                pos[node] = (x, y)
        
        # Fine-tune positions to reduce edge crossings
        for edge in graph.edges():
            node1, node2 = edge
            if node1 in pos and node2 in pos:
                # Slight adjustment for better alignment
                pass
        
        return pos
    
    def _find_propagation_path(self, root_device_id: str, graph: nx.Graph, depth: int = 2) -> Tuple[List[str], int]:
        """
        Find propagation path from root cause using BFS
        Returns (path_nodes, total_affected_devices)
        """
        if not root_device_id or not graph.has_node(root_device_id):
            return [], 0
        
        visited = set()
        queue = deque([(root_device_id, 0)])
        path = [root_device_id]
        affected_devices = set()
        
        while queue:
            node, level = queue.popleft()
            if level >= depth:
                continue
            
            for neighbor in graph.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    affected_devices.add(neighbor)
                    if level < depth - 1:
                        queue.append((neighbor, level + 1))
                        if neighbor not in path:
                            path.append(neighbor)
        
        # Get device names for path
        device_names = []
        for node_id in path[:depth + 2]:  # Limit path length
            device = st.session_state.devices.get(node_id)
            if device:
                device_names.append(device.name)
            else:
                device_names.append(node_id[:8])
        
        return device_names, len(affected_devices)
    
    def generate_network(self):
        """Generate complete network topology with all components"""
        with st.spinner("🌐 Generating enterprise network topology..."):
            generator = NetworkGenerator()
            devices, connections = generator.generate_enterprise_network()
            
            # Build graph
            graph = nx.Graph()
            for device_id, device in devices.items():
                layer_value = device.layer.value if hasattr(device, 'layer') else 'endpoint'
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
        
        # NEW: GNN anomalies (Graph Neural Network)
        gnn_anomalies = st.session_state.gnn_detector.detect(
            st.session_state.graph, st.session_state.devices, current_metrics
        )
        
        # Store telemetry to CSV
        for device_id, data in current_metrics.items():
            device = st.session_state.devices.get(device_id)
            if device:
                st.session_state.storage.save_telemetry(
                    device_id, device.name,
                    data['baseline'], data['current'],
                    data['is_anomaly']
                )
        
        # Update packet simulator with anomaly IDs
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
        
        # Find root cause using rule-based anomalies
        if st.session_state.graph and rule_anomalies:
            st.session_state.root_cause = st.session_state.anomaly_engine.find_root_cause(
                rule_anomalies, st.session_state.graph
            )
            
            # Calculate propagation path from root cause
            if st.session_state.root_cause:
                path, impact_count = self._find_propagation_path(
                    st.session_state.root_cause['device_id'],
                    st.session_state.graph,
                    depth=2
                )
                st.session_state.propagation_path = path
                st.session_state.impact_devices = impact_count
        else:
            st.session_state.root_cause = None
            st.session_state.propagation_path = []
            st.session_state.impact_devices = 0
        
        st.session_state.last_update = datetime.now()
        st.session_state.attack_mode = attack_mode
        
        return rule_anomalies, ml_anomalies, gnn_anomalies
    
    def draw_network_graph_hierarchical(self):
        """Draw network topology with hierarchical layer-based layout"""
        if not st.session_state.graph:
            return None
        
        fig, ax = plt.subplots(figsize=(14, 10), facecolor='#111827')
        ax.set_facecolor('#111827')
        
        # Calculate hierarchical positions
        pos = self._calculate_hierarchical_positions(st.session_state.graph)
        
        # Get all anomaly IDs from all detection methods
        rule_anomaly_ids = {a['device_id'] for a in st.session_state.anomalies}
        ml_anomaly_ids = {a['device_id'] for a in st.session_state.ml_anomalies}
        gnn_anomaly_ids = {a['device_id'] for a in st.session_state.gnn_anomalies}
        root_cause_id = st.session_state.root_cause['device_id'] if st.session_state.root_cause else None
        
        # Draw edges with styles
        for edge in st.session_state.graph.edges():
            color, width, alpha, flow_count = st.session_state.packet_simulator.get_edge_style(edge)
            
            # Thicker edges for anomaly connections
            if edge[0] in rule_anomaly_ids or edge[1] in rule_anomaly_ids:
                width = width + 1.5
                color = '#DC2626'
            
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
                        ax.scatter(px, py, c='#60A5FA', s=42, zorder=5,
                                  edgecolors='#0B0F14', linewidths=1)
        
        # Draw nodes with different colors based on detection method
        for node in st.session_state.graph.nodes():
            # Determine node style
            if node == root_cause_id:
                color, size, edgecolor, linewidth = '#DC2626', 760, '#FCA5A5', 2.2
            elif node in rule_anomaly_ids:
                color, size, edgecolor, linewidth = '#B91C1C', 580, '#FCA5A5', 1.8
            elif node in ml_anomaly_ids:
                color, size, edgecolor, linewidth = '#2563EB', 520, '#93C5FD', 1.6
            elif node in gnn_anomaly_ids:
                color, size, edgecolor, linewidth = '#D97706', 520, '#FCD34D', 1.6
            else:
                color, size, edgecolor, linewidth = '#374151', 430, '#6B7280', 1.2
            
            nx.draw_networkx_nodes(
                st.session_state.graph, pos,
                nodelist=[node],
                node_color=color,
                node_size=size,
                alpha=0.95,
                edgecolors=edgecolor,
                linewidths=linewidth,
                ax=ax
            )
        
        # Draw labels
        labels = {}
        for node in st.session_state.graph.nodes():
            name = st.session_state.graph.nodes[node].get('name', node)
            if len(name) > 15:
                name = name[:12] + '..'
            
            if node == root_cause_id:
                name = f"🎯 {name}"
            elif node in rule_anomaly_ids:
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
            font_color='#E5E7EB',
            ax=ax
        )
        
        # Add layer annotations
        layer_y_positions = {'EDGE': 3.0, 'CORE': 2.0, 'ACCESS': 1.0, 'ENDPOINT': 0.0}
        for layer, y in layer_y_positions.items():
            ax.text(-2.5, y, f"─── {layer} LAYER ───", fontsize=10, 
                   fontweight='bold', color='#9CA3AF', alpha=0.8,
                   transform=ax.transData)
        
        ax.set_title("🌐 Hierarchical Network Topology with Multi-Layer Anomaly Detection", 
                    fontsize=16, fontweight='bold', pad=20, color='#E5E7EB')
        ax.axis('off')
        
        # Enhanced Legend
        legend_elements = [
            Patch(facecolor='#374151', edgecolor='#6B7280', label='Normal Device'),
            Patch(facecolor='#DC2626', edgecolor='#FCA5A5', label='🎯 Root Cause Device'),
            Patch(facecolor='#B91C1C', edgecolor='#FCA5A5', label='🔴 Rule-based Anomaly'),
            Patch(facecolor='#2563EB', edgecolor='#93C5FD', label='🤖 ML Anomaly'),
            Patch(facecolor='#D97706', edgecolor='#FCD34D', label='🕸️ GNN Anomaly'),
            plt.Line2D([0], [0], color='#4B5563', linewidth=2, label='Normal Connection'),
            plt.Line2D([0], [0], color='#2563EB', linewidth=3, label='📡 Active Packet Flow'),
            plt.Line2D([0], [0], color='#DC2626', linewidth=3, label='⚠️ Connection to Anomaly'),
            plt.Line2D([0], [0], color='#60A5FA', marker='o', markersize=7, linestyle='None',
                      label='💫 Moving Packets')
        ]
        legend = ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=9)
        legend.get_frame().set_facecolor('#111827')
        legend.get_frame().set_edgecolor('#111827')
        for text in legend.get_texts():
            text.set_color('#E5E7EB')
        
        plt.tight_layout()
        return fig

    def draw_cyber_3d_topology(self):
        """Draw a large interactive Plotly 3D topology model."""
        if not st.session_state.graph:
            return None

        pos_2d = self._calculate_hierarchical_positions(st.session_state.graph)
        xs = [p[0] for p in pos_2d.values()]
        ys = [p[1] for p in pos_2d.values()]
        x_mid = (min(xs) + max(xs)) / 2 if xs else 0
        y_mid = (min(ys) + max(ys)) / 2 if ys else 0
        x_span = max(max(xs) - min(xs), 1) if xs else 1
        y_span = max(max(ys) - min(ys), 1) if ys else 1

        pos = {}
        for idx, (node, (x, y)) in enumerate(pos_2d.items()):
            layer = st.session_state.graph.nodes[node].get('layer', 'endpoint')
            z_base = self._get_layer_level(layer) * 0.46
            pos[node] = (
                (x - x_mid) / x_span * 6.8,
                (y - y_mid) / y_span * 3.8,
                z_base + np.sin(idx * 0.73) * 0.18,
            )

        rule_anomaly_ids = {a['device_id'] for a in st.session_state.anomalies}
        ml_anomaly_ids = {a['device_id'] for a in st.session_state.ml_anomalies}
        gnn_anomaly_ids = {a['device_id'] for a in st.session_state.gnn_anomalies}
        root_cause_id = st.session_state.root_cause['device_id'] if st.session_state.root_cause else None

        traces = []
        theta = np.linspace(0, 2 * np.pi, 260)
        for radius, color, alpha, z in [
            (5.1, '#b77dff', 0.5, 0.58),
            (3.75, '#22d3ee', 0.28, 0.78),
        ]:
            traces.append(go.Scatter3d(
                x=radius * np.cos(theta),
                y=1.05 * np.sin(theta),
                z=np.full_like(theta, z),
                mode="lines",
                line=dict(color=color, width=5),
                opacity=alpha,
                hoverinfo="skip",
                showlegend=False,
            ))

        for grid_x in np.linspace(-5.4, 5.4, 8):
            traces.append(go.Scatter3d(
                x=[grid_x, grid_x], y=[-2.6, 2.6], z=[-0.08, -0.08],
                mode="lines",
                line=dict(color='rgba(34,211,238,0.18)', width=2),
                hoverinfo="skip",
                showlegend=False,
            ))
        for grid_y in np.linspace(-2.6, 2.6, 6):
            traces.append(go.Scatter3d(
                x=[-5.4, 5.4], y=[grid_y, grid_y], z=[-0.08, -0.08],
                mode="lines",
                line=dict(color='rgba(34,211,238,0.18)', width=2),
                hoverinfo="skip",
                showlegend=False,
            ))

        edge_x, edge_y, edge_z = [], [], []
        active_x, active_y, active_z = [], [], []
        anomaly_edge_x, anomaly_edge_y, anomaly_edge_z = [], [], []
        packet_paths = []
        for edge in st.session_state.graph.edges():
            color, width, alpha, flow_count = st.session_state.packet_simulator.get_edge_style(edge)
            target = (edge_x, edge_y, edge_z)
            if edge[0] in rule_anomaly_ids or edge[1] in rule_anomaly_ids:
                target = (anomaly_edge_x, anomaly_edge_y, anomaly_edge_z)
            elif edge in st.session_state.packet_simulator.active_edges or \
                 (edge[1], edge[0]) in st.session_state.packet_simulator.active_edges:
                target = (active_x, active_y, active_z)

            x0, y0, z0 = pos[edge[0]]
            x1, y1, z1 = pos[edge[1]]
            target[0].extend([x0, x1, None])
            target[1].extend([y0, y1, None])
            target[2].extend([z0, z1, None])

            if edge in st.session_state.packet_simulator.active_edges or \
               (edge[1], edge[0]) in st.session_state.packet_simulator.active_edges:
                for flow_id, packet in st.session_state.packet_simulator.packet_positions.items():
                    if packet['edge'] != edge and packet['edge'] != (edge[1], edge[0]):
                        continue

                    if packet['edge'] == (edge[1], edge[0]):
                        sx, sy, sz = x1, y1, z1
                        ex, ey, ez = x0, y0, z0
                    else:
                        sx, sy, sz = x0, y0, z0
                        ex, ey, ez = x1, y1, z1

                    packet_paths.append({
                        "progress": packet['progress'],
                        "speed": packet.get('speed', 1.0),
                        "sx": sx, "sy": sy, "sz": sz,
                        "ex": ex, "ey": ey, "ez": ez,
                    })

        def build_packet_visuals(progress_offset: float = 0.0) -> Dict[str, List[float]]:
            visuals = {
                "head_x": [], "head_y": [], "head_z": [],
                "glow_x": [], "glow_y": [], "glow_z": [],
                "trail_x": [], "trail_y": [], "trail_z": [],
                "segment_x": [], "segment_y": [], "segment_z": [],
            }

            for packet in packet_paths:
                sx, sy, sz = packet["sx"], packet["sy"], packet["sz"]
                ex, ey, ez = packet["ex"], packet["ey"], packet["ez"]
                t = (packet["progress"] + progress_offset * packet["speed"]) % 1.0

                px = sx + t * (ex - sx)
                py = sy + t * (ey - sy)
                pz = sz + t * (ez - sz)
                visuals["head_x"].append(px)
                visuals["head_y"].append(py)
                visuals["head_z"].append(pz + 0.035)
                visuals["glow_x"].append(px)
                visuals["glow_y"].append(py)
                visuals["glow_z"].append(pz + 0.035)

                segment_start = max(0.0, t - 0.09)
                visuals["segment_x"].extend([sx + segment_start * (ex - sx), px, None])
                visuals["segment_y"].extend([sy + segment_start * (ey - sy), py, None])
                visuals["segment_z"].extend([sz + segment_start * (ez - sz) + 0.025, pz + 0.035, None])

                for trail_step in (0.07, 0.14, 0.21):
                    trail_t = max(0.0, t - trail_step)
                    visuals["trail_x"].append(sx + trail_t * (ex - sx))
                    visuals["trail_y"].append(sy + trail_t * (ey - sy))
                    visuals["trail_z"].append(sz + trail_t * (ez - sz) + 0.025)

            return visuals

        packet_visuals = build_packet_visuals()

        traces.extend([
            go.Scatter3d(
                x=edge_x, y=edge_y, z=edge_z,
                mode="lines",
                line=dict(color='rgba(34,211,238,0.32)', width=3),
                hoverinfo="skip",
                showlegend=False,
            ),
            go.Scatter3d(
                x=active_x, y=active_y, z=active_z,
                mode="lines",
                line=dict(color='rgba(245,158,11,0.78)', width=6),
                hoverinfo="skip",
                showlegend=False,
            ),
            go.Scatter3d(
                x=anomaly_edge_x, y=anomaly_edge_y, z=anomaly_edge_z,
                mode="lines",
                line=dict(color='rgba(255,63,143,0.9)', width=7),
                hoverinfo="skip",
                showlegend=False,
            ),
        ])

        node_groups = {
            "Normal Device": {"x": [], "y": [], "z": [], "text": [], "color": "#28e7ff", "size": 9},
            "Root Cause": {"x": [], "y": [], "z": [], "text": [], "color": "#ff3f8f", "size": 16},
            "Rule Anomaly": {"x": [], "y": [], "z": [], "text": [], "color": "#ff4d7d", "size": 13},
            "ML Anomaly": {"x": [], "y": [], "z": [], "text": [], "color": "#b77dff", "size": 12},
            "GNN Anomaly": {"x": [], "y": [], "z": [], "text": [], "color": "#f59e0b", "size": 12},
        }
        for node in st.session_state.graph.nodes():
            if node == root_cause_id:
                group = node_groups["Root Cause"]
            elif node in rule_anomaly_ids:
                group = node_groups["Rule Anomaly"]
            elif node in ml_anomaly_ids:
                group = node_groups["ML Anomaly"]
            elif node in gnn_anomaly_ids:
                group = node_groups["GNN Anomaly"]
            else:
                group = node_groups["Normal Device"]

            x, y, z = pos[node]
            name = st.session_state.graph.nodes[node].get('name', node)
            if len(name) > 15:
                name = name[:13] + ".."
            group["x"].append(x)
            group["y"].append(y)
            group["z"].append(z)
            group["text"].append(name)

        for label, group in node_groups.items():
            if not group["x"]:
                continue
            traces.append(go.Scatter3d(
                x=group["x"], y=group["y"], z=group["z"],
                mode="markers+text",
                text=group["text"],
                textposition="top center",
                textfont=dict(color="#dffbff", size=11, family="JetBrains Mono, Fira Code, monospace"),
                marker=dict(
                    size=group["size"],
                    color=group["color"],
                    opacity=0.92,
                    line=dict(color="#dffbff", width=1.2),
                ),
                hovertemplate="<b>%{text}</b><extra>" + label + "</extra>",
                name=label,
            ))

        traces.append(go.Scatter3d(
            x=packet_visuals["segment_x"], y=packet_visuals["segment_y"], z=packet_visuals["segment_z"],
            mode="lines",
            line=dict(color='rgba(212,246,255,0.72)', width=6),
            opacity=0.62,
            hoverinfo="skip",
            name="Packet Motion",
            showlegend=False,
        ))
        traces.append(go.Scatter3d(
            x=packet_visuals["trail_x"], y=packet_visuals["trail_y"], z=packet_visuals["trail_z"],
            mode="markers",
            marker=dict(size=3.8, color="#7dd3fc", opacity=0.42),
            hoverinfo="skip",
            name="Packet Trail",
            showlegend=False,
        ))
        traces.append(go.Scatter3d(
            x=packet_visuals["glow_x"], y=packet_visuals["glow_y"], z=packet_visuals["glow_z"],
            mode="markers",
            marker=dict(size=12, color="#67e8f9", opacity=0.18),
            hoverinfo="skip",
            name="Packet Glow",
            showlegend=False,
        ))
        traces.append(go.Scatter3d(
            x=packet_visuals["head_x"], y=packet_visuals["head_y"], z=packet_visuals["head_z"],
            mode="markers",
            marker=dict(size=6.8, color="#f8fafc", opacity=0.94, line=dict(color="#22d3ee", width=1.4)),
            hovertemplate="Packet in transit<extra></extra>",
            name="Moving Packets",
            showlegend=False,
        ))

        fig = go.Figure(data=traces)
        fig.update_layout(
            height=820,
            margin=dict(l=0, r=0, t=8, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#dffbff", family="JetBrains Mono, Fira Code, monospace"),
            showlegend=False,
            scene=dict(
                bgcolor="rgba(0,0,0,0)",
                xaxis=dict(visible=False, range=[-5.8, 5.8]),
                yaxis=dict(visible=False, range=[-2.95, 2.95]),
                zaxis=dict(visible=False, range=[-0.2, 2.15]),
                aspectmode="manual",
                aspectratio=dict(x=2.45, y=1.25, z=0.72),
                camera=dict(
                    eye=dict(x=1.15, y=-1.85, z=1.05),
                    center=dict(x=0, y=0, z=0.18),
                    up=dict(x=0, y=0, z=1),
                ),
            ),
        )
        return fig
    
    def draw_packet_flow_metrics(self):
        """Draw enhanced packet flow metrics panel"""
        if not st.session_state.packet_simulator:
            return None
        
        stats = st.session_state.packet_simulator.get_flow_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Total Packets", stats['total_packets'],
                     delta=f"+{stats['active_flows']} active")
        
        with col2:
            st.metric("⚡ Active Flows", stats['active_flows'],
                     delta="🔴 HIGH" if st.session_state.attack_mode else "🟢 NORMAL")
        
        with col3:
            st.metric("✨ Animated Packets", stats['animated_packets'], delta="Moving")
        
        with col4:
            if stats['most_active_edge']:
                edge = stats['most_active_edge']
                st.metric("🔥 Busiest Link", f"{edge[0][:6]}→{edge[1][:6]}",
                         delta=f"{stats['total_flows']} flows")
            else:
                st.metric("🔥 Busiest Link", "None", delta="No traffic")
        
        st.progress(min(1.0, stats['active_flows'] / 20), 
                   text=f"📊 Network Traffic Intensity: {stats['active_flows']} active flows")
    
    def draw_traffic_heatmap(self):
        """Draw real-time traffic heatmap by layer"""
        if not st.session_state.devices:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 4), facecolor='#111827')
        
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
        colors = ['#DC2626' if layer.lower() in anomaly_layers else '#2563EB'
                  for layer in layers]
        
        bars = ax.bar(layers, values, color=colors, alpha=0.86, edgecolor='#1F2937', linewidth=1)
        ax.set_ylabel('Avg Traffic (pkts/sec)', fontsize=11, color='#9CA3AF')
        ax.set_title('Network Layer Traffic Distribution', fontsize=13, fontweight='bold', color='#E5E7EB')
        ax.set_facecolor('#111827')
        ax.tick_params(colors='#9CA3AF')
        ax.grid(axis='y', color='#1F2937', linewidth=0.8, alpha=0.75)
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 5,
                   f'{value:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#E5E7EB')
        
        flow_stats = st.session_state.packet_simulator.get_flow_statistics()
        ax.text(0.98, 0.95, f"📡 Active Flows: {flow_stats['active_flows']}", 
               transform=ax.transAxes, ha='right', va='top',
               color='#E5E7EB',
               bbox=dict(boxstyle='round', facecolor='#0B0F14', edgecolor='#0B0F14', alpha=0.92))
        
        plt.tight_layout()
        return fig
    
    def render_sidebar(self):
        """Render collapsible sidebar controls with grouped sections"""
        for key, value in {
            "sidebar_collapsed": False,
            "show_anomalies": True,
            "show_animation": True,
            "simulate_attack": False,
            "auto_refresh": True,
            "refresh_rate": 3,
        }.items():
            if key not in st.session_state:
                st.session_state[key] = value

        collapsed = st.session_state.sidebar_collapsed
        state_class = "collapsed" if collapsed else "expanded"
        toggle_icon = "»" if collapsed else "«"
        st.sidebar.markdown(f'<span class="sidebar-state {state_class}"></span>', unsafe_allow_html=True)

        if st.sidebar.button(toggle_icon, key="sidebar_toggle", help="Expand sidebar" if collapsed else "Collapse sidebar"):
            st.session_state.sidebar_collapsed = not collapsed
            st.rerun()

        if collapsed:
            if st.sidebar.button("G", key="generate_network_compact", help="Generate Network"):
                self.generate_network()
                st.rerun()

            if st.sidebar.button("O", key="show_anomalies_compact", help="Show Anomalies"):
                st.session_state.show_anomalies = not st.session_state.show_anomalies
                st.rerun()

            if st.sidebar.button("P", key="show_animation_compact", help="Live Packet Animation"):
                st.session_state.show_animation = not st.session_state.show_animation
                st.rerun()

            if st.sidebar.button("!", key="attack_mode_compact", help="Simulate Attack Mode"):
                st.session_state.simulate_attack = not st.session_state.simulate_attack
                st.session_state.attack_type = AttackType.DDOS if st.session_state.simulate_attack else AttackType.NONE
                st.rerun()

            if st.sidebar.button("A", key="auto_refresh_compact", help="Auto Refresh"):
                st.session_state.auto_refresh = not st.session_state.auto_refresh
                st.rerun()

            return (
                st.session_state.show_anomalies,
                st.session_state.show_animation,
                st.session_state.simulate_attack,
                st.session_state.auto_refresh,
                st.session_state.refresh_rate if st.session_state.auto_refresh else None,
            )

        st.sidebar.markdown("""
        <style>
        .sidebar-section {
            padding: 12px 0;
            margin-bottom: 12px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.sidebar.title("CONTROL PANEL")
        
        # Network Section
        st.sidebar.markdown("### 🌐 Network")
        if st.sidebar.button("🔄 Generate New Network", use_container_width=True, type="primary", help="Generate Network"):
            self.generate_network()
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Display Section
        st.sidebar.markdown("### ⚙️ Display")
        show_anomalies = st.sidebar.toggle("🔴 Show Anomalies", key="show_anomalies")
        show_animation = st.sidebar.toggle("✨ Live Packet Animation", key="show_animation")
        
        st.sidebar.markdown("---")
        
        # Attack Section
        st.sidebar.markdown("### 🎯 Attack Simulation")
        simulate_attack = st.sidebar.toggle(
            "⚠️ Simulate Attack Mode",
            key="simulate_attack",
            help="Increases anomaly probability (30%) and traffic intensity (3.5-6x baseline)"
        )
        
        if simulate_attack:
            attack_type = st.sidebar.selectbox(
                "Attack Type",
                ["DDoS", "MAC Spoofing", "Device Failure"],
                help="Select attack type to simulate"
            )
            attack_map = {
                "DDoS": AttackType.DDOS,
                "MAC Spoofing": AttackType.MAC_SPOOFING,
                "Device Failure": AttackType.DEVICE_FAILURE
            }
            st.session_state.attack_type = attack_map[attack_type]
            
            st.sidebar.warning("🔴 **ATTACK MODE ACTIVE**\n\n• 30% anomaly probability\n• 3.5-6x traffic spikes")
        else:
            st.session_state.attack_type = AttackType.NONE
        
        st.sidebar.markdown("---")
        
        # Refresh Section
        st.sidebar.markdown("### 🔄 Refresh")
        auto_refresh = st.sidebar.toggle("Auto Refresh", key="auto_refresh")
        
        if auto_refresh:
            refresh_rate = st.sidebar.select_slider(
                "Refresh Rate",
                options=[2, 3, 5, 10],
                key="refresh_rate"
            )
        else:
            refresh_rate = None
        
        return show_anomalies, show_animation, simulate_attack, auto_refresh, refresh_rate
    
    def render_metrics(self):
        """Render glass HUD metric strip."""
        st.markdown('<div class="hud-section-title">SYSTEM METRICS</div>', unsafe_allow_html=True)

        def metric_tile(value, label, color="#E5E7EB"):
            st.markdown(f"""
            <div class="metric-tile">
                <h3 style="color: {color};">{value}</h3>
                <p>{label}</p>
            </div>
            """, unsafe_allow_html=True)

        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

        with col1:
            metric_tile(len(st.session_state.devices) if st.session_state.devices else 0, "Devices")

        with col2:
            metric_tile(len(st.session_state.connections) if st.session_state.connections else 0, "Connections")

        with col3:
            color = "#DC2626" if len(st.session_state.anomalies) > 0 else "#2563EB"
            metric_tile(len(st.session_state.anomalies), "Rule", color)

        with col4:
            metric_tile(len(st.session_state.ml_anomalies), "ML", "#2563EB")

        with col5:
            color = "#D97706" if len(st.session_state.gnn_anomalies) > 0 else "#2563EB"
            metric_tile(len(st.session_state.gnn_anomalies), "GNN", color)

        with col6:
            active_flows = len(st.session_state.packet_simulator.active_edges) if st.session_state.packet_simulator else 0
            metric_tile(active_flows, "Active Flows", "#2563EB")

        with col7:
            attack_status = "ACTIVE" if st.session_state.simulate_attack else "INACTIVE"
            color = "#DC2626" if st.session_state.simulate_attack else "#9CA3AF"
            metric_tile(attack_status, "Attack", color)

        st.markdown("---")
        col8, col9, col10, col11 = st.columns(4)

        with col8:
            severity_counts = {}
            for a in st.session_state.anomalies:
                severity_counts[a['severity']] = severity_counts.get(a['severity'], 0) + 1
            critical_count = severity_counts.get('critical', 0)
            st.metric("Critical Alerts", critical_count, delta="URGENT" if critical_count > 0 else None)

        with col9:
            if st.session_state.root_cause:
                st.metric("Root Cause", st.session_state.root_cause['device_name'][:20])
            else:
                st.metric("Root Cause", "None Detected")

        with col10:
            total_anomalies = len(st.session_state.anomalies) + len(st.session_state.ml_anomalies) + len(st.session_state.gnn_anomalies)
            health_percent = max(0, 100 - (total_anomalies * 3))
            st.metric("Network Health", f"{health_percent}%")

        with col11:
            gnn_count = len(st.session_state.gnn_anomalies)
            if gnn_count > 0:
                st.metric("GNN Active", f"{gnn_count} detections", delta="Working")
            else:
                st.metric("GNN Status", "Standby", delta="Waiting")

    def render_fingerprint_insights(self):
        """Display device fingerprinting insights"""
        if not st.session_state.fingerprinter:
            return
        
        st.markdown("### 🔍 Device Fingerprinting")
        st.markdown("*Behavior-based device classification*")
        
        insights = st.session_state.fingerprinter.get_category_insights()
        
        cols = st.columns(len(insights))
        for i, (category, count) in enumerate(insights.items()):
            with cols[i]:
                st.metric(category.replace('_', ' ').title(), count)
        
        if st.session_state.anomalies:
            risk = st.session_state.fingerprinter.get_category_risk_assessment(st.session_state.anomalies)
            high_risk = [f"{k}: {v}" for k, v in risk.items() if v > 0]
            if high_risk:
                st.caption("🎯 Risk by Category: " + ", ".join(high_risk))
    
    def render_detection_summary(self):
        """Render summary of all detection methods"""
        st.markdown("### 🧠 Multi-Layer Detection Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Rule-Based Detection**\n\n• {len(st.session_state.anomalies)} anomalies\n• Threshold-based\n• Immediate detection")
        
        with col2:
            st.info(f"**ML Detection (Isolation Forest)**\n\n• {len(st.session_state.ml_anomalies)} anomalies\n• Statistical outlier detection\n• Unsupervised learning")
        
        with col3:
            st.info(f"**GNN Detection**\n\n• {len(st.session_state.gnn_anomalies)} anomalies\n• Graph-aware detection\n• Captures propagation patterns")
    
    def render_root_cause(self):
        """Render enhanced root cause panel with propagation path"""
        if st.session_state.root_cause:
            rc = st.session_state.root_cause
            
            # Build propagation path string
            path_str = " → ".join(st.session_state.propagation_path[:5]) if st.session_state.propagation_path else "None"
            
            st.markdown(f"""
            <div style="background: #111827;
                        padding: 20px; border-radius: 8px; margin: 14px 0;">
                <h3 style="color: #E5E7EB; margin: 0;">🎯 ROOT CAUSE ANALYSIS</h3>
                <hr style="background: rgba(255,255,255,0.06); margin: 12px 0; border: none; height: 1px;">
                <p style="color: #E5E7EB; margin: 5px 0 0 0; font-size: 18px;">
                    <strong>🚨 Primary Source:</strong> {rc['device_name']}
                </p>
                <p style="color: #9CA3AF; margin: 5px 0;">
                    <strong>📍 Layer:</strong> {rc['layer'].upper()} | 
                    <strong>⚠️ Severity:</strong> {rc['severity'].upper()} |
                    <strong>📊 Spike Ratio:</strong> {rc['spike_ratio']}x |
                    <strong>🔗 Connections:</strong> {rc.get('connection_count', 'N/A')}
                </p>
                <p style="color: #9CA3AF; margin: 10px 0 0 0; font-size: 14px;">
                    <strong>💡 Impact Analysis:</strong> {rc.get('impact_analysis', 'Device is primary anomaly source')}
                </p>
                <p style="color: #E5E7EB; margin: 10px 0 0 0; font-size: 14px; background: #0B0F14; padding: 10px; border-radius: 8px;">
                    <strong>🌊 Affected Path:</strong> {path_str}
                </p>
                <p style="color: #9CA3AF; margin: 8px 0 0 0; font-size: 12px;">
                    <strong>📊 Potential Impact Devices:</strong> {st.session_state.impact_devices}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.session_state.network_generated:
                st.success("✅ **No root cause detected** - Network operating within normal parameters")
    
    def render_telemetry_storage(self):
        """Render telemetry storage section"""
        if not st.session_state.storage:
            return
        
        st.markdown('<div class="hud-section-title telemetry-title">RECENT TELEMETRY STORAGE</div>', unsafe_allow_html=True)
        with st.expander("", expanded=True):
            df = st.session_state.storage.get_telemetry_history(limit=50)
            
            if not df.empty:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Total Records", len(df))
                with col2:
                    st.metric("🖥️ Unique Devices", df['device_id'].nunique())
                with col3:
                    last_time = df['timestamp'].iloc[-1][:19] if len(df) > 0 else "N/A"
                    st.metric("⏱️ Last Updated", last_time)
                
                st.subheader("Recent Telemetry Records")
                display_df = df.tail(10)[['timestamp', 'device_name', 'baseline_traffic', 
                                           'current_traffic', 'is_anomaly']]
                display_df.columns = ['Timestamp', 'Device', 'Baseline', 'Current', 'Anomaly']
                st.dataframe(display_df, use_container_width=True)
                
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
                "Severity": f"🔴 {anomaly['severity'].upper()}",
                "Detection": "Rule",
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
                "Severity": "🤖 ML",
                "Detection": "ML",
                "Details": f"Score: {anomaly.get('anomaly_score', 0):.2f}",
                "Reason": "Isolation Forest outlier detection"
            })
        
        # GNN anomalies
        for anomaly in st.session_state.gnn_anomalies:
            category = st.session_state.fingerprinter.get_device_category(anomaly['device_id']) if st.session_state.fingerprinter else "unknown"
            anomaly_data.append({
                "Device": anomaly['device_name'],
                "Layer": anomaly.get('layer', 'N/A').upper(),
                "Category": category.replace('_', ' ').title(),
                "Severity": "🕸️ GNN",
                "Detection": "GNN",
                "Details": f"Spike: {anomaly.get('spike_ratio', 0)}x | Neighbor: {anomaly.get('neighbor_avg_spike', 0)}x",
                "Reason": anomaly.get('reason', 'GNN detection')
            })
        
        df = pd.DataFrame(anomaly_data)
        
        def color_severity(val):
            if 'CRITICAL' in str(val):
                return 'color: #DC2626; font-weight: bold'
            elif 'HIGH' in str(val):
                return 'color: #D97706; font-weight: bold'
            return ''
        
        def color_detection(val):
            if val == 'Rule':
                return 'background-color: rgba(220, 38, 38, 0.14); color: #E5E7EB'
            elif val == 'ML':
                return 'background-color: rgba(37, 99, 235, 0.14); color: #E5E7EB'
            elif val == 'GNN':
                return 'background-color: rgba(217, 119, 6, 0.14); color: #E5E7EB'
            return ''
        
        styled_df = df.style.applymap(color_severity, subset=['Severity'])
        styled_df = styled_df.applymap(color_detection, subset=['Detection'])
        
        st.dataframe(styled_df, use_container_width=True, height=400)
    
    def run(self):
        """Main dashboard loop"""
        st.set_page_config(
            page_title="NetGraphIQ - Intelligent Network Monitor",
            page_icon="📡",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        collapsed = st.session_state.get("sidebar_collapsed", False)
        shell_class = "shell-collapsed" if collapsed else "shell-expanded"
        
        # Custom CSS for dark, minimal dashboard styling
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        :root {
            --bg: #020713;
            --panel: rgba(7, 28, 46, 0.76);
            --panel-strong: rgba(8, 42, 64, 0.92);
            --sidebar: rgba(5, 24, 39, 0.86);
            --text: #dffbff;
            --muted: #79b8c8;
            --accent: #22d3ee;
            --accent-hover: #58f3ff;
            --danger: #ff3f8f;
            --amber: #f59e0b;
        }

        .stApp {
            background:
                radial-gradient(circle at 52% 10%, rgba(34,211,238,0.18), transparent 24%),
                radial-gradient(circle at 0% 48%, rgba(126,58,242,0.23), transparent 31%),
                linear-gradient(rgba(34,211,238,0.09) 1px, transparent 1px),
                linear-gradient(90deg, rgba(34,211,238,0.09) 1px, transparent 1px),
                var(--bg);
            background-size: auto, auto, 74px 74px, 74px 74px, auto;
            color: var(--text);
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            line-height: 1.6;
        }

        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background:
                linear-gradient(90deg, rgba(2,7,19,0.1), transparent 18%, transparent 82%, rgba(2,7,19,0.55)),
                repeating-linear-gradient(0deg, rgba(255,255,255,0.03), rgba(255,255,255,0.03) 1px, transparent 1px, transparent 5px);
            z-index: 0;
        }

        .stApp * {
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            letter-spacing: 0;
        }

        .stale,
        [data-stale="true"],
        [data-stale="true"] > *,
        [data-testid="stAppViewContainer"] .stale,
        [data-testid="stAppViewContainer"] [data-stale="true"],
        [data-testid="stElementContainer"].stale,
        [data-testid="stElementContainer"][data-stale="true"],
        [data-testid="stVerticalBlock"].stale,
        [data-testid="stVerticalBlock"][data-stale="true"],
        div[data-testid="stExpander"][data-stale="true"],
        div[data-testid="stExpander"] details,
        div[data-testid="stExpander"] summary {
            opacity: 1 !important;
            filter: none !important;
            transition: none !important;
        }

        .block-container {
            max-width: none;
            padding-top: 0.65rem;
            padding-left: 1.35rem;
            padding-right: 1.35rem;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"] {
            background:
                linear-gradient(180deg, rgba(10, 74, 99, 0.22), rgba(6, 20, 35, 0.92)),
                var(--sidebar);
            border: none;
            box-shadow: inset -1px 0 0 rgba(34,211,238,0.28), 0 0 48px rgba(34,211,238,0.08);
        }

        section[data-testid="stSidebar"] {
            width: 240px !important;
            min-width: 240px !important;
            max-width: 240px !important;
            transition: width 0.3s ease, min-width 0.3s ease, max-width 0.3s ease;
            overflow-x: hidden;
            overflow-y: hidden;
            flex: 0 0 240px !important;
        }

        section[data-testid="stSidebar"] > div,
        [data-testid="stSidebarContent"] {
            width: 240px !important;
            min-width: 240px !important;
            max-width: 240px !important;
            transition: width 0.3s ease, min-width 0.3s ease, max-width 0.3s ease, padding 0.3s ease;
            overflow-x: hidden !important;
            overflow-y: auto !important;
            max-height: 100vh;
            scrollbar-width: thin;
            scrollbar-color: rgba(34,211,238,0.5) rgba(5,24,39,0.35);
        }

        [data-testid="stSidebarContent"]::-webkit-scrollbar {
            width: 6px;
        }

        [data-testid="stSidebarContent"]::-webkit-scrollbar-track {
            background: rgba(5,24,39,0.35);
        }

        [data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {
            background: rgba(34,211,238,0.5);
            border-radius: 999px;
        }

        section[data-testid="stSidebar"] button[title*="sidebar"],
        section[data-testid="stSidebar"] button[aria-label*="sidebar"],
        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
        section[data-testid="stSidebar"] [data-testid="collapsedControl"] {
            display: none !important;
        }

        section[data-testid="stSidebar"] button:has(span[class*="material-icons"]),
        section[data-testid="stSidebar"] button:has(span[class*="material-symbols"]) {
            font-size: 0 !important;
        }

        section[data-testid="stSidebar"] button:has(span[class*="material-icons"]) span,
        section[data-testid="stSidebar"] button:has(span[class*="material-symbols"]) span {
            display: none !important;
        }

        section[data-testid="stSidebar"]:has(.sidebar-state.collapsed) {
            width: 70px !important;
            min-width: 70px !important;
            max-width: 70px !important;
            flex: 0 0 70px !important;
        }

        section[data-testid="stSidebar"]:has(.sidebar-state.collapsed) > div,
        section[data-testid="stSidebar"]:has(.sidebar-state.collapsed) [data-testid="stSidebarContent"] {
            width: 70px !important;
            min-width: 70px !important;
            max-width: 70px !important;
            padding-left: 8px !important;
            padding-right: 8px !important;
        }

        section[data-testid="stSidebar"] + div,
        [data-testid="stAppViewContainer"] > .main {
            transition: margin-left 0.3s ease, width 0.3s ease;
        }

        [data-testid="stSidebarUserContent"] {
            overflow: visible;
            padding-bottom: 32px;
        }

        .sidebar {
            width: 240px;
            transition: width 0.3s ease;
        }

        .sidebar.collapsed {
            width: 70px;
        }

        .main-content {
            margin-left: 240px;
            transition: margin-left 0.3s ease;
        }

        .sidebar.collapsed + .main-content {
            margin-left: 70px;
        }

        section[data-testid="stSidebar"]:has(.sidebar-state.collapsed) .stButton > button {
            width: 44px;
            min-width: 44px;
            max-width: 44px;
            height: 44px;
            min-height: 44px;
            padding: 0;
            margin: 6px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
        }

        section[data-testid="stSidebar"]:has(.sidebar-state.collapsed) .stButton > button p {
            color: var(--text);
            font-size: 1rem;
            line-height: 1;
            margin: 0;
            width: auto;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: var(--text);
        }

        [data-testid="stSidebar"] h1 {
            font-size: 1.05rem;
            letter-spacing: 0.18em;
            text-transform: uppercase;
        }

        [data-testid="stSidebar"] h3 {
            color: #58f3ff;
            font-size: 0.68rem;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            margin-top: 1.25rem;
        }

        [data-testid="stSidebar"] hr,
        hr {
            border: none;
            height: 1px;
            background: rgba(255,255,255,0.06);
            margin: 1.2rem 0;
        }

        .main-header {
            padding: 20px 0 10px;
            background: transparent;
            margin-bottom: 6px;
        }

        .main-header h1 {
            color: var(--text);
            margin: 0;
            font-size: clamp(1.7rem, 3vw, 3.1rem);
            font-weight: 600;
            letter-spacing: 0.03em;
            text-shadow: 0 0 24px rgba(34,211,238,0.22);
        }

        .main-header p {
            color: var(--muted);
            margin: 8px 0 0 0;
            font-size: 0.92rem;
        }

        .topology-hero,
        .topology-frame,
        .chart-frame {
            position: relative;
            background: linear-gradient(180deg, rgba(8, 36, 58, 0.72), rgba(3, 12, 27, 0.86));
            border: 1px solid rgba(34,211,238,0.42);
            box-shadow: 0 0 28px rgba(34,211,238,0.13), inset 0 0 36px rgba(34,211,238,0.07);
            padding: 8px;
            margin: 8px 0 14px;
            clip-path: polygon(0 0, calc(100% - 28px) 0, 100% 28px, 100% 100%, 0 100%);
        }

        [data-testid="stPlotlyChart"] {
            min-height: 78vh;
            background:
                radial-gradient(circle at 50% 34%, rgba(34,211,238,0.12), transparent 30%),
                linear-gradient(rgba(34,211,238,0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(34,211,238,0.08) 1px, transparent 1px);
            background-size: auto, 68px 68px, 68px 68px;
            border: 1px solid rgba(34,211,238,0.32);
            box-shadow: inset 0 0 50px rgba(34,211,238,0.07), 0 0 30px rgba(34,211,238,0.1);
        }

        [data-testid="stTabs"] {
            margin-top: 1.2rem;
        }

        [data-testid="stTabs"] [data-baseweb="tab-panel"] {
            padding-top: 1.15rem;
            min-height: 260px;
            overflow: visible;
        }

        [data-testid="stTabs"] [role="tablist"] {
            gap: 0.35rem;
            border-bottom: 1px solid rgba(34,211,238,0.24);
        }

        [data-testid="stTabs"] [role="tab"] {
            background: rgba(8, 36, 58, 0.72);
            border: 1px solid rgba(34,211,238,0.24);
            border-bottom: none;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            min-height: 50px;
            padding: 0 14px;
            display: flex;
            align-items: center;
            white-space: nowrap;
        }

        [data-testid="stTabs"] [aria-selected="true"] {
            color: #dffbff;
            background: rgba(34,211,238,0.16);
            border-color: rgba(88,243,255,0.58);
        }

        .hud-section-title {
            color: #58f3ff;
            font-size: 0.76rem;
            letter-spacing: 0.24em;
            text-transform: uppercase;
            margin: 8px 0 10px;
            text-shadow: 0 0 12px rgba(34,211,238,0.45);
        }

        .metric-tile {
            background: linear-gradient(180deg, rgba(13, 57, 79, 0.82), rgba(8, 21, 39, 0.86));
            border: 1px solid rgba(34,211,238,0.32);
            border-radius: 2px;
            padding: 15px 13px;
            text-align: left;
            box-shadow: inset 0 0 22px rgba(34,211,238,0.08);
        }

        .metric-tile h3 {
            margin: 0;
            font-size: 1.55rem;
            font-weight: 500;
            text-shadow: 0 0 14px currentColor;
        }

        .metric-tile p {
            color: var(--muted);
            margin: 6px 0 0 0;
            font-size: 0.72rem;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        div[data-testid="stMetric"],
        div[data-testid="stAlert"],
        div[data-testid="stExpander"] {
            background: var(--panel);
            border: 1px solid rgba(34,211,238,0.22);
            border-radius: 2px;
            box-shadow: none;
        }

        div[data-testid="stExpander"] {
            margin-top: 0.75rem;
            margin-bottom: 2rem;
            overflow: visible;
        }

        div[data-testid="stExpander"] details {
            overflow: visible;
        }

        div[data-testid="stExpander"] summary {
            display: none;
        }

        div[data-testid="stExpander"] summary p {
            margin: 0;
            line-height: 1.35;
            color: var(--text);
        }

        div[data-testid="stExpanderDetails"] {
            padding-top: 1rem;
        }

        div[data-testid="stMetric"] {
            padding: 14px 16px;
        }

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricDelta"] {
            color: var(--muted);
        }

        div[data-testid="stMetricValue"],
        h1, h2, h3, h4, h5, h6 {
            color: var(--text);
        }

        p, label, span, .stMarkdown {
            color: var(--muted);
        }

        .stButton > button,
        [data-testid="stSidebar"] .stButton > button {
            background: linear-gradient(180deg, rgba(34,211,238,0.18), rgba(34,211,238,0.06));
            color: var(--text);
            border: 1px solid rgba(34,211,238,0.35);
            border-radius: 3px;
            box-shadow: inset 0 0 18px rgba(34,211,238,0.09), 0 0 14px rgba(34,211,238,0.08);
            transition: background 120ms ease, color 120ms ease;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }

        .stButton > button:hover,
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(34,211,238,0.2);
            color: var(--text);
            border: 1px solid rgba(88,243,255,0.72);
        }

        .stButton > button[kind="primary"],
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(180deg, rgba(34,211,238,0.32), rgba(34,211,238,0.12));
            color: #dffbff;
            border-color: rgba(88,243,255,0.8);
        }

        .stButton > button[kind="primary"]:hover,
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
            background: var(--accent-hover);
            color: #FFFFFF;
        }

        [data-testid="stSidebar"] .stButton > button:focus {
            background: rgba(37, 99, 235, 0.15);
            box-shadow: none;
        }

        [data-testid="stDataFrame"] {
            background: var(--panel);
            border: 1px solid rgba(34,211,238,0.25);
        }

        .stProgress > div > div > div > div {
            background-color: var(--accent);
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Title with minimal styling
        st.markdown("""
        <div class="main-header">
            <h1>NetGraphIQ: Complete Network Intelligence Platform</h1>
            <p>
                Multi-Layer Detection: Rule-Based | ML (Isolation Forest) | GNN (Graph Neural Network) | Live Packet Flow
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.network_generated:
            with st.spinner("Initializing network intelligence system..."):
                self.generate_network()
        
        show_anomalies, show_animation, attack_mode, auto_refresh, refresh_rate = self.render_sidebar()
        
        # Update network state
        rule_anomalies, ml_anomalies, gnn_anomalies = self.update_network_state(attack_mode)
        
        # Update packet flows
        if show_animation and st.session_state.packet_simulator:
            st.session_state.packet_simulator.update_flows(attack_mode)
        
        st.markdown('<div class="topology-hero">', unsafe_allow_html=True)
        st.markdown('<div class="hud-section-title">MULTI-LAYER INTELLIGENCE MAP</div>', unsafe_allow_html=True)
        fig_graph = self.draw_cyber_3d_topology()
        if fig_graph:
            st.plotly_chart(fig_graph, use_container_width=True, config={
                "displayModeBar": False,
                "scrollZoom": True,
                "responsive": True,
            })
        st.markdown('</div>', unsafe_allow_html=True)

        metrics_tab, traffic_tab, detection_tab, intelligence_tab, storage_tab = st.tabs([
            "System Metrics",
            "Traffic Analysis",
            "Detection Results",
            "Intelligence",
            "Telemetry Storage",
        ])

        with metrics_tab:
            self.render_metrics()
            self.draw_packet_flow_metrics()

        with traffic_tab:
            fig_traffic = self.draw_traffic_heatmap()
            if fig_traffic:
                st.pyplot(fig_traffic, use_container_width=True)

        with detection_tab:
            self.render_anomaly_table()

        with intelligence_tab:
            self.render_fingerprint_insights()
            self.render_detection_summary()
            self.render_root_cause()

        with storage_tab:
            self.render_telemetry_storage()
        
        # Footer
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"📡 NetGraphIQ v5.0 | Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")
        with col2:
            if attack_mode:
                st.caption("⚠️ Attack Mode: ACTIVE")
            else:
                st.caption("✅ Attack Mode: Inactive")
        with col3:
            total_anomalies = len(rule_anomalies) + len(ml_anomalies) + len(gnn_anomalies)
            st.caption(f"🚨 Total Alerts: {total_anomalies} (Rule: {len(rule_anomalies)}, ML: {len(ml_anomalies)}, GNN: {len(gnn_anomalies)})")
        
        # Keep the 3D model mounted. A full-page st.rerun() tears down the
        # Plotly/WebGL scene, which causes the visible disappear/reappear flicker.


def main():
    dashboard = IntegratedDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
