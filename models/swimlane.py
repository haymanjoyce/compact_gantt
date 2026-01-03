from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Swimlane:
    """Represents a horizontal swimlane spanning multiple rows."""
    swimlane_id: int
    first_row: int  # 1-based row number (user perspective)
    last_row: int   # 1-based row number (user perspective), inclusive
    name: str = ""  # Optional label displayed in bottom-right corner
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Swimlane':
        """Create Swimlane from dictionary (for JSON deserialization)."""
        return cls(
            swimlane_id=int(data["swimlane_id"]),
            first_row=int(data["first_row"]),
            last_row=int(data["last_row"]),
            name=data.get("name", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Swimlane to dictionary (for JSON serialization)."""
        result = {
            "swimlane_id": self.swimlane_id,
            "first_row": self.first_row,
            "last_row": self.last_row,
        }
        # Only save non-default values to reduce JSON size
        if self.name:
            result["name"] = self.name
        return result

