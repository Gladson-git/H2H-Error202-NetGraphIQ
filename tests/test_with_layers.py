"""Test network generation with layer tags, status, and baselines"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.network_generator import NetworkGenerator
from src.core.models import NetworkLayer, DeviceStatus

def test_layered_network():
    print("=" * 70)
    print("🔥 NetGraphIQ - Enhanced Network with Layer Tags")
    print("=" * 70)
    
    # Generate network
    gen = NetworkGenerator()
    devices, connections = gen.generate_enterprise_network()
    
    # Get detailed summary
    summary = gen.get_summary()
    
    print("\n" + "=" * 70)
    print("📊 NETWORK STATISTICS")
    print("=" * 70)
    print(f"Total Devices: {summary['total_devices']}")
    print(f"Total Connections: {summary['total_connections']}")
    
    print("\n📈 DEVICE TYPE BREAKDOWN:")
    for dtype, count in summary['device_types'].items():
        expected = summary['expected_counts'].get(dtype, "N/A")
        print(f"   {dtype}: {count} (Expected: {expected})")
    
    print("\n🏷️  LAYER DISTRIBUTION (VERY IMPRESSIVE!):")
    for layer, count in summary['layer_distribution'].items():
        print(f"   🔹 {layer.upper()} LAYER: {count} devices")
    
    print("\n📊 BASELINE TRAFFIC BY LAYER:")
    for layer, baseline in summary['layer_baselines'].items():
        print(f"   {layer.upper()}: {baseline} packets/sec (baseline)")
    
    print("\n✅ DEVICE STATUS:")
    for status, count in summary['status_distribution'].items():
        print(f"   {status.upper()}: {count} devices")
    
    print("\n" + "=" * 70)
    print("🔍 SAMPLE DEVICES WITH ALL ENHANCED FIELDS")
    print("=" * 70)
    print(f"{'Name':<35} {'Type':<15} {'Layer':<12} {'Status':<12} {'Baseline':<12} {'IP':<15}")
    print("-" * 110)
    
    for device in list(devices.values())[:12]:
        print(f"{device.name:<35} {device.device_type.value:<15} "
              f"{device.layer.value:<12} {device.status.value:<12} "
              f"{device.baseline_traffic:<12} {device.ip_address:<15}")
    
    print("\n" + "=" * 70)
    print("🎯 LAYER-SPECIFIC QUERIES (Demo)")
    print("=" * 70)
    
    # Demo: Get devices by layer
    for layer in NetworkLayer:
        devices_in_layer = gen.get_devices_by_layer(layer)
        print(f"\n{layer.value.upper()} LAYER Devices ({len(devices_in_layer)}):")
        for device in devices_in_layer[:3]:  # Show first 3
            print(f"   • {device.name} - Baseline: {device.baseline_traffic} pkts/sec")
        if len(devices_in_layer) > 3:
            print(f"   ... and {len(devices_in_layer) - 3} more")
    
    print("\n" + "=" * 70)
    print("⚠️  ANOMALY DETECTION READINESS")
    print("=" * 70)
    print("✓ Each device has baseline_traffic for comparison")
    print("✓ Layer tags enable targeted anomaly detection")
    print("✓ Status field tracks device health")
    print("\nExample anomaly messages you can now generate:")
    print("   🔴 'Anomaly detected at ACCESS layer - Traffic spike 3x baseline'")
    print("   🟡 'EDGE layer device failure - Edge-Router-01 is INACTIVE'")
    print("   🔵 'CORE layer high utilization - Core-Switch-1 at 95% CPU'")
    
    print("\n" + "=" * 70)
    print("✅ Enhanced Network Generation Complete!")
    print("=" * 70)
    
    return devices, connections, gen

def test_failure_simulation(gen):
    """Test device failure simulation"""
    print("\n" + "=" * 70)
    print("🔥 FAILURE SIMULATION TEST")
    print("=" * 70)
    
    # Get an access switch
    access_devices = gen.get_devices_by_layer(NetworkLayer.ACCESS)
    if access_devices:
        test_device = access_devices[0]
        print(f"\nSimulating failure on: {test_device.name}")
        print(f"   Layer: {test_device.layer.value}")
        print(f"   Baseline: {test_device.baseline_traffic} pkts/sec")
        
        gen.simulate_device_failure(test_device.id, test_device.layer.value)
        
        # Check status
        if gen.devices[test_device.id].status == DeviceStatus.INACTIVE:
            print(f"\n✅ Status updated to: {gen.devices[test_device.id].status.value.upper()}")
            print(f"\n🔔 ALERT: Device at {test_device.layer.value.upper()} layer is DOWN!")
            print(f"   Impact: All {len(gen.get_devices_by_layer(NetworkLayer.ENDPOINT))} endpoint devices affected")

if __name__ == "__main__":
    devices, connections, gen = test_layered_network()
    test_failure_simulation(gen)
    
    print("\n💡 Next Steps:")
    print("   1. Layer tags enable targeted anomaly detection")
    print("   2. Baselines ready for Day 4 anomaly detection")
    print("   3. Try: python test_with_layers.py")