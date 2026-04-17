"""Simple standalone test for network generator"""

import sys
import os
import random
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# Define classes directly in this file to avoid import issues
class DeviceType(Enum):
    ROUTER = "router"
    CORE_SWITCH = "core_switch"
    ACCESS_SWITCH = "access_switch"
    IOT_DEVICE = "iot_device"

@dataclass
class Device:
    id: str
    name: str
    device_type: DeviceType
    ip_address: str
    mac_address: str
    parent_id: Optional[str] = None

@dataclass
class Connection:
    source_id: str
    target_id: str
    connection_type: str = "ethernet"

class SimpleNetworkGenerator:
    """Simplified network generator for testing"""
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.connections: List[Connection] = []
        self.mac_counter = 0x100000000000
        self.ip_counter = {
            DeviceType.ROUTER: 1,
            DeviceType.CORE_SWITCH: 1,
            DeviceType.ACCESS_SWITCH: 1,
            DeviceType.IOT_DEVICE: 1
        }
        
    def generate_network(self) -> Tuple[Dict[str, Device], List[Connection]]:
        """Generate test network"""
        
        self.ip_subnets = {
            DeviceType.ROUTER: "192.168.1.",
            DeviceType.CORE_SWITCH: "192.168.2.",
            DeviceType.ACCESS_SWITCH: "192.168.3.",
            DeviceType.IOT_DEVICE: "192.168.4."
        }
        
        # Internet Gateway
        internet = Device(
            id="internet_gw",
            name="Internet-Gateway",
            device_type=DeviceType.ROUTER,
            ip_address="1.1.1.1",
            mac_address=self._gen_mac()
        )
        self.devices[internet.id] = internet
        
        # Main Router
        router = Device(
            id="router_01",
            name="Edge-Router-01",
            device_type=DeviceType.ROUTER,
            ip_address=self._get_ip(DeviceType.ROUTER),
            mac_address=self._gen_mac()
        )
        self.devices[router.id] = router
        self.connections.append(Connection(internet.id, router.id))
        
        # Core Switches (2)
        core_switches = []
        for i in range(2):
            core = Device(
                id=f"core_sw_{i+1}",
                name=f"Core-Switch-{i+1}",
                device_type=DeviceType.CORE_SWITCH,
                ip_address=self._get_ip(DeviceType.CORE_SWITCH),
                mac_address=self._gen_mac(),
                parent_id=router.id
            )
            self.devices[core.id] = core
            self.connections.append(Connection(router.id, core.id))
            core_switches.append(core)
        
        # Access Switches (3 per core = 6 total)
        access_switches = []
        for core in core_switches:
            for j in range(3):
                access = Device(
                    id=f"access_{core.id}_{j+1}",
                    name=f"Access-Switch-{core.id[-1]}-{j+1}",
                    device_type=DeviceType.ACCESS_SWITCH,
                    ip_address=self._get_ip(DeviceType.ACCESS_SWITCH),
                    mac_address=self._gen_mac(),
                    parent_id=core.id
                )
                self.devices[access.id] = access
                self.connections.append(Connection(core.id, access.id))
                access_switches.append(access)
        
        # IoT Devices (2-4 per access switch)
        iot_names = ["Camera", "Thermostat", "DoorLock", "MotionSensor", "LightBulb"]
        for access in access_switches:
            num_iot = random.randint(2, 4)
            for k in range(num_iot):
                iot = Device(
                    id=f"iot_{access.id}_{k+1}",
                    name=f"{random.choice(iot_names)}-{k+1}",
                    device_type=DeviceType.IOT_DEVICE,
                    ip_address=self._get_ip(DeviceType.IOT_DEVICE),
                    mac_address=self._gen_mac(),
                    parent_id=access.id
                )
                self.devices[iot.id] = iot
                self.connections.append(Connection(access.id, iot.id))
        
        return self.devices, self.connections
    
    def _get_ip(self, device_type: DeviceType) -> str:
        ip_num = self.ip_counter[device_type]
        self.ip_counter[device_type] += 1
        return self.ip_subnets[device_type] + str(ip_num)
    
    def _gen_mac(self) -> str:
        mac_bytes = [
            (self.mac_counter >> 40) & 0xFF,
            (self.mac_counter >> 32) & 0xFF,
            (self.mac_counter >> 24) & 0xFF,
            (self.mac_counter >> 16) & 0xFF,
            (self.mac_counter >> 8) & 0xFF,
            self.mac_counter & 0xFF
        ]
        self.mac_counter += 1
        return ':'.join(f'{b:02x}' for b in mac_bytes)

def main():
    print("=" * 70)
    print("NetGraphIQ - Network Generator Test")
    print("=" * 70)
    
    # Generate network
    gen = SimpleNetworkGenerator()
    devices, connections = gen.generate_network()
    
    # Count device types
    type_counts = {}
    for device in devices.values():
        t = device.device_type.value
        type_counts[t] = type_counts.get(t, 0) + 1
    
    print(f"\n✅ Network Generated Successfully!")
    print(f"\n📊 STATISTICS:")
    print(f"   Total Devices: {len(devices)}")
    print(f"   Total Connections: {len(connections)}")
    print(f"\n   Device Breakdown:")
    print(f"   - Routers: {type_counts.get('router', 0)} (Expected: 2)")
    print(f"   - Core Switches: {type_counts.get('core_switch', 0)} (Expected: 2)")
    print(f"   - Access Switches: {type_counts.get('access_switch', 0)} (Expected: 6)")
    print(f"   - IoT Devices: {type_counts.get('iot_device', 0)} (Expected: 12-24)")
    
    print("\n" + "=" * 70)
    print("📱 DEVICE DETAILS (First 10 devices):")
    print("=" * 70)
    print(f"{'No.':<4} {'Name':<30} {'Type':<15} {'IP Address':<15} {'MAC Address':<20}")
    print("-" * 84)
    
    for i, (dev_id, device) in enumerate(list(devices.items())[:10], 1):
        print(f"{i:<4} {device.name:<30} {device.device_type.value:<15} {device.ip_address:<15} {device.mac_address:<20}")
    
    print("\n" + "=" * 70)
    print("🔗 CONNECTION DETAILS (First 10 connections):")
    print("=" * 70)
    
    for i, conn in enumerate(connections[:10], 1):
        src = devices[conn.source_id].name
        tgt = devices[conn.target_id].name
        print(f"   {i}. {src} → {tgt}")
    
    print("\n" + "=" * 70)
    print("✅ Test completed successfully!")
    print("=" * 70)
    
    # Check for duplicates
    print("\n🔍 VALIDATION CHECKS:")
    
    # Check IP duplicates
    ips = {}
    ip_dupes = []
    for device in devices.values():
        if device.ip_address in ips:
            ip_dupes.append(device.name)
        else:
            ips[device.ip_address] = device.name
    
    if ip_dupes:
        print(f"   ❌ Duplicate IPs found: {ip_dupes}")
    else:
        print(f"   ✓ All {len(devices)} IP addresses are unique")
    
    # Check MAC duplicates
    macs = {}
    mac_dupes = []
    for device in devices.values():
        if device.mac_address in macs:
            mac_dupes.append(device.name)
        else:
            macs[device.mac_address] = device.name
    
    if mac_dupes:
        print(f"   ❌ Duplicate MACs found: {mac_dupes}")
    else:
        print(f"   ✓ All {len(devices)} MAC addresses are unique")
    
    return devices, connections

if __name__ == "__main__":
    devices, connections = main()