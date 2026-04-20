"""
Graph Visualization Module - Displays network topology with anomaly highlighting
Uses NetworkX for graph structure and Matplotlib for rendering
"""

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from typing import Dict, List, Tuple, Optional
import numpy as np


class GraphVisualizer:
    """
    Visualizes network topology with anomaly highlighting
    """
    
    # Color scheme
    COLORS = {
        'normal': '#4A90E2',      # Soft blue for normal devices
        'anomaly': '#E74C3C',     # Bright red for anomalies
        'edge_normal': '#95A5A6',  # Light gray for normal edges
        'edge_anomaly': '#E74C3C',  # Red for edges connected to anomalies
        'background': '#FFFFFF',   # White background
        'text': '#2C3E50'          # Dark gray for text
    }
    
    # Node size mapping by device type (larger for critical devices)
    NODE_SIZES = {
        'router': 700,      # Reduced from 800
        'core_switch': 600,  # Reduced from 700
        'access_switch': 450, # Reduced from 500
        'iot_device': 250     # Reduced from 300
    }
    
    # Node shape mapping
    NODE_SHAPES = {
        'router': 's',      # Square for routers
        'core_switch': '^',  # Triangle for core switches
        'access_switch': 'o', # Circle for access switches
        'iot_device': 'v'     # Downward triangle for IoT
    }
    
    def __init__(self, devices: Dict, connections: List, anomalies: List = None):
        """
        Initialize visualizer with network data
        
        Args:
            devices: Dictionary of device objects (id -> Device)
            connections: List of Connection objects
            anomalies: List of anomaly dictionaries (from AnomalyEngine)
        """
        self.devices = devices
        self.connections = connections
        self.anomalies = anomalies or []
        self.graph = nx.Graph()
        self.anomaly_ids = self._get_anomaly_ids()
        
        # Build the graph
        self._build_graph()
        
    def _get_anomaly_ids(self) -> set:
        """Extract device IDs from anomaly list"""
        anomaly_ids = set()
        for anomaly in self.anomalies:
            if 'device_id' in anomaly:
                anomaly_ids.add(anomaly['device_id'])
            elif 'device' in anomaly and hasattr(anomaly['device'], 'id'):
                anomaly_ids.add(anomaly['device'].id)
        return anomaly_ids
    
    def _get_edges_connected_to_anomalies(self) -> set:
        """Get all edges that are connected to at least one anomalous device"""
        anomaly_edges = set()
        for edge in self.graph.edges():
            if edge[0] in self.anomaly_ids or edge[1] in self.anomaly_ids:
                anomaly_edges.add(edge)
        return anomaly_edges
    
    def _build_graph(self):
        """Build NetworkX graph from devices and connections"""
        # Add nodes with attributes
        for device_id, device in self.devices.items():
            # Determine if device has anomaly
            is_anomaly = device_id in self.anomaly_ids
            
            # Get node attributes
            node_attrs = {
                'name': device.name,
                'type': device.device_type.value if hasattr(device, 'device_type') else 'unknown',
                'layer': device.layer.value if hasattr(device, 'layer') else 'unknown',
                'is_anomaly': is_anomaly,
                'baseline': round(device.baseline_traffic, 2) if hasattr(device, 'baseline_traffic') else 0
            }
            
            # Add anomaly-specific attributes if applicable
            if is_anomaly:
                anomaly_data = self._get_anomaly_data(device_id)
                if anomaly_data:
                    node_attrs['severity'] = anomaly_data.get('severity', 'unknown')
                    node_attrs['current_traffic'] = anomaly_data.get('current_traffic', 0)
                    node_attrs['spike_ratio'] = anomaly_data.get('spike_ratio', 0)
            
            self.graph.add_node(device_id, **node_attrs)
        
        # Add edges
        for conn in self.connections:
            self.graph.add_edge(conn.source_id, conn.target_id)
    
    def _get_anomaly_data(self, device_id: str) -> Optional[Dict]:
        """Get anomaly details for a device"""
        for anomaly in self.anomalies:
            if anomaly.get('device_id') == device_id:
                return anomaly
        return None
    
    def _get_node_color(self, node_id: str) -> str:
        """Determine node color based on anomaly status"""
        if node_id in self.anomaly_ids:
            return self.COLORS['anomaly']
        return self.COLORS['normal']
    
    def _get_node_size(self, node_id: str) -> int:
        """Get node size based on device type"""
        node_attrs = self.graph.nodes[node_id]
        device_type = node_attrs.get('type', 'iot_device')
        return self.NODE_SIZES.get(device_type, 400)
    
    def _get_node_shape(self, node_id: str) -> str:
        """Get node shape based on device type"""
        node_attrs = self.graph.nodes[node_id]
        device_type = node_attrs.get('type', 'iot_device')
        return self.NODE_SHAPES.get(device_type, 'o')
    
    def _get_node_label(self, node_id: str) -> str:
        """Generate node label with anomaly indicator (shortened for clarity)"""
        node_attrs = self.graph.nodes[node_id]
        name = node_attrs.get('name', node_id)
        
        # Truncate long names more aggressively
        if len(name) > 18:
            name = name[:15] + ".."
        
        # Add anomaly indicator (shorter version)
        if node_id in self.anomaly_ids:
            anomaly = self._get_anomaly_data(node_id)
            if anomaly:
                severity = anomaly.get('severity', 'unknown')
                severity_symbol = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🔵'
                }.get(severity, '⚠️')
                # Even shorter label for anomaly
                return f"{name[:12]}..{severity_symbol}" if len(name) > 12 else f"{name} {severity_symbol}"
        
        return name
    
    def draw_topology(self, 
                     figsize: Tuple[int, int] = (16, 12),
                     title: str = "NetGraphIQ - Network Topology with Anomalies",
                     show_labels: bool = True,
                     save_path: Optional[str] = None):
        """
        Draw the network topology with anomaly highlighting
        
        Args:
            figsize: Figure size (width, height)
            title: Plot title
            show_labels: Whether to show node labels
            save_path: Optional path to save the figure
        """
        # Create figure with higher DPI for better quality
        plt.figure(figsize=figsize, facecolor=self.COLORS['background'], dpi=100)
        
        # Calculate layout (use spring layout with adjusted parameters for less overlap)
        pos = nx.spring_layout(self.graph, k=2.5, iterations=50, seed=42)
        
        # Get edges connected to anomalies
        anomaly_edges = self._get_edges_connected_to_anomalies()
        normal_edges = [e for e in self.graph.edges() if e not in anomaly_edges]
        
        # Draw normal edges first (light gray, thinner)
        if normal_edges:
            nx.draw_networkx_edges(
                self.graph, pos,
                edgelist=normal_edges,
                edge_color=self.COLORS['edge_normal'],
                width=1.2,
                alpha=0.5,
                style='solid'
            )
        
        # Draw anomaly edges (red, thicker, more visible)
        if anomaly_edges:
            nx.draw_networkx_edges(
                self.graph, pos,
                edgelist=list(anomaly_edges),
                edge_color=self.COLORS['edge_anomaly'],
                width=2.5,
                alpha=0.8,
                style='solid'
            )
        
        # Separate nodes by anomaly status for drawing
        normal_nodes = [n for n in self.graph.nodes() if n not in self.anomaly_ids]
        anomaly_nodes = [n for n in self.graph.nodes() if n in self.anomaly_ids]
        
        # Draw normal nodes (blue, with shapes)
        for node in normal_nodes:
            nx.draw_networkx_nodes(
                self.graph, pos,
                nodelist=[node],
                node_color=self.COLORS['normal'],
                node_size=self._get_node_size(node),
                node_shape=self._get_node_shape(node),
                alpha=0.8,
                edgecolors='black',
                linewidths=1.2
            )
        
        # Draw anomaly nodes (red, larger, with shapes, glowing effect)
        for node in anomaly_nodes:
            # Draw outer glow for anomalies
            nx.draw_networkx_nodes(
                self.graph, pos,
                nodelist=[node],
                node_color=self.COLORS['anomaly'],
                node_size=self._get_node_size(node) * 1.3,  # 30% larger
                node_shape=self._get_node_shape(node),
                alpha=0.3,
                edgecolors='none'
            )
            # Draw main anomaly node
            nx.draw_networkx_nodes(
                self.graph, pos,
                nodelist=[node],
                node_color=self.COLORS['anomaly'],
                node_size=self._get_node_size(node),
                node_shape=self._get_node_shape(node),
                alpha=0.95,
                edgecolors='darkred',
                linewidths=2.5
            )
        
        # Draw labels with smaller font to reduce overlap
        if show_labels:
            labels = {node: self._get_node_label(node) for node in self.graph.nodes()}
            nx.draw_networkx_labels(
                self.graph, pos,
                labels=labels,
                font_size=7,  # Reduced from 8 to 7
                font_weight='bold',
                font_color=self.COLORS['text']
            )
        
        # Add title
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Create enhanced legend with clear explanations
        legend_elements = [
            # Node types
            Patch(facecolor=self.COLORS['normal'], edgecolor='black', 
                  label='● Normal Device', alpha=0.8),
            Patch(facecolor=self.COLORS['anomaly'], edgecolor='darkred', 
                  label='🔴 Anomalous Device (High Risk)', alpha=0.9),
            
            # Edge types
            Patch(facecolor='none', edgecolor=self.COLORS['edge_normal'], 
                  label='── Normal Connection', alpha=0.8),
            Patch(facecolor='none', edgecolor=self.COLORS['edge_anomaly'], 
                  label='── Connection to Anomaly', alpha=0.8),
            
            # Device shapes
            Patch(facecolor='white', edgecolor='black', 
                  label='■ Router | ▲ Core Switch'),
            Patch(facecolor='white', edgecolor='black', 
                  label='● Access Switch | ▼ IoT Device')
        ]
        
        # Add severity legend if there are anomalies
        if self.anomalies:
            severity_counts = {}
            for anomaly in self.anomalies:
                severity = anomaly.get('severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if severity_counts:
                severity_text = "⚠️ Severity Levels: "
                severity_items = []
                for severity, count in severity_counts.items():
                    symbol = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}.get(severity, '⚪')
                    severity_items.append(f"{symbol} {severity.title()} ({count})")
                severity_text += " | ".join(severity_items)
                
                plt.figtext(0.5, 0.01, severity_text, 
                           ha='center', fontsize=9, 
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))
        
        # Position legend outside the plot to reduce clutter
        plt.legend(handles=legend_elements, loc='upper left', 
                  bbox_to_anchor=(1.02, 1), fontsize=9, 
                  framealpha=0.9, title="Legend")
        
        # Remove axes
        plt.axis('off')
        
        # Adjust layout with more margin for legend
        plt.tight_layout()
        plt.subplots_adjust(right=0.85)  # Make room for legend on the right
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor=self.COLORS['background'])
            print(f"📸 Visualization saved to: {save_path}")
        
        # Show plot
        plt.show()
    
    def draw_layer_view(self, figsize: Tuple[int, int] = (16, 12)):
        """
        Draw topology with layer-based coloring (alternative view)
        """
        plt.figure(figsize=figsize, facecolor=self.COLORS['background'], dpi=100)
        
        # Layer colors
        layer_colors = {
            'edge': '#FF6B6B',      # Red for edge
            'core': '#4ECDC4',       # Teal for core
            'access': '#45B7D1',     # Blue for access
            'endpoint': '#96CEB4'    # Green for endpoint
        }
        
        # Layer descriptions for legend
        layer_descriptions = {
            'edge': '🌐 EDGE Layer (Internet Gateway, Routers)',
            'core': '⚡ CORE Layer (Core Switches - Backbone)',
            'access': '🔌 ACCESS Layer (Access Switches)',
            'endpoint': '📱 ENDPOINT Layer (IoT Devices, Endpoints)'
        }
        
        pos = nx.spring_layout(self.graph, k=2.5, iterations=50, seed=42)
        
        # Get edges connected to anomalies
        anomaly_edges = self._get_edges_connected_to_anomalies()
        normal_edges = [e for e in self.graph.edges() if e not in anomaly_edges]
        
        # Draw normal edges first
        if normal_edges:
            nx.draw_networkx_edges(self.graph, pos, edgelist=normal_edges,
                                  edge_color=self.COLORS['edge_normal'], 
                                  width=1.2, alpha=0.5)
        
        # Draw anomaly edges
        if anomaly_edges:
            nx.draw_networkx_edges(self.graph, pos, edgelist=list(anomaly_edges),
                                  edge_color=self.COLORS['edge_anomaly'],
                                  width=2.5, alpha=0.8)
        
        # Draw nodes by layer
        for layer, color in layer_colors.items():
            nodes = [n for n, attrs in self.graph.nodes(data=True) 
                    if attrs.get('layer') == layer]
            if nodes:
                # Increase size for anomaly nodes in this layer
                sizes = []
                for node in nodes:
                    base_size = self._get_node_size(node)
                    if node in self.anomaly_ids:
                        sizes.append(base_size * 1.2)
                    else:
                        sizes.append(base_size)
                
                # Draw glow for anomaly nodes
                anomaly_in_layer = [n for n in nodes if n in self.anomaly_ids]
                if anomaly_in_layer:
                    nx.draw_networkx_nodes(
                        self.graph, pos,
                        nodelist=anomaly_in_layer,
                        node_color=self.COLORS['anomaly'],
                        node_size=[self._get_node_size(n) * 1.4 for n in anomaly_in_layer],
                        alpha=0.3,
                        edgecolors='none'
                    )
                
                # Draw main nodes
                nx.draw_networkx_nodes(
                    self.graph, pos,
                    nodelist=nodes,
                    node_color=[self.COLORS['anomaly'] if n in self.anomaly_ids else color 
                               for n in nodes],
                    node_size=sizes,
                    alpha=0.85,
                    edgecolors='black',
                    linewidths=[2.5 if n in self.anomaly_ids else 1.2 for n in nodes]
                )
        
        # Draw labels with smaller font
        labels = {node: self._get_node_label(node) for node in self.graph.nodes()}
        nx.draw_networkx_labels(self.graph, pos, labels=labels, 
                               font_size=7, font_weight='bold')
        
        # Add title
        plt.title("NetGraphIQ - Layer-Based Topology View with Anomalies", 
                 fontsize=16, fontweight='bold', pad=20)
        
        # Create legend
        legend_elements = []
        for layer, color in layer_colors.items():
            legend_elements.append(
                Patch(facecolor=color, edgecolor='black', 
                      label=layer_descriptions.get(layer, layer.upper()))
            )
        
        # Add anomaly to legend
        legend_elements.append(
            Patch(facecolor=self.COLORS['anomaly'], edgecolor='darkred',
                  label='⚠️ Anomalous Device (Red Border)')
        )
        
        plt.legend(handles=legend_elements, loc='upper left', 
                  bbox_to_anchor=(1.02, 1), fontsize=9, 
                  framealpha=0.9, title="Network Layers")
        
        plt.axis('off')
        plt.tight_layout()
        plt.subplots_adjust(right=0.85)
        plt.show()
    
    def print_statistics(self):
        """Print network statistics"""
        print("\n" + "=" * 60)
        print("📊 NETWORK VISUALIZATION STATISTICS")
        print("=" * 60)
        
        print(f"\n   Total Nodes: {self.graph.number_of_nodes()}")
        print(f"   Total Edges: {self.graph.number_of_edges()}")
        print(f"   Graph Density: {nx.density(self.graph):.3f}")
        print(f"   Connected Components: {nx.number_connected_components(self.graph)}")
        
        # Count by device type
        type_counts = {}
        for _, attrs in self.graph.nodes(data=True):
            dtype = attrs.get('type', 'unknown')
            type_counts[dtype] = type_counts.get(dtype, 0) + 1
        
        print("\n   Device Types:")
        for dtype, count in type_counts.items():
            print(f"      {dtype}: {count}")
        
        # Count by layer
        layer_counts = {}
        for _, attrs in self.graph.nodes(data=True):
            layer = attrs.get('layer', 'unknown')
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        
        print("\n   Layer Distribution:")
        for layer, count in layer_counts.items():
            print(f"      {layer.upper()}: {count}")
        
        # Edge statistics
        anomaly_edges = self._get_edges_connected_to_anomalies()
        print(f"\n   Edge Statistics:")
        print(f"      Total Edges: {self.graph.number_of_edges()}")
        print(f"      Edges connected to anomalies: {len(anomaly_edges)}")
        
        # Anomaly statistics
        if self.anomaly_ids:
            print(f"\n   ⚠️ Anomalous Devices: {len(self.anomaly_ids)}")
            severity_counts = {}
            for anomaly in self.anomalies:
                severity = anomaly.get('severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            print("   Severity Breakdown:")
            for severity, count in severity_counts.items():
                symbol = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}.get(severity, '⚪')
                print(f"      {symbol} {severity.upper()}: {count}")