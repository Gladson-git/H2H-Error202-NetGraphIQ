import random
from typing import List, Dict, Tuple
from .models import Device, DeviceType, Connection, NetworkLayer, DeviceStatus

class NetworkGenerator:
    """Generates realistic hierarchical network topology with layer tagging"""
    
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
        
    def generate_enterprise_network(self) -> Tuple[Dict[str, Device], List[Connection]]:
        """Generate complete network with layer tagging"""
        
        # Define IP subnets for each device type
        self.ip_subnets = {
            DeviceType.ROUTER: "192.168.1.",
            DeviceType.CORE_SWITCH: "192.168.2.",
            DeviceType.ACCESS_SWITCH: "192.168.3.",
            DeviceType.IOT_DEVICE: "192.168.4."
        }
        
        print("\n🏗️ Building Network Hierarchy with Layer Tags...")
        
        # 1. EDGE LAYER: Internet gateway + Router
        print("   📡 EDGE LAYER: Creating edge devices...")
        
        internet = Device(
            id="internet_gw",
            name="Internet-Gateway",
            device_type=DeviceType.ROUTER,
            ip_address="1.1.1.1",
            mac_address=self._generate_mac(),
            layer=NetworkLayer.EDGE,
            status=DeviceStatus.ACTIVE,
            baseline_traffic=random.uniform(500, 1000)
        )
        self.devices[internet.id] = internet
        
        router = Device(
            id="router_01",
            name="Edge-Router-01",
            device_type=DeviceType.ROUTER,
            ip_address=self._get_next_ip(DeviceType.ROUTER),
            mac_address=self._generate_mac(),
            layer=NetworkLayer.EDGE,
            status=DeviceStatus.ACTIVE
        )
        self.devices[router.id] = router
        self.connections.append(Connection(internet.id, router.id, layer=NetworkLayer.EDGE))
        
        # 2. CORE LAYER: Core switches
        print("   🎯 CORE LAYER: Creating core switches...")
        core_switches = []
        for i in range(2):
            core = Device(
                id=f"core_sw_{i+1}",
                name=f"Core-Switch-{i+1}",
                device_type=DeviceType.CORE_SWITCH,
                ip_address=self._get_next_ip(DeviceType.CORE_SWITCH),
                mac_address=self._generate_mac(),
                parent_id=router.id,
                layer=NetworkLayer.CORE,
                status=DeviceStatus.ACTIVE
            )
            self.devices[core.id] = core
            self.connections.append(Connection(router.id, core.id, layer=NetworkLayer.CORE))
            core_switches.append(core)
        
        # 3. ACCESS LAYER: Access switches
        print("   🔌 ACCESS LAYER: Creating access switches...")
        access_switches = []
        for core_idx, core in enumerate(core_switches, 1):
            for j in range(3):
                access = Device(
                    id=f"access_sw_c{core_idx}_{j+1}",
                    name=f"Access-Switch-C{core_idx}-{j+1}",
                    device_type=DeviceType.ACCESS_SWITCH,
                    ip_address=self._get_next_ip(DeviceType.ACCESS_SWITCH),
                    mac_address=self._generate_mac(),
                    parent_id=core.id,
                    layer=NetworkLayer.ACCESS,
                    status=DeviceStatus.ACTIVE
                )
                self.devices[access.id] = access
                self.connections.append(Connection(core.id, access.id, layer=NetworkLayer.ACCESS))
                access_switches.append(access)
        
        # 4. ENDPOINT LAYER: IoT devices
        print("   📱 ENDPOINT LAYER: Creating IoT devices...")
        iot_types = ["Camera", "Thermostat", "DoorLock", "MotionSensor", "LightBulb", 
                     "SmokeDetector", "CO2Sensor", "HumiditySensor", "SmartPlug", "WaterLeak"]
        
        iot_count = 0
        for access in access_switches:
            num_devices = random.randint(2, 4)
            for k in range(num_devices):
                iot_name = random.choice(iot_types)
                
                # Special baseline for different IoT types
                if iot_name == "Camera":
                    baseline = random.uniform(80, 150)
                elif iot_name == "Thermostat":
                    baseline = random.uniform(5, 20)
                elif iot_name == "DoorLock":
                    baseline = random.uniform(10, 30)
                else:
                    baseline = random.uniform(15, 60)
                
                iot = Device(
                    id=f"iot_{access.id}_{k+1}",
                    name=f"{iot_name}-{access.name[-3:]}-{k+1}",
                    device_type=DeviceType.IOT_DEVICE,
                    ip_address=self._get_next_ip(DeviceType.IOT_DEVICE),
                    mac_address=self._generate_mac(),
                    parent_id=access.id,
                    layer=NetworkLayer.ENDPOINT,
                    status=DeviceStatus.ACTIVE,
                    baseline_traffic=baseline
                )
                self.devices[iot.id] = iot
                self.connections.append(Connection(access.id, iot.id, layer=NetworkLayer.ENDPOINT))
                iot_count += 1
        
        print(f"\n✅ Network Generated Successfully!")
        print(f"   📊 Total: {len(self.devices)} devices | {len(self.connections)} connections")
        print(f"   🏷️  Layer Distribution:")
        
        # Count by layer
        layer_counts = {}
        for device in self.devices.values():
            layer_counts[device.layer.value] = layer_counts.get(device.layer.value, 0) + 1
        
        for layer, count in layer_counts.items():
            print(f"      - {layer.upper()}: {count} devices")
        
        return self.devices, self.connections
    
    def _get_next_ip(self, device_type: DeviceType) -> str:
        """Get next unique IP address for device type"""
        ip_num = self.ip_counter[device_type]
        self.ip_counter[device_type] += 1
        return self.ip_subnets[device_type] + str(ip_num)
    
    def _generate_mac(self) -> str:
        """Generate realistic unique MAC address"""
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
    
    def get_summary(self) -> dict:
        """Get network statistics with layer information"""
        type_counts = {}
        layer_counts = {}
        status_counts = {}
        
        for device in self.devices.values():
            type_counts[device.device_type.value] = type_counts.get(device.device_type.value, 0) + 1
            layer_counts[device.layer.value] = layer_counts.get(device.layer.value, 0) + 1
            status_counts[device.status.value] = status_counts.get(device.status.value, 0) + 1
        
        # Calculate average baseline traffic by layer
        layer_baselines = {}
        for layer in NetworkLayer:
            devices_in_layer = [d for d in self.devices.values() if d.layer == layer]
            if devices_in_layer:
                avg_baseline = sum(d.baseline_traffic for d in devices_in_layer) / len(devices_in_layer)
                layer_baselines[layer.value] = round(avg_baseline, 2)
        
        return {
            "total_devices": len(self.devices),
            "total_connections": len(self.connections),
            "device_types": type_counts,
            "layer_distribution": layer_counts,
            "status_distribution": status_counts,
            "layer_baselines": layer_baselines,
            "expected_counts": {
                "router": 2,
                "core_switch": 2,
                "access_switch": 6,
                "iot_device": "12-24"
            }
        }
    
    def simulate_device_failure(self, device_id: str, layer: str = None):
        """Simulate device failure for testing anomaly detection"""
        if device_id in self.devices:
            self.devices[device_id].status = DeviceStatus.INACTIVE
            print(f"⚠️ Device {self.devices[device_id].name} ({layer or 'unknown'} layer) has FAILED")
            return True
        return False
    
    def get_devices_by_layer(self, layer: NetworkLayer) -> List[Device]:
        """Get all devices in a specific layer"""
        return [d for d in self.devices.values() if d.layer == layer]