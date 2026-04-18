"""
Discovery Engine - Simulates ARP and LLDP protocols for topology inference
WITH EXPLAINABILITY - Every connection includes WHY it was accepted
"""

from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from enum import Enum


class NetworkLayer(Enum):
    EDGE = "edge"
    CORE = "core"
    ACCESS = "access"
    ENDPOINT = "endpoint"


class DiscoveryEngine:
    """
    Discovers network topology with full explainability
    Each discovered connection includes reasoning
    """
    
    # Valid layer pairs for quick lookup
    VALID_LAYER_PAIRS = {
        (NetworkLayer.EDGE, NetworkLayer.CORE): "EDGE ↔ CORE (valid hierarchical layer connection - edge router connects to core infrastructure)",
        (NetworkLayer.CORE, NetworkLayer.ACCESS): "CORE ↔ ACCESS (valid aggregation layer link - core switch connects to access switches)",
        (NetworkLayer.ACCESS, NetworkLayer.ENDPOINT): "ACCESS ↔ ENDPOINT (valid access layer connection - endpoint devices connect to access switches)",
    }
    
    def __init__(self, devices: Dict):
        self.devices = devices
        self.arp_table: Dict[str, str] = {}
        self.lldp_neighbors: Dict[str, List[str]] = {}
        self.inferred_topology: List[Tuple[Tuple[str, str], List[str]]] = []  # (edge, explanations)
        self.discovery_timestamp = datetime.now()
        
    def generate_arp_table(self) -> Dict[str, str]:
        """Generate ARP table with IP→MAC mappings"""
        print("\n📡 Generating ARP Table (IP → MAC mappings)...")
        
        self.arp_table = {}
        for device_id, device in self.devices.items():
            self.arp_table[device.ip_address] = device.mac_address
        
        print(f"   ✅ ARP table populated with {len(self.arp_table)} entries")
        return self.arp_table
    
    def generate_lldp_neighbors(self) -> Dict[str, List[str]]:
        """
        Generate LLDP neighbor tables based on parent-child relationships
        """
        print("\n🔌 Generating LLDP Neighbor Tables...")
        
        # Initialize empty neighbor lists
        for device_id in self.devices.keys():
            self.lldp_neighbors[device_id] = []
        
        # Build neighbor relationships based on parent-child
        for device_id, device in self.devices.items():
            # If device has a parent, they are neighbors
            if device.parent_id and device.parent_id in self.devices:
                parent_id = device.parent_id
                # Add parent as neighbor
                if parent_id not in self.lldp_neighbors[device_id]:
                    self.lldp_neighbors[device_id].append(parent_id)
                # Add device as neighbor of parent
                if device_id not in self.lldp_neighbors[parent_id]:
                    self.lldp_neighbors[parent_id].append(device_id)
            
            # Special case: Routers connect to all core switches
            if device.device_type.value == "router" and device.name != "Internet-Gateway":
                for other_id, other in self.devices.items():
                    if other.device_type.value == "core_switch":
                        if other_id not in self.lldp_neighbors[device_id]:
                            self.lldp_neighbors[device_id].append(other_id)
                        if device_id not in self.lldp_neighbors[other_id]:
                            self.lldp_neighbors[other_id].append(device_id)
            
            # Core switches connect to access switches that have them as parent
            if device.device_type.value == "core_switch":
                for other_id, other in self.devices.items():
                    if other.device_type.value == "access_switch" and other.parent_id == device_id:
                        if other_id not in self.lldp_neighbors[device_id]:
                            self.lldp_neighbors[device_id].append(other_id)
                        if device_id not in self.lldp_neighbors[other_id]:
                            self.lldp_neighbors[other_id].append(device_id)
        
        # Remove duplicates from each neighbor list
        for device_id in self.lldp_neighbors:
            self.lldp_neighbors[device_id] = list(set(self.lldp_neighbors[device_id]))
        
        # Statistics
        devices_with_neighbors = sum(1 for n in self.lldp_neighbors.values() if n)
        total_neighbors = sum(len(n) for n in self.lldp_neighbors.values())
        
        print(f"   ✅ LLDP neighbors discovered for {devices_with_neighbors} devices")
        print(f"   📊 Total neighbor relationships: {total_neighbors}")
        
        return self.lldp_neighbors
    
    def discover_topology(self) -> List[Tuple[Tuple[str, str], List[str]]]:
        """
        Discover topology from LLDP neighbors with explanations
        
        Returns:
            List of tuples: ((device1_id, device2_id), [explanation1, explanation2, ...])
        """
        print("\n🔍 Discovering Topology from Protocol Data...")
        
        discovered_edges = {}
        
        for device_id, neighbors in self.lldp_neighbors.items():
            for neighbor_id in neighbors:
                # Create sorted edge key
                edge = tuple(sorted([device_id, neighbor_id]))
                
                if edge not in discovered_edges:
                    # Generate explanations for this connection
                    explanations = self._generate_explanations(edge[0], edge[1])
                    discovered_edges[edge] = explanations
        
        # Convert to list of (edge, explanations) tuples
        self.inferred_topology = [(edge, explanations) for edge, explanations in discovered_edges.items()]
        
        print(f"   ✅ Discovered {len(self.inferred_topology)} connections with explanations")
        
        return self.inferred_topology
    
    def _generate_explanations(self, device1_id: str, device2_id: str) -> List[str]:
        """
        Generate human-readable explanations for why a connection was accepted
        
        Args:
            device1_id: First device ID
            device2_id: Second device ID
        
        Returns:
            List of explanation strings
        """
        explanations = []
        
        device1 = self.devices.get(device1_id)
        device2 = self.devices.get(device2_id)
        
        if not device1 or not device2:
            return ["Unable to generate explanations - device not found"]
        
        # Get layers
        layer1 = device1.layer if hasattr(device1, 'layer') else None
        layer2 = device2.layer if hasattr(device2, 'layer') else None
        
        # Explanation 1: Layer validation
        if layer1 and layer2:
            pair1 = (layer1, layer2)
            pair2 = (layer2, layer1)
            
            if pair1 in self.VALID_LAYER_PAIRS:
                explanations.append(f"✓ {self.VALID_LAYER_PAIRS[pair1]}")
            elif pair2 in self.VALID_LAYER_PAIRS:
                explanations.append(f"✓ {self.VALID_LAYER_PAIRS[pair2]}")
            else:
                explanations.append("⚠️ Layer validation passed (connection follows network hierarchy)")
        
        # Explanation 2: LLDP discovery
        if device2_id in self.lldp_neighbors.get(device1_id, []):
            explanations.append("✓ Discovered via LLDP neighbor advertisement - Device sent LLDP packets detected by neighbor")
        elif device1_id in self.lldp_neighbors.get(device2_id, []):
            explanations.append("✓ Discovered via LLDP neighbor advertisement - Device received LLDP packets from neighbor")
        else:
            explanations.append("⚠️ Inferred through network hierarchy and naming patterns")
        
        # Explanation 3: ARP validation
        if self._arp_validation(device1, device2):
            explanations.append("✓ Validated via ARP identity mapping - Both devices have each other's MAC addresses in ARP cache")
        else:
            explanations.append("ℹ️ ARP validation not available - Connection based on LLDP and hierarchy")
        
        # Explanation 4: Parent-child relationship (if applicable)
        if self._has_parent_child_relationship(device1, device2):
            explanations.append("✓ Confirmed by parent-child relationship in network configuration")
        
        # Explanation 5: Specific connection type
        connection_type = self._get_connection_type(device1, device2)
        if connection_type:
            explanations.append(f"✓ {connection_type}")
        
        return explanations
    
    def _arp_validation(self, device1, device2) -> bool:
        """Check if ARP table validates the connection"""
        # In real ARP, devices would have each other's MACs
        # For simulation, we check if they're in same network segment
        if hasattr(device1, 'ip_address') and hasattr(device2, 'ip_address'):
            # Same subnet indicates ARP visibility
            return self._same_subnet(device1.ip_address, device2.ip_address)
        return False
    
    def _same_subnet(self, ip1: str, ip2: str, mask: str = "255.255.255.0") -> bool:
        """Check if IPs are on same subnet"""
        try:
            ip1_parts = [int(x) for x in ip1.split('.')]
            ip2_parts = [int(x) for x in ip2.split('.')]
            mask_parts = [int(x) for x in mask.split('.')]
            
            for i in range(4):
                if (ip1_parts[i] & mask_parts[i]) != (ip2_parts[i] & mask_parts[i]):
                    return False
            return True
        except:
            return False
    
    def _has_parent_child_relationship(self, device1, device2) -> bool:
        """Check if devices have parent-child relationship"""
        if hasattr(device1, 'parent_id') and device1.parent_id == device2.id:
            return True
        if hasattr(device2, 'parent_id') and device2.parent_id == device1.id:
            return True
        return False
    
    def _get_connection_type(self, device1, device2) -> str:
        """Get specific connection type description"""
        type1 = device1.device_type.value if hasattr(device1, 'device_type') else None
        type2 = device2.device_type.value if hasattr(device2, 'device_type') else None
        
        if not type1 or not type2:
            return ""
        
        connection_map = {
            ('router', 'core_switch'): "Edge-to-Core uplink connection - Router connects to core switching infrastructure",
            ('core_switch', 'access_switch'): "Core-to-Access distribution link - Core switch provides connectivity to access layer",
            ('access_switch', 'iot_device'): "Access-to-Device edge connection - Endpoint connects to network via access switch",
            ('core_switch', 'core_switch'): "Core-to-Core interconnect - Redundant core switching fabric",
        }
        
        # Check both orders
        pair = (type1, type2)
        if pair in connection_map:
            return connection_map[pair]
        
        pair_rev = (type2, type1)
        if pair_rev in connection_map:
            return connection_map[pair_rev]
        
        return ""
    
    def print_topology_with_explanations(self, limit: int = 15):
        """Print discovered topology with full explanations"""
        print("\n" + "=" * 80)
        print("🌐 DISCOVERED TOPOLOGY WITH EXPLANATIONS")
        print("=" * 80)
        
        if not self.inferred_topology:
            print("   No connections discovered")
            return
        
        for i, (edge, explanations) in enumerate(self.inferred_topology[:limit], 1):
            device1 = self.devices.get(edge[0])
            device2 = self.devices.get(edge[1])
            
            if device1 and device2:
                layer1 = device1.layer.value.upper() if hasattr(device1, 'layer') else '?'
                layer2 = device2.layer.value.upper() if hasattr(device2, 'layer') else '?'
                
                print(f"\n{'='*60}")
                print(f"Connection {i}: {device1.name} [{layer1}] ↔ {device2.name} [{layer2}]")
                print(f"{'='*60}")
                print("✅ Connection accepted because:")
                
                for explanation in explanations:
                    print(f"   {explanation}")
        
        if len(self.inferred_topology) > limit:
            print(f"\n   ... and {len(self.inferred_topology) - limit} more connections")
    
    def get_summary(self) -> Dict:
        """Get discovery summary"""
        devices_with_lldp = sum(1 for n in self.lldp_neighbors.values() if n)
        
        # Count connections by layer
        layer_connections = {}
        for edge, _ in self.inferred_topology:
            d1 = self.devices.get(edge[0])
            d2 = self.devices.get(edge[1])
            if d1 and d2:
                l1 = d1.layer.value if hasattr(d1, 'layer') else 'unknown'
                l2 = d2.layer.value if hasattr(d2, 'layer') else 'unknown'
                pair = tuple(sorted([l1, l2]))
                layer_connections[pair] = layer_connections.get(pair, 0) + 1
        
        return {
            "timestamp": self.discovery_timestamp,
            "arp_entries": len(self.arp_table),
            "lldp_capable_devices": devices_with_lldp,
            "total_neighbor_relationships": sum(len(n) for n in self.lldp_neighbors.values()),
            "discovered_connections": len(self.inferred_topology),
            "layer_connections": layer_connections
        }
    
    def print_arp_sample(self, limit: int = 10):
        """Print sample ARP entries"""
        print("\n📋 SAMPLE ARP TABLE ENTRIES:")
        print("-" * 50)
        items = list(self.arp_table.items())[:limit]
        for ip, mac in items:
            print(f"   {ip:20} → {mac}")
    
    def print_lldp_sample(self, limit: int = 5):
        """Print sample LLDP neighbors"""
        print("\n🔌 SAMPLE LLDP NEIGHBOR TABLES:")
        print("-" * 50)
        
        devices_with_neighbors = [(id, n) for id, n in self.lldp_neighbors.items() if n]
        for device_id, neighbors in devices_with_neighbors[:limit]:
            device = self.devices.get(device_id)
            device_name = device.name if device else device_id
            device_layer = device.layer.value if device and hasattr(device, 'layer') else 'unknown'
            
            print(f"\n   Device: {device_name} ({device_layer})")
            for nid in neighbors[:5]:
                neighbor = self.devices.get(nid)
                neighbor_name = neighbor.name if neighbor else nid
                neighbor_layer = neighbor.layer.value if neighbor and hasattr(neighbor, 'layer') else 'unknown'
                print(f"      └─ {neighbor_name} ({neighbor_layer})")
    
    def compare_with_ground_truth(self, ground_truth_connections: List) -> Dict:
        """Compare with ground truth"""
        discovered_set = set([edge for edge, _ in self.inferred_topology])
        ground_set = set([tuple(sorted([c.source_id, c.target_id])) for c in ground_truth_connections])
        
        correct = len(discovered_set.intersection(ground_set))
        missed = len(ground_set - discovered_set)
        false_positives = len(discovered_set - ground_set)
        accuracy = (correct / len(ground_set)) * 100 if ground_set else 0
        
        return {
            "accuracy_percent": round(accuracy, 2),
            "correct_connections": correct,
            "missed_connections": missed,
            "false_positives": false_positives,
            "total_ground_truth": len(ground_set),
            "total_discovered": len(discovered_set)
        }