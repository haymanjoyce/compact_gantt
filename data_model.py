"""
Purpose: Manages Gantt chart data and layout structure, independent of UI or rendering logic.
Why: Centralizes data logic, making it reusable and easier to maintain/test.
"""

from dataclasses import dataclass
from datetime import datetime
import json  # Kept for JSON serialization intent; used implicitly by to_json/from_json

@dataclass
class TimeFrame:
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    width_proportion: float  # 0.0 to 1.0, fraction of inner_frame width
    magnification: float     # e.g., 1.0 for normal, 0.5 for half-scale

    def validate(self):
        try:
            datetime.strptime(self.start_date, "%Y-%m-%d")
            datetime.strptime(self.end_date, "%Y-%m-%d")
            assert 0 <= self.width_proportion <= 1.0
            assert self.magnification > 0
        except (ValueError, AssertionError):
            raise ValueError("Invalid TimeFrame data")

@dataclass
class FrameConfig:
    outer_width: float
    outer_height: float
    header_height: float
    footer_height: float
    margins: tuple[float, float, float, float]  # (top, right, bottom, left)
    num_rows: int
    upper_scale_height: float
    lower_scale_height: float
    header_text: str = ""  # New
    footer_text: str = ""  # New
    horizontal_gridlines: bool = False  # New
    vertical_gridlines: bool = False  # New

    @property
    def inner_height(self):
        return (self.outer_height - self.header_height - self.footer_height -
                self.margins[0] - self.margins[2] - self.upper_scale_height - self.lower_scale_height)

    def validate(self):
        assert self.outer_width > 0 and self.outer_height > 0
        assert 0 <= self.header_height < self.outer_height
        assert 0 <= self.footer_height < self.outer_height
        assert self.num_rows > 0 and isinstance(self.num_rows, int)
        assert self.upper_scale_height >= 0
        assert self.lower_scale_height >= 0
        assert self.inner_height > 0, "Inner height must be positive after accounting for scales and margins"
        assert isinstance(self.header_text, str) and isinstance(self.footer_text, str)
        assert isinstance(self.horizontal_gridlines, bool) and isinstance(self.vertical_gridlines, bool)

class ProjectData:
    def __init__(self):
        self.frame_config = FrameConfig(800, 600, 50, 50, (10, 10, 10, 10), 1, 20.0, 20.0, "", "", False, False)
        self.time_frames = []
        self.tasks = []

    def add_time_frame(self, start_date, end_date, width_proportion, magnification=1.0):
        """Add a time frame with validation."""
        tf = TimeFrame(start_date, end_date, width_proportion, magnification)
        tf.validate()
        total_width = sum(tf.width_proportion for tf in self.time_frames) + width_proportion
        if total_width > 1.0:
            raise ValueError("Total width proportion exceeds 1.0")
        self.time_frames.append(tf)

    def add_task(self, name, start_date, duration):
        """Add a task with validation."""
        try:
            if start_date:
                datetime.strptime(start_date, "%Y-%m-%d")
            if duration:
                float(duration)
            self.tasks.append({"name": name, "start": start_date, "duration": float(duration) if duration else 0})
        except ValueError as e:
            raise ValueError(f"Invalid task data: {e}")

    def to_json(self):
        return {
            "frame_config": {
                "outer_width": self.frame_config.outer_width,
                "outer_height": self.frame_config.outer_height,
                "header_height": self.frame_config.header_height,
                "footer_height": self.frame_config.footer_height,
                "margins": list(self.frame_config.margins),
                "num_rows": self.frame_config.num_rows,
                "upper_scale_height": self.frame_config.upper_scale_height,
                "lower_scale_height": self.frame_config.lower_scale_height,
                "header_text": self.frame_config.header_text,
                "footer_text": self.frame_config.footer_text,
                "horizontal_gridlines": self.frame_config.horizontal_gridlines,
                "vertical_gridlines": self.frame_config.vertical_gridlines
            },
            "time_frames": [
                {"start_date": tf.start_date, "end_date": tf.end_date,
                 "width_proportion": tf.width_proportion, "magnification": tf.magnification}
                for tf in self.time_frames
            ],
            "tasks": self.tasks
        }

    @classmethod
    def from_json(cls, data):
        instance = cls()
        margins = data["frame_config"]["margins"]
        if not (isinstance(margins, (list, tuple)) and len(margins) == 4 and all(
                isinstance(x, (int, float)) for x in margins)):
            raise ValueError("Margins must be a tuple of 4 floats")
        instance.frame_config = FrameConfig(
            data["frame_config"]["outer_width"], data["frame_config"]["outer_height"],
            data["frame_config"]["header_height"], data["frame_config"]["footer_height"],
            (float(margins[0]), float(margins[1]), float(margins[2]), float(margins[3])),
            data["frame_config"].get("num_rows", 1),
            data["frame_config"].get("upper_scale_height", 20.0),
            data["frame_config"].get("lower_scale_height", 20.0),
            data["frame_config"].get("header_text", ""),
            data["frame_config"].get("footer_text", ""),
            data["frame_config"].get("horizontal_gridlines", False),
            data["frame_config"].get("vertical_gridlines", False)
        )
        instance.time_frames = [TimeFrame(tf["start_date"], tf["end_date"], tf["width_proportion"], tf["magnification"])
                                for tf in data.get("time_frames", [])]
        instance.tasks = data.get("tasks", [])
        for task in instance.tasks:
            if "start" in task and task["start"]:
                datetime.strptime(task["start"], "%Y-%m-%d")
            if "duration" in task and task["duration"]:
                float(task["duration"])
        return instance

    def get_table_data(self, table_type):
        """Return data formatted for a specific table."""
        if table_type == "tasks":
            return [[t["name"], t["start"], str(t["duration"])] for t in self.tasks]
        return []

    def update_from_table(self, table_type, table_data):
        """Update data from table input."""
        if table_type == "tasks":
            self.tasks.clear()
            for row in table_data:
                self.add_task(row[0], row[1], row[2])
