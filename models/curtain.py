from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Curtain:
    """Represents a shaded area between two dates (two vertical lines with hatching)."""
    curtain_id: int
    start_date: str  # yyyy-mm-dd format
    end_date: str    # yyyy-mm-dd format
    color: str = "red"
    name: str = ""  # Optional label, rotated 90 degrees along the start line
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Curtain':
        """Create Curtain from dictionary (for JSON deserialization)."""
        return cls(
            curtain_id=int(data["curtain_id"]),
            start_date=data["start_date"],
            end_date=data["end_date"],
            color=data.get("color", "red"),
            name=data.get("name", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Curtain to dictionary (for JSON serialization)."""
        result = {
            "curtain_id": self.curtain_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        # Only save non-default values to reduce JSON size
        if self.color != "red":
            result["color"] = self.color
        if self.name:
            result["name"] = self.name
        return result

