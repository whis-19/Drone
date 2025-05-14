from dataclasses import dataclass
from typing import Optional

@dataclass
class Package:
    id: int
    weight: float
    value: float
    destination: str
    priority: Optional[int] = None
    status: str = "pending"  # pending, assigned, delivered
    
    def __post_init__(self):
        """Validate package attributes after initialization."""
        if self.id <= 0:
            raise ValueError("Package ID must be positive")
        if self.weight <= 0:
            raise ValueError("Package weight must be positive")
        if self.value < 0:
            raise ValueError("Package value cannot be negative")
        if not isinstance(self.destination, str) or not self.destination.strip():
            raise ValueError("Package destination must be a non-empty string")
    
    @property
    def value_weight_ratio(self) -> float:
        """Calculate the value-to-weight ratio of the package."""
        return self.value / self.weight if self.weight > 0 else 0
    
    def is_valid(self) -> bool:
        """Validate package attributes."""
        return (
            self.id > 0 and
            self.weight > 0 and
            self.value >= 0 and
            isinstance(self.destination, str) and
            self.destination.strip() != ""
        )
    
    def __str__(self) -> str:
        return f"Package(id={self.id}, weight={self.weight}, value={self.value}, destination={self.destination})" 