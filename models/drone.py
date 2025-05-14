from dataclasses import dataclass
from typing import List, Optional
from models.package import Package

@dataclass
class Drone:
    id: int
    max_weight: float
    max_distance: float
    current_location: str = "Warehouse"
    current_weight: float = 0.0
    current_distance: float = 0.0
    battery_level: float = 100.0
    status: str = "idle"  # idle, busy, charging
    
    def __post_init__(self):
        """Validate drone attributes after initialization."""
        if self.id <= 0:
            raise ValueError("Drone ID must be positive")
        if self.max_weight <= 0:
            raise ValueError("Drone max weight must be positive")
        if self.max_distance <= 0:
            raise ValueError("Drone max distance must be positive")
        if not isinstance(self.current_location, str) or not self.current_location.strip():
            raise ValueError("Drone location must be a non-empty string")
        if self.battery_level < 0 or self.battery_level > 100:
            raise ValueError("Battery level must be between 0 and 100")
    
    def can_carry_package(self, package: Package) -> bool:
        """Check if the drone can carry an additional package."""
        return self.current_weight + package.weight <= self.max_weight
    
    def can_fly_distance(self, distance: float) -> bool:
        """Check if the drone can fly the given distance."""
        return self.current_distance + distance <= self.max_distance
    
    def add_package(self, package: Package) -> bool:
        """Add a package to the drone's load."""
        if not self.can_carry_package(package):
            return False
        self.current_weight += package.weight
        return True
    
    def remove_package(self, package: Package) -> None:
        """Remove a package from the drone's load."""
        self.current_weight -= package.weight
    
    def update_location(self, new_location: str, distance: float) -> bool:
        """Update drone's location and distance traveled."""
        if not self.can_fly_distance(distance):
            return False
        self.current_location = new_location
        self.current_distance += distance
        return True
    
    def reset_trip(self) -> None:
        """Reset drone's trip metrics."""
        self.current_weight = 0.0
        self.current_distance = 0.0
        self.current_location = "Warehouse"
    
    def is_valid(self) -> bool:
        """Validate drone attributes."""
        return (
            self.id > 0 and
            self.max_weight > 0 and
            self.max_distance > 0 and
            self.battery_level >= 0 and
            self.battery_level <= 100
        )
    
    def __str__(self) -> str:
        return f"Drone(id={self.id}, max_weight={self.max_weight}, max_distance={self.max_distance})" 