from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Pipe:
    """Represents a vertical line marker at a specific date."""
    pipe_id: int
    date: str  # yyyy-mm-dd format
    color: str = "red"
    name: str = ""  # Optional label, rotated 90 degrees along the line
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pipe':
        """Create Pipe from dictionary (for JSON deserialization)."""
        return cls(
            pipe_id=int(data["pipe_id"]),
            date=data["date"],
            color=data.get("color", "red"),
            name=data.get("name", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Pipe to dictionary (for JSON serialization)."""
        result = {
            "pipe_id": self.pipe_id,
            "date": self.date,
        }
        # Only save non-default values to reduce JSON size
        if self.color != "red":
            result["color"] = self.color
        if self.name:
            result["name"] = self.name
        return result

