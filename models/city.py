from typing import Dict, Set, Optional
from dataclasses import dataclass

@dataclass
class Route:
    destination: str
    distance: float
    is_active: bool = True

class City:
    def __init__(self, name: str):
        self.name = name
        self.connections: Dict[str, Route] = {}
        self.has_charging_station: bool = False
        self.packages: Set[int] = set()  # Set of package IDs at this city
    
    def add_connection(self, destination: str, distance: float) -> None:
        """Add a connection to another city."""
        if distance <= 0:
            raise ValueError("Distance must be positive")
        self.connections[destination] = Route(destination, distance)
    
    def remove_connection(self, destination: str) -> None:
        """Remove a connection to another city."""
        if destination in self.connections:
            del self.connections[destination]
    
    def deactivate_route(self, destination: str) -> None:
        """Deactivate a route to another city."""
        if destination in self.connections:
            self.connections[destination].is_active = False
    
    def activate_route(self, destination: str) -> None:
        """Activate a route to another city."""
        if destination in self.connections:
            self.connections[destination].is_active = True
    
    def get_active_connections(self) -> Dict[str, float]:
        """Get all active connections and their distances."""
        return {
            dest: route.distance
            for dest, route in self.connections.items()
            if route.is_active
        }
    
    def add_package(self, package_id: int) -> None:
        """Add a package to the city."""
        self.packages.add(package_id)
    
    def remove_package(self, package_id: int) -> None:
        """Remove a package from the city."""
        self.packages.discard(package_id)
    
    def has_package(self, package_id: int) -> bool:
        """Check if the city has a specific package."""
        return package_id in self.packages
    
    def is_valid(self) -> bool:
        """Validate city attributes."""
        return (
            isinstance(self.name, str) and
            self.name.strip() != "" and
            all(distance > 0 for distance in self.get_active_connections().values())
        )
    
    def __str__(self) -> str:
        return f"City(name={self.name}, connections={len(self.connections)})" 