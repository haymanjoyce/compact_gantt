from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TextBox:
    """Represents a text box that can be positioned anywhere on the chart."""
    textbox_id: int
    x: float  # X coordinate relative to chart area origin (pixels)
    y: float  # Y coordinate relative to chart area origin (pixels)
    width: float  # Width of text box (pixels)
    height: float  # Height of text box (pixels)
    text: str = ""  # Text content (supports wrapping)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TextBox':
        """Create TextBox from dictionary (for JSON deserialization)."""
        # Backward compatibility: support old list format
        if isinstance(data, list):
            # Old format: [Text, X, Y, Color] - convert to dict format
            if len(data) >= 3:
                return cls(
                    textbox_id=0,  # No ID in old format
                    x=float(data[1]) if data[1] else 0.0,
                    y=float(data[2]) if data[2] else 0.0,
                    width=100.0,  # Default width
                    height=50.0,  # Default height
                    text=str(data[0]) if data[0] else ""
                )
            else:
                return cls(textbox_id=0, x=0.0, y=0.0, width=100.0, height=50.0, text="")
        
        return cls(
            textbox_id=int(data["textbox_id"]),
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            width=float(data.get("width", 100.0)),
            height=float(data.get("height", 50.0)),
            text=data.get("text", "")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert TextBox to dictionary (for JSON serialization)."""
        result = {
            "textbox_id": self.textbox_id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }
        # Only save non-default values to reduce JSON size
        if self.text:
            result["text"] = self.text
        return result

