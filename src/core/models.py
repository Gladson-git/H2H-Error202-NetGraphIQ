from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import uuid
import random

class DeviceType(Enum):
    ROUTER = "router"
    CORE_SWITCH = "core_switch"
    ACCESS_SWITCH = "access_switch"
    IOT_DEVICE = "iot_device"

class NetworkLayer(Enum):
    """Network hierarchy layers for better anomaly localization"""
    EDGE = "edge"      # Internet gateway, edge routers
    CORE = "core"      # Core switches, backbone
    ACCESS = "access"  # Access switches
    ENDPOINT = "endpoint"  # IoT devices, end devices

class DeviceStatus(Enum):
    """Device operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    COMPROMISED = "compromised"

@dataclass
class Device:
    id: str
    name: str
    device_type: DeviceType
    ip_address: str
    mac_address: str
    parent_id: Optional[str] = None
    layer: NetworkLayer = NetworkLayer.ENDPOINT  # NEW: Layer classification
    status: DeviceStatus = DeviceStatus.ACTIVE   # NEW: Operational status
    baseline_traffic: float = None               # NEW: Baseline for anomaly detection
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
        
        # Auto-assign layer based on device type if not specified
        if self.layer == NetworkLayer.ENDPOINT:
            self.layer = self._determine_layer()
        
        # Set baseline traffic if not provided
        if self.baseline_traffic is None:
            self.baseline_traffic = self._generate_baseline()
    
    def _determine_layer(self) -> NetworkLayer:
        """Determine network layer based on device type"""
        layer_mapping = {
            DeviceType.ROUTER: NetworkLayer.EDGE,
            DeviceType.CORE_SWITCH: NetworkLayer.CORE,
            DeviceType.ACCESS_SWITCH: NetworkLayer.ACCESS,
            DeviceType.IOT_DEVICE: NetworkLayer.ENDPOINT
        }
        return layer_mapping.get(self.device_type, NetworkLayer.ENDPOINT)
    
    def _generate_baseline(self) -> float:
        """Generate realistic baseline traffic based on device type and layer"""
        baselines = {
            # Edge layer (routers) - high traffic
            (DeviceType.ROUTER, NetworkLayer.EDGE): random.uniform(300, 800),
            
            # Core layer (core switches) - very high traffic
            (DeviceType.CORE_SWITCH, NetworkLayer.CORE): random.uniform(500, 1200),
            
            # Access layer (access switches) - medium traffic
            (DeviceType.ACCESS_SWITCH, NetworkLayer.ACCESS): random.uniform(100, 400),
            
            # Endpoint layer (IoT) - low traffic
            (DeviceType.IOT_DEVICE, NetworkLayer.ENDPOINT): random.uniform(10, 80)
        }
        
        # Default fallback
        baseline = baselines.get((self.device_type, self.layer), random.uniform(50, 150))
        
        # Add some variation based on device name (more realistic)
        if "camera" in self.name.lower():
            baseline *= 1.5  # Cameras use more bandwidth
        elif "thermostat" in self.name.lower():
            baseline *= 0.5  # Thermostats use very little
        
        return round(baseline, 2)
    
    def to_dict(self) -> dict:
        """Convert device to dictionary for easy serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.device_type.value,
            "layer": self.layer.value,
            "status": self.status.value,
            "ip": self.ip_address,
            "mac": self.mac_address,
            "baseline_traffic": self.baseline_traffic,
            "parent_id": self.parent_id
        }

@dataclass
class Connection:
    source_id: str
    target_id: str
    connection_type: str = "ethernet"
    layer: NetworkLayer = None  # Connection layer (usually the higher of the two devices)
    
    def __post_init__(self):
        if self.layer is None:
            # Layer will be set by the graph builder based on connected devices
            pass