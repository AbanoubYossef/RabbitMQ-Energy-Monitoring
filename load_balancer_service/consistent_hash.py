"""
Consistent Hashing Implementation for Load Balancing
"""
import hashlib
from bisect import bisect_right


class ConsistentHash:
    """
    Consistent hashing ring for distributing load across replicas
    """
    
    def __init__(self, num_replicas=3, virtual_nodes=150):
        """
        Initialize consistent hash ring
        
        Args:
            num_replicas: Number of monitoring service replicas
            virtual_nodes: Number of virtual nodes per replica (for better distribution)
        """
        self.num_replicas = num_replicas
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self._build_ring()
    
    def _hash(self, key):
        """Generate hash for a key"""
        return int(hashlib.md5(str(key).encode('utf-8')).hexdigest(), 16)
    
    def _build_ring(self):
        """Build the hash ring with virtual nodes"""
        for replica_id in range(1, self.num_replicas + 1):
            for vnode in range(self.virtual_nodes):
                # Create virtual node key
                vnode_key = f"replica_{replica_id}_vnode_{vnode}"
                hash_value = self._hash(vnode_key)
                
                # Add to ring
                self.ring[hash_value] = replica_id
        
        # Sort keys for binary search
        self.sorted_keys = sorted(self.ring.keys())
        
        print(f"✅ Hash ring built with {self.num_replicas} replicas and {self.virtual_nodes} virtual nodes each")
        print(f"   Total nodes in ring: {len(self.ring)}")
    
    def get_replica(self, device_id):
        """
        Get replica ID for a device using consistent hashing
        
        Args:
            device_id: Device UUID
            
        Returns:
            int: Replica ID (1 to num_replicas)
        """
        if not self.ring:
            return 1  # Default to replica 1 if ring is empty
        
        # Hash the device ID
        device_hash = self._hash(device_id)
        
        # Find the first node >= device_hash
        index = bisect_right(self.sorted_keys, device_hash)
        
        # Wrap around if necessary
        if index == len(self.sorted_keys):
            index = 0
        
        # Get replica ID from ring
        replica_id = self.ring[self.sorted_keys[index]]
        
        return replica_id
    
    def get_distribution_stats(self, device_ids):
        """
        Get distribution statistics for a list of devices
        
        Args:
            device_ids: List of device UUIDs
            
        Returns:
            dict: Distribution statistics per replica
        """
        distribution = {i: 0 for i in range(1, self.num_replicas + 1)}
        
        for device_id in device_ids:
            replica_id = self.get_replica(device_id)
            distribution[replica_id] += 1
        
        return distribution
    
    def add_replica(self):
        """Add a new replica to the ring (for scaling)"""
        self.num_replicas += 1
        
        # Add virtual nodes for new replica
        new_replica_id = self.num_replicas
        for vnode in range(self.virtual_nodes):
            vnode_key = f"replica_{new_replica_id}_vnode_{vnode}"
            hash_value = self._hash(vnode_key)
            self.ring[hash_value] = new_replica_id
        
        # Re-sort keys
        self.sorted_keys = sorted(self.ring.keys())
        
        print(f"✅ Added replica {new_replica_id} to hash ring")
    
    def remove_replica(self, replica_id):
        """Remove a replica from the ring (for scaling down)"""
        if self.num_replicas <= 1:
            print("⚠️  Cannot remove last replica")
            return False
        
        # Remove all virtual nodes for this replica
        keys_to_remove = [k for k, v in self.ring.items() if v == replica_id]
        for key in keys_to_remove:
            del self.ring[key]
        
        # Re-sort keys
        self.sorted_keys = sorted(self.ring.keys())
        
        print(f"✅ Removed replica {replica_id} from hash ring")
        return True
