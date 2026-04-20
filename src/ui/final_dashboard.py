"""
NetGraphIQ - Final Intelligent Dashboard
Complete system with root cause detection, attack simulation, and enhanced live packet flow
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

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network_generator import NetworkGenerator
from src.core.telemetry_engine import TelemetryEngine
from src.core.anomaly_engine import AnomalyEngine


class PacketFlowSimulator:
    """Simulates live packet flow through the network with enhanced visualization"""
    
    def __init__(self, graph: nx.Graph, anomaly_ids: set = None):
        self.graph = graph
        self.anomaly_ids = anomaly_ids or set()
        self.active_edges = {}
        self.edge_flow_count = {}  # Track flow frequency per edge
        self.flow_counter = 0
        self.packet_positions = {}  # For animated packet dots
        self.flow_history = []
        
        # Initialize edge flow counts
        for edge in self.graph.edges():
            self.edge_flow_count[edge] = 0
            self.edge_flow_count[(edge[1], edge[0])] = 0
    
    def update_flows(self, attack_mode: bool = False):
        """Update active packet flows with enhanced simulation"""
        if not self.graph or self.graph.number_of_edges() == 0:
            return
        
        # Number of flows to simulate (more in attack mode)
        num_flows = random.randint(5, 12) if attack_mode else random.randint(3, 8)
        
        for _ in range(num_flows):
            edge = random.choice(list(self.graph.edges()))
            
            # Increment flow count for this edge
            self.edge_flow_count[edge] = self.edge_flow_count.get(edge, 0) + 1
            self.flow_counter += 1
            
            # Determine intensity based on anomalies and attack mode
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
            
            # Add packet position for animation
            self.packet_positions[self.flow_counter] = {
                'edge': edge,
                'progress': 0.0,
                'speed': random.uniform(0.5, 1.5)
            }
        
        # Update packet positions and remove expired flows
        current_time = time.time()
        expired = []
        
        for flow_id, flow_data in self.active_edges.items():
            if current_time - flow_data['start_time'] >= flow_data['duration']:
                expired.append(flow_id)
        
        for edge in expired:
            del self.active_edges[edge]
            # Remove associated packet positions
            to_remove = [fid for fid, pos in self.packet_positions.items() 
                        if pos['edge'] == edge]
            for fid in to_remove:
                del self.packet_positions[fid]
        
        # Update packet progress for active flows
        for flow_id, pos in self.packet_positions.items():
            pos['progress'] += pos['speed'] * 0.05
            if pos['progress'] >= 1.0:
                pos['progress'] = 0.0
    
    def get_edge_style(self, edge: Tuple) -> Tuple[str, float, float, int]:
        """Get edge style based on active flows and anomalies"""
        # Check if edge has active flow
        if edge in self.active_edges or (edge[1], edge[0]) in self.active_edges:
            flow_count = self.edge_flow_count.get(edge, 0)
            
            # More intense for high flow count
            if flow_count > 10:
                return '#FF4500', 5.0, 0.95, flow_count  # Bright red-orange
            elif flow_count > 5:
                return '#FF8C00', 4.0, 0.9, flow_count   # Orange
            else:
                return '#FFA500', 3.5, 0.85, flow_count   # Light orange
        
        # Check if edge connects to anomaly
        if edge[0] in self.anomaly_ids or edge[1] in self.anomaly_ids:
            return '#E74C3C', 2.5, 0.8, 0  # Red - anomaly connection
        
        # Normal edge
        return '#95A5A6', 1.2, 0.5, 0  # Gray - normal
    
    def get_flow_statistics(self) -> Dict:
        """Get packet flow statistics"""
        return {
            'total_flows': self.flow_counter,
            'active_flows': len(self.active_edges),
            'animated_packets': len(self.packet_positions),
            'most_active_edge': max(self.edge_flow_count.items(), key=lambda x: x[1])[0] if self.edge_flow_count else None,
            'total_packets': sum(self.edge_flow_count.values())
        }


class FinalDashboard:
    """Complete intelligent dashboard with all features"""
    
    def __init__(self):
        self._init_session_state()
    
    def _init_session_state(self):
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
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
    
    def generate_network(self):
        """Generate complete network topology"""
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
            
            # Initialize engines
            telemetry = TelemetryEngine(devices)
            anomaly_engine = AnomalyEngine(devices)
            packet_simulator = PacketFlowSimulator(graph, set())
            
            st.session_state.devices = devices
            st.session_state.connections = connections
            st.session_state.graph = graph
            st.session_state.telemetry = telemetry
            st.session_state.anomaly_engine = anomaly_engine
            st.session_state.packet_simulator = packet_simulator
            st.session_state.network_generated = True
            
            return True
        return False
    
    def update_network_state(self, attack_mode: bool):
        """Update telemetry and detect anomalies"""
        if not st.session_state.devices:
            return
        
        # Adjust anomaly rate based on attack mode
        anomaly_rate = 0.30 if attack_mode else 0.12
        
        # Generate telemetry
        current_metrics = st.session_state.telemetry.generate_telemetry(
            inject_anomalies=True,
            anomaly_rate=anomaly_rate
        )
        
        # Detect anomalies
        anomalies = st.session_state.anomaly_engine.detect_anomalies(current_metrics)
        st.session_state.anomalies = anomalies
        
        # Update packet simulator with anomaly IDs
        anomaly_ids = {a['device_id'] for a in anomalies}
        st.session_state.packet_simulator.anomaly_ids = anomaly_ids
        
        # Find root cause using the anomaly engine's method
        if st.session_state.graph and anomalies:
            st.session_state.root_cause = st.session_state.anomaly_engine.find_root_cause(
                anomalies, st.session_state.graph
            )
        else:
            st.session_state.root_cause = None
        
        st.session_state.last_update = datetime.now()
        st.session_state.attack_mode = attack_mode
        
        return anomalies
    
    def draw_network_graph(self):
        """Draw network topology with anomaly highlighting and packet flow"""
        if not st.session_state.graph:
            return None
        
        fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')
        
        # Calculate layout
        pos = nx.spring_layout(st.session_state.graph, k=2, iterations=50, seed=42)
        
        # Get anomaly IDs
        anomaly_ids = {a['device_id'] for a in st.session_state.anomalies}
        
        # Draw edges with styles based on packet flow
        for edge in st.session_state.graph.edges():
            color, width, alpha, flow_count = st.session_state.packet_simulator.get_edge_style(edge)
            
            # Add glow effect for high-flow edges
            if flow_count > 5:
                # Draw glow
                nx.draw_networkx_edges(
                    st.session_state.graph, pos,
                    edgelist=[edge],
                    edge_color=color,
                    width=width + 2,
                    alpha=0.3,
                    ax=ax
                )
            
            # Draw main edge
            nx.draw_networkx_edges(
                st.session_state.graph, pos,
                edgelist=[edge],
                edge_color=color,
                width=width,
                alpha=alpha,
                ax=ax
            )
            
            # Draw animated packets on active edges
            if edge in st.session_state.packet_simulator.active_edges or \
               (edge[1], edge[0]) in st.session_state.packet_simulator.active_edges:
                
                # Get packet position
                for flow_id, packet in st.session_state.packet_simulator.packet_positions.items():
                    if packet['edge'] == edge or packet['edge'] == (edge[1], edge[0]):
                        # Calculate packet position along edge
                        x0, y0 = pos[edge[0]]
                        x1, y1 = pos[edge[1]]
                        t = packet['progress']
                        px = x0 + t * (x1 - x0)
                        py = y0 + t * (y1 - y0)
                        
                        # Draw packet as a dot
                        ax.scatter(px, py, c='#FFD700', s=50, zorder=5, 
                                  edgecolors='black', linewidths=1)
        
        # Separate nodes
        normal_nodes = [n for n in st.session_state.graph.nodes() if n not in anomaly_ids]
        anomaly_nodes = [n for n in st.session_state.graph.nodes() if n in anomaly_ids]
        
        # Draw normal nodes
        if normal_nodes:
            nx.draw_networkx_nodes(
                st.session_state.graph, pos,
                nodelist=normal_nodes,
                node_color='#4A90E2',
                node_size=450,
                alpha=0.85,
                edgecolors='black',
                linewidths=1.5,
                ax=ax
            )
        
        # Draw anomaly nodes (larger, red, with glow)
        if anomaly_nodes:
            # Outer glow
            nx.draw_networkx_nodes(
                st.session_state.graph, pos,
                nodelist=anomaly_nodes,
                node_color='#E74C3C',
                node_size=700,
                alpha=0.3,
                ax=ax
            )
            # Main node
            nx.draw_networkx_nodes(
                st.session_state.graph, pos,
                nodelist=anomaly_nodes,
                node_color='#E74C3C',
                node_size=550,
                alpha=0.95,
                edgecolors='darkred',
                linewidths=2.5,
                ax=ax
            )
        
        # Draw labels
        labels = {}
        for node in st.session_state.graph.nodes():
            name = st.session_state.graph.nodes[node].get('name', node)
            if len(name) > 15:
                name = name[:12] + '..'
            
            # Add severity indicator for anomalies
            if node in anomaly_ids:
                for anomaly in st.session_state.anomalies:
                    if anomaly['device_id'] == node:
                        severity = anomaly['severity'][:1].upper()
                        name = f"⚠️ {name} [{severity}]"
                        break
            
            labels[node] = name
        
        nx.draw_networkx_labels(
            st.session_state.graph, pos,
            labels=labels,
            font_size=8,
            font_weight='bold',
            ax=ax
        )
        
        ax.set_title("🌐 Live Network Topology with Anomaly Detection & Packet Flow", 
                    fontsize=14, fontweight='bold')
        ax.axis('off')
        
        # Enhanced Legend
        legend_elements = [
            Patch(facecolor='#4A90E2', edgecolor='black', label='Normal Device'),
            Patch(facecolor='#E74C3C', edgecolor='darkred', label='⚠️ Anomalous Device'),
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
        """Draw enhanced packet flow metrics panel"""
        if not st.session_state.packet_simulator:
            return None
        
        stats = st.session_state.packet_simulator.get_flow_statistics()
        
        # Create metrics in a grid
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "📦 Total Packets Sent",
                stats['total_packets'],
                delta=f"+{stats['active_flows']} active"
            )
        
        with col2:
            st.metric(
                "⚡ Active Flows",
                stats['active_flows'],
                delta="🔴 High" if st.session_state.attack_mode else "🟢 Normal"
            )
        
        with col3:
            st.metric(
                "✨ Animated Packets",
                stats['animated_packets'],
                delta="Moving"
            )
        
        with col4:
            if stats['most_active_edge']:
                edge = stats['most_active_edge']
                # Get device names if possible
                st.metric(
                    "🔥 Busiest Link",
                    f"{edge[0][:8]}→{edge[1][:8]}",
                    delta=f"{stats['total_flows']} flows"
                )
            else:
                st.metric("🔥 Busiest Link", "None", delta="No traffic")
        
        # Add traffic intensity gauge
        st.progress(min(1.0, stats['active_flows'] / 20), 
                   text=f"📊 Network Traffic Intensity: {stats['active_flows']} active flows")
    
    def draw_traffic_heatmap(self):
        """Draw real-time traffic heatmap by layer"""
        if not st.session_state.devices:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Calculate traffic by layer
        layer_traffic = {'edge': 0, 'core': 0, 'access': 0, 'endpoint': 0}
        layer_counts = {'edge': 0, 'core': 0, 'access': 0, 'endpoint': 0}
        
        for device_id, device in st.session_state.devices.items():
            layer = device.layer.value if hasattr(device, 'layer') else 'unknown'
            if layer in layer_traffic:
                baseline = device.baseline_traffic
                layer_traffic[layer] += baseline
                layer_counts[layer] += 1
        
        # Calculate averages
        for layer in layer_traffic:
            if layer_counts[layer] > 0:
                layer_traffic[layer] /= layer_counts[layer]
        
        layers = ['EDGE', 'CORE', 'ACCESS', 'ENDPOINT']
        values = [layer_traffic['edge'], layer_traffic['core'], 
                  layer_traffic['access'], layer_traffic['endpoint']]
        
        # Color based on anomaly presence
        anomaly_layers = {a['layer'] for a in st.session_state.anomalies}
        colors = ['#E74C3C' if layer.lower() in anomaly_layers else '#4A90E2' 
                  for layer in layers]
        
        bars = ax.bar(layers, values, color=colors, alpha=0.8)
        ax.set_ylabel('Avg Traffic (pkts/sec)')
        ax.set_title('Network Layer Traffic Distribution')
        
        # Add value labels
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 5,
                   f'{value:.0f}', ha='center', va='bottom', fontsize=9)
        
        # Add packet flow overlay
        flow_stats = st.session_state.packet_simulator.get_flow_statistics()
        ax.text(0.98, 0.95, f"📡 Active Flows: {flow_stats['active_flows']}", 
               transform=ax.transAxes, ha='right', va='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.title("🎮 NetGraphIQ Controls")
        
        if st.sidebar.button("🔄 Generate New Network", use_container_width=True, type="primary"):
            self.generate_network()
            st.rerun()
        
        st.sidebar.divider()
        
        st.sidebar.subheader("⚙️ Display Settings")
        show_anomalies = st.sidebar.toggle("🔴 Show Anomalies", value=True)
        show_animation = st.sidebar.toggle("✨ Live Packet Animation", value=True)
        
        st.sidebar.divider()
        
        st.sidebar.subheader("🎯 Attack Simulation")
        attack_mode = st.sidebar.toggle(
            "⚠️ Simulate Attack Mode",
            value=False,
            help="Increases anomaly probability (30%) and traffic intensity (3.5-6x baseline)"
        )
        
        if attack_mode:
            st.sidebar.warning("🔴 **ATTACK MODE ACTIVE**\n\n• 30% anomaly probability\n• 3.5-6x traffic spikes\n• Simulating DDoS/Abnormal traffic")
        
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
        
        return show_anomalies, show_animation, attack_mode, auto_refresh, refresh_rate
    
    def render_metrics(self):
        """Render enhanced metrics panel with highlighting"""
        st.markdown("### 📊 System Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🖥️ Total Devices",
                len(st.session_state.devices) if st.session_state.devices else 0,
                help="Total number of devices in the network"
            )
        
        with col2:
            st.metric(
                "🔗 Connections",
                len(st.session_state.connections) if st.session_state.connections else 0,
                help="Total number of network connections"
            )
        
        with col3:
            anomaly_count = len(st.session_state.anomalies)
            delta = f"+{anomaly_count}" if anomaly_count > 0 else None
            st.metric(
                "⚠️ Active Anomalies",
                anomaly_count,
                delta=delta,
                delta_color="inverse",
                help="Number of devices with abnormal behavior"
            )
        
        with col4:
            active_flows = len(st.session_state.packet_simulator.active_edges) if st.session_state.packet_simulator else 0
            st.metric(
                "📡 Active Flows",
                active_flows,
                delta="🚨 HIGH" if st.session_state.attack_mode else "🟢 NORMAL",
                help="Number of active packet flows in the network"
            )
        
        # Add highlighted metrics row
        st.markdown("---")
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            severity_counts = {}
            for a in st.session_state.anomalies:
                severity_counts[a['severity']] = severity_counts.get(a['severity'], 0) + 1
            
            critical_count = severity_counts.get('critical', 0)
            st.metric(
                "🔴 Critical Alerts",
                critical_count,
                delta="URGENT" if critical_count > 0 else None,
                help="Critical severity anomalies requiring immediate attention"
            )
        
        with col6:
            if st.session_state.root_cause:
                st.metric(
                    "🎯 Root Cause",
                    st.session_state.root_cause['device_name'][:20],
                    help="Primary source of anomalies"
                )
            else:
                st.metric("🎯 Root Cause", "None Detected", help="No root cause identified")
        
        with col7:
            # Calculate network health percentage
            total_devices = len(st.session_state.devices) if st.session_state.devices else 1
            health_percent = max(0, 100 - (anomaly_count * 5))
            st.metric(
                "💚 Network Health",
                f"{health_percent}%",
                delta="Good" if health_percent > 80 else "Degraded",
                help="Overall network health score"
            )
        
        with col8:
            if st.session_state.attack_mode:
                st.metric("⚠️ Attack Mode", "ACTIVE", delta="DDoS Simulation", delta_color="inverse")
            else:
                st.metric("✅ Attack Mode", "Inactive", help="No active attack simulation")
    
    def render_root_cause(self):
        """Render root cause detection panel"""
        if st.session_state.root_cause:
            rc = st.session_state.root_cause
            
            # Create warning box
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
    
    def render_anomaly_table(self):
        """Render anomalies table"""
        if not st.session_state.anomalies:
            st.info("✅ No active anomalies - All devices operating normally")
            return
        
        anomaly_data = []
        for anomaly in st.session_state.anomalies:
            anomaly_data.append({
                "Device": anomaly['device_name'],
                "Layer": anomaly['layer'].upper(),
                "Severity": anomaly['severity'].upper(),
                "Current": f"{anomaly['current_traffic']} pkts/sec",
                "Baseline": f"{anomaly['baseline_traffic']} pkts/sec",
                "Spike": f"{anomaly['spike_ratio']}x",
                "Description": anomaly['description']
            })
        
        df = pd.DataFrame(anomaly_data)
        
        # Color coding function
        def color_severity(val):
            if 'CRITICAL' in str(val):
                return 'background-color: #ff4444; color: white'
            elif 'HIGH' in str(val):
                return 'background-color: #ff8888'
            elif 'MEDIUM' in str(val):
                return 'background-color: #ffcc88'
            return ''
        
        st.dataframe(
            df.style.applymap(color_severity, subset=['Severity']),
            use_container_width=True,
            height=250
        )
    
    def run(self):
        """Main dashboard loop"""
        st.set_page_config(
            page_title="NetGraphIQ - Intelligent Network Monitor",
            page_icon="📡",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Title
        st.title("📡 NetGraphIQ: Intelligent Network Monitoring Platform")
        st.markdown("*Real-time topology discovery · Anomaly detection · Root cause analysis · Live packet flow simulation*")
        st.divider()
        
        # Generate initial network if needed
        if not st.session_state.network_generated:
            with st.spinner("Initializing network intelligence system..."):
                self.generate_network()
        
        # Render sidebar
        show_anomalies, show_animation, attack_mode, auto_refresh, refresh_rate = self.render_sidebar()
        
        # Update network state
        self.update_network_state(attack_mode)
        
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
            
            # Attack mode indicator
            if attack_mode:
                st.warning("⚠️ **ATTACK SIMULATION ACTIVE**\n\n• High anomaly probability (30%)\n• Elevated traffic spikes (3.5-6x baseline)\n• Simulated DDoS/Abnormal traffic patterns")
        
        # Metrics row with highlighting
        st.divider()
        self.render_metrics()
        
        # Root cause section
        st.divider()
        self.render_root_cause()
        
        # Anomaly table
        st.subheader("🚨 Active Anomalies")
        self.render_anomaly_table()
        
        # Footer
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"📡 NetGraphIQ v2.0 | Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")
        with col2:
            if attack_mode:
                st.caption("⚠️ Attack Mode: ACTIVE")
            else:
                st.caption("✅ Attack Mode: Inactive")
        with col3:
            anomaly_count = len(st.session_state.anomalies)
            if anomaly_count > 0:
                st.caption(f"🚨 Active Alerts: {anomaly_count}")
            else:
                st.caption("✅ System Health: Normal")
        
        # Auto refresh
        if auto_refresh and refresh_rate:
            time.sleep(refresh_rate)
            st.rerun()


def main():
    dashboard = FinalDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()