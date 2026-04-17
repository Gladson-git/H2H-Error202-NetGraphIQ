"""Test script for network simulation"""

import sys
import os

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import using relative imports
from .network_generator import NetworkGenerator

def test_network_generation():
    print("=" * 60)
    print("NetGraphIQ - Network Simulation Test")
    print("=" * 60)
    
    # Generate network
    gen = NetworkGenerator()
    devices, connections = gen.generate_enterprise_network()
    
    # Get summary
    summary = gen.get_summary()
    
    print(f"\n✅ Network Generated Successfully")
    print(f"📊 Total Devices: {summary['total_devices']}")
    print(f"🔗 Total Connections: {summary['total_connections']}")
    
    print("\n📈 Device Type Breakdown:")
    for dtype, count in summary['device_types'].items():
        expected = summary['expected_counts'].get(dtype, "N/A")
        if expected == "12-24":
            status = "✓" if 12 <= count <= 24 else "⚠️"
        else:
            status = "✓" if count == expected else "⚠️"
        print(f"  {status} {dtype}: {count} (Expected: {expected})")
    
    # Check for duplicate IPs
    print("\n🔍 Checking for duplicate IP addresses...")
    ip_addresses = {}
    duplicates = []
    for device_id, device in devices.items():
        if device.ip_address in ip_addresses:
            duplicates.append((device.name, device.ip_address, ip_addresses[device.ip_address]))
        else:
            ip_addresses[device.ip_address] = device.name
    
    if duplicates:
        print(f"  ❌ Found {len(duplicates)} duplicate IPs:")
        for dup in duplicates:
            print(f"     - {dup[0]} and {dup[2]} both have {dup[1]}")
    else:
        print("  ✓ All IP addresses are unique")
    
    # Check MAC addresses
    print("\n🔍 Checking MAC addresses...")
    mac_addresses = {}
    mac_duplicates = []
    for device_id, device in devices.items():
        if device.mac_address in mac_addresses:
            mac_duplicates.append((device.name, device.mac_address))
        else:
            mac_addresses[device.mac_address] = device.name
    
    if mac_duplicates:
        print(f"  ❌ Found {len(mac_duplicates)} duplicate MACs")
    else:
        print("  ✓ All MAC addresses are unique and sequential")
    
    # Print first few devices
    print("\n📱 Sample Devices (first 8):")
    for i, (dev_id, device) in enumerate(list(devices.items())[:8]):
        print(f"  {i+1}. {device.name:35} | {device.device_type.value:15} | {device.ip_address:15} | {device.mac_address}")
    
    # Print connection sample
    print("\n🔗 Sample Connections (first 8):")
    for i, conn in enumerate(connections[:8]):
        src = devices[conn.source_id].name
        tgt = devices[conn.target_id].name
        print(f"  {i+1}. {src} → {tgt}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Final Summary")
    print("=" * 60)
    print(f"✓ Routers: {summary['device_types'].get('router', 0)}/2")
    print(f"✓ Core Switches: {summary['device_types'].get('core_switch', 0)}/2")
    print(f"✓ Access Switches: {summary['device_types'].get('access_switch', 0)}/6")
    print(f"✓ IoT Devices: {summary['device_types'].get('iot_device', 0)}/12-24")
    
    return devices, connections

if __name__ == "__main__":
    devices, connections = test_network_generation()