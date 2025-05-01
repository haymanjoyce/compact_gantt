from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

@dataclass
class FrameConfig:
    outer_width: int = 800
    outer_height: int = 600
    header_height: int = 50
    footer_height: int = 50
    margins: Tuple[int, int, int, int] = (10, 10, 10, 10)
    num_rows: int = 1
    header_text: str = ""
    footer_text: str = ""
    horizontal_gridlines: bool = True
    vertical_gridlines: bool = True
    chart_start_date: str = "2025-01-01"

@dataclass
class TimeFrame:
    time_frame_id: int
    finish_date: str
    width_proportion: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeFrame':
        return cls(
            time_frame_id=data["time_frame_id"],
            finish_date=data["finish_date"],
            width_proportion=data["width_proportion"]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time_frame_id": self.time_frame_id,
            "finish_date": self.finish_date,
            "width_proportion": self.width_proportion
        }

@dataclass
class Task:
    task_id: int
    task_order: float
    task_name: str
    start_date: str
    finish_date: str
    row_number: int
    is_milestone: bool = False
    label_placement: str = "Inside"
    label_hide: str = "No"
    label_alignment: str = "Left"
    label_horizontal_offset: float = 1.0
    label_vertical_offset: float = 0.5
    label_text_colour: str = "black"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        return cls(
            task_id=data["task_id"],
            task_order=data["task_order"],
            task_name=data["task_name"],
            start_date=data["start_date"],
            finish_date=data["finish_date"],
            row_number=data["row_number"],
            is_milestone=data.get("is_milestone", False),
            label_placement=data.get("label_placement", "Inside"),
            label_hide=data.get("label_hide", "No"),
            label_alignment=data.get("label_alignment", "Left"),
            label_horizontal_offset=data.get("label_horizontal_offset", 1.0),
            label_vertical_offset=data.get("label_vertical_offset", 0.5),
            label_text_colour=data.get("label_text_colour", "black")
        ) 