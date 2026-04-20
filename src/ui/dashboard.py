"""
Advanced Dashboard - Live Network Monitoring with Packet Flow Simulation
Uses Streamlit for interactive web interface
"""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from matplotlib.patches import Patch
import random
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Tuple, Optional
import numpy as np

# Import project modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.network_generator import NetworkGenerator
from src.core.telemetry_engine import TelemetryEngine
from src.core.anomaly_engine import AnomalyEngine
from src.visualization.graph_viz import GraphVisualizer


class PacketFlowSimulator:
    """
    Simulates packet flow through network connections
    Creates animated visualization of network traffic
    """
    
    def __init__(self, graph: nx.Graph, anomaly_ids: set = None):
        self.graph = graph
        self.anomaly_ids = anomaly_ids or set()
        self.active_flows = {}
        self.flow_history = []
        
    def get_edge_traffic_intensity(self, edge: Tuple) -> float:
        """
        Calculate traffic intensity for an edge
        Higher for edges connected to anomalies
        """
        intensity = 0.5  # Base intensity
        
        # Increase intensity if edge connects to anomaly
        if edge[0] in self.anomaly_ids or edge[1] in self.anomaly_ids:
            intensity += random.uniform(0.3, 0.7)
        
        # Add random variation
        intensity += random.uniform(-0.2, 0.2)
        
        return max(0.2, min(1.0, intensity))
    
    def get_edge_color_for_traffic(self, intensity: float) -> str:
        """Get edge color based on traffic intensity"""
        if intensity > 0.8:
            return "#FF0000"  # Red - heavy traffic
        elif intensity > 0.6:
            return "#FF6B6B"  # Light red - medium-heavy
        elif intensity > 0.4:
            return "#4ECDC4"  # Teal - normal traffic
        else:
            return "#95A5A6"  # Gray - light traffic
    
    def get_edge_width_for_traffic(self, intensity: float) -> float:
        """Get edge width based on traffic intensity"""
        return 1.5 + (intensity * 3)  # 1.5 to 4.5 width


class LiveDashboard:
    """
    Main dashboard controller - coordinates all visualization components
    """
    
    def __init__(self):
        """Initialize dashboard state"""
        self.devices = {}
        self.connections = []
        self.graph = None
        self.telemetry = None
        self.anomaly_engine = None
        self.packet_simulator = None
        self.visualizer = None
        
        # Initialize session state
        self._init_session_state()
        
    def _init_session_state(self):
        """Initialize Streamlit session state"""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            st.session_state.devices = None
            st.session_state.connections = None
            st.session_state.anomalies = []
            st.session_state.metrics_history = []
            st.session_state.packet_animation = True
            st.session_state.show_anomalies = True
            st.session_state.last_update = datetime.now()
    
    def generate_network(self):
        """Generate or regenerate the network"""
        with st.spinner("🌐 Generating network topology..."):
            generator = NetworkGenerator()
            self.devices, self.connections = generator.generate_enterprise_network()
            
            # Build graph
            self.graph = nx.Graph()
            for device_id, device in self.devices.items():
                self.graph.add_node(
                    device_id,
                    name=device.name,
                    type=device.device_type.value,
                    layer=device.layer.value
                )
            for conn in self.connections:
                self.graph.add_edge(conn.source_id, conn.target_id)
            
            # Initialize telemetry and anomaly detection
            self.telemetry = TelemetryEngine(self.devices)
            self.anomaly_engine = AnomalyEngine(self.devices)
            
            # Initialize packet simulator
            self.packet_simulator = PacketFlowSimulator(self.graph, set())
            
            # Update session state
            st.session_state.devices = self.devices
            st.session_state.connections = self.connections
            st.session_state.generated = True
            
            return True
        return False
    
    def update_telemetry(self):
        """Update telemetry and detect anomalies"""
        if not self.devices:
            return
        
        # Generate new telemetry
        current_metrics = self.telemetry.generate_telemetry(
            inject_anomalies=True,
            anomaly_rate=0.15
        )
        
        # Detect anomalies
        anomalies = self.anomaly_engine.detect_anomalies(current_metrics)
        
        # Update packet simulator with anomaly IDs
        anomaly_ids = {a['device_id'] for a in anomalies}
        self.packet_simulator.anomaly_ids = anomaly_ids
        
        # Store in session state
        st.session_state.anomalies = anomalies
        st.session_state.current_metrics = current_metrics
        st.session_state.last_update = datetime.now()
        
        # Store in history
        st.session_state.metrics_history.append({
            'timestamp': datetime.now(),
            'anomaly_count': len(anomalies),
            'total_devices': len(self.devices)
        })
        
        # Keep last 100 entries
        if len(st.session_state.metrics_history) > 100:
            st.session_state.metrics_history = st.session_state.metrics_history[-100:]
        
        return anomalies
    
    def create_network_graph_figure(self):
        """
        Create interactive Plotly figure for network graph
        """
        if not self.graph:
            return None
        
        # Get positions for nodes
        pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
        
        # Create edge traces
        edge_traces = []
        
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            # Determine edge color based on anomalies
            anomaly_ids = {a['device_id'] for a in st.session_state.anomalies}
            if edge[0] in anomaly_ids or edge[1] in anomaly_ids:
                edge_color = '#FF0000'
                edge_width = 3
            else:
                edge_color = '#888888'
                edge_width = 1
            
            edge_trace = go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode='lines',
                line=dict(width=edge_width, color=edge_color),
                hoverinfo='none',
                showlegend=False
            )
            edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        node_sizes = []
        
        anomaly_ids = {a['device_id'] for a in st.session_state.anomalies}
        
        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            device = self.devices.get(node)
            if device:
                # Node text
                node_text.append(f"{device.name}<br>Type: {device.device_type.value}<br>Layer: {device.layer.value}")
                
                # Node color based on anomaly
                if node in anomaly_ids:
                    node_colors.append('#FF0000')
                    node_sizes.append(25)
                else:
                    node_colors.append('#4A90E2')
                    node_sizes.append(15)
            else:
                node_text.append(node)
                node_colors.append('#888888')
                node_sizes.append(10)
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[self.graph.nodes[n].get('name', n)[:15] for n in self.graph.nodes()],
            textposition="top center",
            hovertext=node_text,
            hoverinfo='text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='DarkSlateGrey')
            ),
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace],
                       layout=go.Layout(
                           title=dict(
                               text="🌐 Network Topology with Anomalies",
                               font=dict(size=16)
                           ),
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           height=500,
                           plot_bgcolor='white'
                       ))
        
        return fig
    
    def create_packet_flow_figure(self):
        """
        Create animated packet flow visualization
        Uses matplotlib for animation
        """
        if not self.graph:
            return None
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Get positions
        pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
        
        # Draw nodes
        anomaly_ids = {a['device_id'] for a in st.session_state.anomalies}
        
        node_colors = []
        node_sizes = []
        for node in self.graph.nodes():
            if node in anomaly_ids:
                node_colors.append('#FF0000')
                node_sizes.append(500)
            else:
                node_colors.append('#4A90E2')
                node_sizes.append(300)
        
        nx.draw_networkx_nodes(self.graph, pos, ax=ax,
                              node_color=node_colors,
                              node_size=node_sizes,
                              alpha=0.9,
                              edgecolors='black',
                              linewidths=2)
        
        # Draw edges with traffic-based styling
        for edge in self.graph.edges():
            intensity = self.packet_simulator.get_edge_traffic_intensity(edge)
            edge_color = self.packet_simulator.get_edge_color_for_traffic(intensity)
            edge_width = self.packet_simulator.get_edge_width_for_traffic(intensity)
            
            nx.draw_networkx_edges(self.graph, pos, ax=ax,
                                  edgelist=[edge],
                                  edge_color=edge_color,
                                  width=edge_width,
                                  alpha=0.7)
        
        # Draw labels
        labels = {node: self.graph.nodes[node].get('name', node)[:12] 
                 for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, ax=ax,
                               labels=labels,
                               font_size=8,
                               font_weight='bold')
        
        # Add title
        ax.set_title("📡 Live Packet Flow Simulation", fontsize=14, fontweight='bold')
        ax.axis('off')
        
        # Add legend
        legend_elements = [
            Patch(facecolor='#4A90E2', edgecolor='black', label='Normal Device'),
            Patch(facecolor='#FF0000', edgecolor='black', label='⚠️ Anomalous Device'),
            plt.Line2D([0], [0], color='#95A5A6', linewidth=2, label='Light Traffic'),
            plt.Line2D([0], [0], color='#4ECDC4', linewidth=3, label='Normal Traffic'),
            plt.Line2D([0], [0], color='#FF6B6B', linewidth=4, label='Heavy Traffic'),
            plt.Line2D([0], [0], color='#FF0000', linewidth=5, label='⚠️ Anomaly Traffic')
        ]
        ax.legend(handles=legend_elements, loc='upper left', 
                 bbox_to_anchor=(1.02, 1), fontsize=8)
        
        plt.tight_layout()
        return fig
    
    def render_sidebar(self):
        """Render sidebar controls"""
        st.sidebar.title("🎮 Dashboard Controls")
        
        if st.sidebar.button("🔄 Generate New Network", use_container_width=True):
            self.generate_network()
            st.rerun()
        
        st.sidebar.divider()
        
        st.sidebar.subheader("⚙️ Display Options")
        show_anomalies = st.sidebar.toggle("🔴 Show Anomalies", value=True)
        show_animation = st.sidebar.toggle("✨ Show Packet Animation", value=True)
        auto_refresh = st.sidebar.toggle("🔄 Auto Refresh", value=True)
        
        if auto_refresh:
            refresh_rate = st.sidebar.select_slider(
                "Refresh Rate (seconds)",
                options=[1, 2, 3, 5, 10],
                value=3
            )
        else:
            refresh_rate = None
        
        st.sidebar.divider()
        
        st.sidebar.subheader("ℹ️ System Info")
        st.sidebar.info(
            f"**Network Status:**\n"
            f"• Devices: {len(self.devices)}\n"
            f"• Connections: {len(self.connections)}\n"
            f"• Anomalies: {len(st.session_state.anomalies)}\n"
            f"• Last Update: {st.session_state.last_update.strftime('%H:%M:%S')}"
        )
        
        return show_anomalies, show_animation, auto_refresh, refresh_rate
    
    def render_metrics(self):
        """Render metrics panel"""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🖥️ Total Devices",
                len(self.devices),
                delta=None
            )
        
        with col2:
            st.metric(
                "🔗 Connections",
                len(self.connections),
                delta=None
            )
        
        with col3:
            anomaly_count = len(st.session_state.anomalies)
            st.metric(
                "⚠️ Anomalies",
                anomaly_count,
                delta=f"-{anomaly_count}" if anomaly_count > 0 else None,
                delta_color="inverse"
            )
        
        with col4:
            # Calculate active flows
            active_flows = len(self.packet_simulator.active_flows) if self.packet_simulator else 0
            st.metric(
                "📡 Active Flows",
                active_flows,
                delta="+5" if active_flows > 0 else None
            )
    
    def render_anomaly_table(self):
        """Render anomalies table"""
        if not st.session_state.anomalies:
            st.info("✅ No active anomalies detected. All systems operational.")
            return
        
        # Create DataFrame
        anomaly_data = []
        for anomaly in st.session_state.anomalies:
            anomaly_data.append({
                "Device": anomaly['device_name'],
                "Layer": anomaly['layer'].upper(),
                "Severity": anomaly['severity'].upper(),
                "Current Traffic": f"{anomaly['current_traffic']} pkts/sec",
                "Baseline": f"{anomaly['baseline_traffic']} pkts/sec",
                "Spike Ratio": f"{anomaly['spike_ratio']}x",
                "Description": anomaly['description'][:50] + "..."
            })
        
        df = pd.DataFrame(anomaly_data)
        
        # Color code severity
        def color_severity(val):
            colors = {
                'CRITICAL': 'background-color: #FF0000; color: white',
                'HIGH': 'background-color: #FF6B6B',
                'MEDIUM': 'background-color: #FFE66D',
                'LOW': 'background-color: #4ECDC4'
            }
            return colors.get(val, '')
        
        st.dataframe(
            df.style.applymap(color_severity, subset=['Severity']),
            use_container_width=True,
            height=300
        )
    
    def run(self):
        """Main dashboard loop"""
        # Page config
        st.set_page_config(
            page_title="NetGraphIQ - Live Network Monitor",
            page_icon="📡",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Title
        st.title("📡 NetGraphIQ: Live Network Monitoring Platform")
        st.markdown("*Real-time topology discovery, anomaly detection, and packet flow simulation*")
        st.divider()
        
        # Generate network if not exists
        if not self.devices:
            with st.spinner("Initializing network..."):
                self.generate_network()
        
        # Render sidebar and get controls
        show_anomalies, show_animation, auto_refresh, refresh_rate = self.render_sidebar()
        
        # Update telemetry
        if auto_refresh:
            self.update_telemetry()
        
        # Main content - 2 columns
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.subheader("🌐 Network Topology")
            fig_graph = self.create_network_graph_figure()
            if fig_graph:
                st.plotly_chart(fig_graph, use_container_width=True)
        
        with col_right:
            st.subheader("📡 Live Packet Flow Simulation")
            if show_animation:
                fig_flow = self.create_packet_flow_figure()
                if fig_flow:
                    st.pyplot(fig_flow)
                
                # Simulate packet movement
                if self.packet_simulator and auto_refresh:
                    # Randomly select edges to simulate packets
                    if self.graph and self.graph.edges():
                        for _ in range(3):  # Simulate 3 packets per refresh
                            edge = random.choice(list(self.graph.edges()))
                            self.packet_simulator.active_flows[edge] = datetime.now()
                            
                            # Remove old flows
                            current_time = datetime.now()
                            self.packet_simulator.active_flows = {
                                k: v for k, v in self.packet_simulator.active_flows.items()
                                if (current_time - v).seconds < 2
                            }
            else:
                st.info("Packet animation is disabled. Toggle 'Show Packet Animation' to enable.")
        
        # Metrics row
        st.divider()
        st.subheader("📊 System Metrics")
        self.render_metrics()
        
        # Anomaly table
        st.subheader("🚨 Active Anomalies")
        self.render_anomaly_table()
        
        # Auto-refresh logic
        if auto_refresh and refresh_rate:
            time.sleep(refresh_rate)
            st.rerun()


def main():
    """Entry point for dashboard"""
    dashboard = LiveDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()