"""
Day 5 - Graph Visualization Test with Enhanced Features
Tests topology visualization with anomaly highlighting and edge coloring
"""

import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.network_generator import NetworkGenerator
from src.core.telemetry_engine import TelemetryEngine
from src.core.anomaly_engine import AnomalyEngine
from src.visualization.graph_viz import GraphVisualizer


def main():
    print("=" * 80)
    print("🎨 NetGraphIQ - Day 5: Enhanced Graph Visualization")
    print("=" * 80)
    print("\n🎯 Improvements:")
    print("   ✅ Reduced label overlap (font_size=7, smaller nodes)")
    print("   ✅ Enhanced legend clarity")
    print("   ✅ Red edges for connections to anomalies")
    print("   ✅ Glowing effect for anomaly nodes")
    
    # Step 1: Generate network
    print("\n" + "=" * 80)
    print("🏗️  STEP 1: Generating Network Topology")
    print("=" * 80)
    
    generator = NetworkGenerator()
    devices, connections = generator.generate_enterprise_network()
    
    print(f"\n   ✅ Network ready: {len(devices)} devices, {len(connections)} connections")
    
    # Step 2: Generate telemetry with anomalies
    print("\n" + "=" * 80)
    print("📊 STEP 2: Generating Telemetry & Detecting Anomalies")
    print("=" * 80)
    
    telemetry = TelemetryEngine(devices)
    current_metrics = telemetry.generate_telemetry(
        inject_anomalies=True,
        anomaly_rate=0.12  # Slightly higher for visualization demo
    )
    
    anomaly_engine = AnomalyEngine(devices)
    anomalies = anomaly_engine.detect_anomalies(current_metrics)
    
    print(f"\n   ✅ Telemetry generated for {len(devices)} devices")
    print(f"   ⚠️  Detected {len(anomalies)} anomalies")
    
    # Step 3: Create visualization
    print("\n" + "=" * 80)
    print("🎨 STEP 3: Creating Enhanced Graph Visualization")
    print("=" * 80)
    
    visualizer = GraphVisualizer(devices, connections, anomalies)
    
    # Print statistics
    visualizer.print_statistics()
    
    # Step 4: Display visualizations
    print("\n" + "=" * 80)
    print("🖼️  STEP 4: Displaying Enhanced Visualizations")
    print("=" * 80)
    
    # Show anomaly highlighting view with red edges
    print("\n   📍 View 1: Anomaly Highlighting")
    print("      • Red nodes = Anomalous devices")
    print("      • Red edges = Connections to anomalies")
    print("      • Blue nodes = Normal devices")
    print("      • Shapes indicate device type")
    
    visualizer.draw_topology(
        figsize=(16, 12),
        title="NetGraphIQ - Network Topology with Anomaly Detection",
        show_labels=True
    )
    
    # Show layer-based view
    print("\n   📍 View 2: Layer-Based Coloring")
    print("      • Different colors per network layer")
    print("      • Anomalies highlighted with red borders")
    print("      • Red edges show anomaly connections")
    
    visualizer.draw_layer_view(figsize=(16, 12))
    
    # Step 5: Save visualization
    print("\n" + "=" * 80)
    print("💾 STEP 5: Saving Enhanced Visualization")
    print("=" * 80)
    
    save_path = "network_topology_with_anomalies_enhanced.png"
    visualizer.draw_topology(
        figsize=(16, 12),
        title="NetGraphIQ - Network Topology with Anomalies (Enhanced)",
        show_labels=True,
        save_path=save_path
    )
    
    print(f"\n   ✅ Visualization saved to: {save_path}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("✅ DAY 5 COMPLETE - Enhanced Visualization Layer Ready")
    print("=" * 80)
    
    print("\n🎯 ENHANCEMENTS ACHIEVED:")
    print("   1. ✅ Reduced label overlap (font_size=7, node_size reduced)")
    print("   2. ✅ Enhanced legend clarity (separate sections)")
    print("   3. ✅ Red edges for anomaly connections (elite feature)")
    print("   4. ✅ Glowing effect for anomaly nodes")
    print("   5. ✅ Better layout with legend outside")
    
    print("\n💡 VISUAL INSIGHTS:")
    print(f"   • Red nodes: {len(anomalies)} anomalous devices")
    print(f"   • Red edges: {len(visualizer._get_edges_connected_to_anomalies())} connections affected")
    print(f"   • Node shapes quickly identify device types")
    print(f"   • Clear legend explains all visual elements")
    
    return devices, connections, anomalies, visualizer


if __name__ == "__main__":
    print("\n🚀 Starting NetGraphIQ Enhanced Visualization System...\n")
    random.seed(42)
    devices, connections, anomalies, visualizer = main()
    print("\n✨ Enhanced visualization complete! Check the popup windows.")