"""
Purpose: Manages Gantt chart data and layout structure, independent of UI or rendering logic.
Why: Centralizes data logic, making it reusable and easier to maintain/test.
"""

from dataclasses import dataclass
from datetime import datetime
import json

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
    header_text: str
    footer_text: str
    horizontal_gridlines: bool
    vertical_gridlines: bool

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

@dataclass
class TimeFrame:
    start_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    width_proportion: float  # 0.0 to 1.0
    upper_scale_intervals: str  # e.g., "days", "weeks", "months", "years"
    lower_scale_intervals: str  # e.g., "days", "weeks", "months", "years"

    def validate(self):
        try:
            datetime.strptime(self.start_date, "%Y-%m-%d")
            datetime.strptime(self.end_date, "%Y-%m-%d")
            assert 0 <= self.width_proportion <= 1.0
            valid_intervals = ["days", "weeks", "months", "years"]
            assert self.upper_scale_intervals in valid_intervals
            assert self.lower_scale_intervals in valid_intervals
            interval_order = {"days": 1, "weeks": 2, "months": 3, "years": 4}
            assert interval_order[self.lower_scale_intervals] <= interval_order[self.upper_scale_intervals], \
                "Lower scale intervals must be shorter than or equal to upper scale intervals"
        except (ValueError, AssertionError) as e:
            raise ValueError(f"Invalid TimeFrame data: {e}")

@dataclass
class Task:
    task_id: int
    task_name: str
    start_date: str  # YYYY-MM-DD
    finish_date: str  # YYYY-MM-DD
    row_number: int

    def validate(self):
        try:
            assert self.task_id > 0 and isinstance(self.task_id, int)
            assert isinstance(self.task_name, str)
            datetime.strptime(self.start_date, "%Y-%m-%d")
            datetime.strptime(self.finish_date, "%Y-%m-%d")
            assert self.row_number > 0 and isinstance(self.row_number, int)
        except (ValueError, AssertionError):
            raise ValueError("Invalid Task data")

@dataclass
class Connector:
    from_task_id: int
    to_task_id: int

    def validate(self):
        assert self.from_task_id > 0 and isinstance(self.from_task_id, int)
        assert self.to_task_id > 0 and isinstance(self.to_task_id, int)

@dataclass
class Swimlane:
    from_row_number: int
    to_row_number: int
    title: str
    colour: str

    def validate(self):
        assert self.from_row_number > 0 and isinstance(self.from_row_number, int)
        assert self.to_row_number >= self.from_row_number and isinstance(self.to_row_number, int)
        assert isinstance(self.title, str)
        assert isinstance(self.colour, str)

@dataclass
class Pipe:
    date: str  # YYYY-MM-DD
    colour: str

    def validate(self):
        datetime.strptime(self.date, "%Y-%m-%d")
        assert isinstance(self.colour, str)

@dataclass
class Curtain:
    from_date: str  # YYYY-MM-DD
    to_date: str    # YYYY-MM-DD
    colour: str

    def validate(self):
        datetime.strptime(self.from_date, "%Y-%m-%d")
        datetime.strptime(self.to_date, "%Y-%m-%d")
        assert isinstance(self.colour, str)

@dataclass
class TextBox:
    text: str
    x_coordinate: float
    y_coordinate: float
    colour: str

    def validate(self):
        assert isinstance(self.text, str)
        assert isinstance(self.x_coordinate, (int, float))
        assert isinstance(self.y_coordinate, (int, float))
        assert isinstance(self.colour, str)

class ProjectData:
    def __init__(self):
        self.frame_config = FrameConfig(800, 600, 50, 50, (10, 10, 10, 10), 1, 20.0, 20.0, "", "", False, False)
        self.time_frames = []
        self.tasks = []
        self.connectors = []
        self.swimlanes = []
        self.pipes = []
        self.curtains = []
        self.text_boxes = []

    def add_time_frame(self, start_date, end_date, width_proportion, upper_scale_intervals, lower_scale_intervals):
        tf = TimeFrame(start_date, end_date, width_proportion, upper_scale_intervals, lower_scale_intervals)
        tf.validate()
        if sum(tf.width_proportion for tf in self.time_frames) + width_proportion > 1.0:
            raise ValueError("Total width proportion exceeds 1.0")
        self.time_frames.append(tf)

    def add_task(self, task_id, task_name, start_date, finish_date, row_number):
        task = Task(task_id, task_name, start_date, finish_date, row_number)
        task.validate()
        self.tasks.append(task)

    def add_connector(self, from_task_id, to_task_id):
        conn = Connector(from_task_id, to_task_id)
        conn.validate()
        self.connectors.append(conn)

    def add_swimlane(self, from_row_number, to_row_number, title, colour):
        sl = Swimlane(from_row_number, to_row_number, title, colour)
        sl.validate()
        self.swimlanes.append(sl)

    def add_pipe(self, date, colour):
        pipe = Pipe(date, colour)
        pipe.validate()
        self.pipes.append(pipe)

    def add_curtain(self, from_date, to_date, colour):
        curtain = Curtain(from_date, to_date, colour)
        curtain.validate()
        self.curtains.append(curtain)

    def add_text_box(self, text, x_coordinate, y_coordinate, colour):
        tb = TextBox(text, x_coordinate, y_coordinate, colour)
        tb.validate()
        self.text_boxes.append(tb)

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
                 "width_proportion": tf.width_proportion,
                 "upper_scale_intervals": tf.upper_scale_intervals,
                 "lower_scale_intervals": tf.lower_scale_intervals}
                for tf in self.time_frames
            ],
            "tasks": [
                {"task_id": t.task_id, "task_name": t.task_name,
                 "start_date": t.start_date, "finish_date": t.finish_date,
                 "row_number": t.row_number}
                for t in self.tasks
            ],
            "connectors": [
                {"from_task_id": c.from_task_id, "to_task_id": c.to_task_id}
                for c in self.connectors
            ],
            "swimlanes": [
                {"from_row_number": s.from_row_number, "to_row_number": s.to_row_number,
                 "title": s.title, "colour": s.colour}
                for s in self.swimlanes
            ],
            "pipes": [
                {"date": p.date, "colour": p.colour}
                for p in self.pipes
            ],
            "curtains": [
                {"from_date": c.from_date, "to_date": c.to_date, "colour": c.colour}
                for c in self.curtains
            ],
            "text_boxes": [
                {"text": tb.text, "x_coordinate": tb.x_coordinate,
                 "y_coordinate": tb.y_coordinate, "colour": tb.colour}
                for tb in self.text_boxes
            ]
        }

    @classmethod
    def from_json(cls, data):
        instance = cls()
        margins = data["frame_config"]["margins"]
        if not (isinstance(margins, (list, tuple)) and len(margins) == 4 and all(isinstance(x, (int, float)) for x in margins)):
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
        instance.time_frames = [
            TimeFrame(tf["start_date"], tf["end_date"], tf["width_proportion"],
                      tf["upper_scale_intervals"], tf["lower_scale_intervals"])
            for tf in data.get("time_frames", [])
        ]
        instance.tasks = [
            Task(t["task_id"], t["task_name"], t["start_date"], t["finish_date"], t["row_number"])
            for t in data.get("tasks", [])
        ]
        instance.connectors = [
            Connector(c["from_task_id"], c["to_task_id"])
            for c in data.get("connectors", [])
        ]
        instance.swimlanes = [
            Swimlane(s["from_row_number"], s["to_row_number"], s["title"], s["colour"])
            for s in data.get("swimlanes", [])
        ]
        instance.pipes = [
            Pipe(p["date"], p["colour"])
            for p in data.get("pipes", [])
        ]
        instance.curtains = [
            Curtain(c["from_date"], c["to_date"], c["colour"])
            for c in data.get("curtains", [])
        ]
        instance.text_boxes = [
            TextBox(tb["text"], tb["x_coordinate"], tb["y_coordinate"], tb["colour"])
            for tb in data.get("text_boxes", [])
        ]
        return instance

    def get_table_data(self, table_type):
        if table_type == "tasks":
            return [[str(t.task_id), t.task_name, t.start_date, t.finish_date, str(t.row_number)]
                    for t in self.tasks]
        elif table_type == "time_frames":
            return [[tf.start_date, tf.end_date, str(tf.width_proportion * 100),
                     tf.upper_scale_intervals, tf.lower_scale_intervals]
                    for tf in self.time_frames]
        elif table_type == "connectors":
            return [[str(c.from_task_id), str(c.to_task_id)] for c in self.connectors]
        elif table_type == "swimlanes":
            return [[str(s.from_row_number), str(s.to_row_number), s.title, s.colour]
                    for s in self.swimlanes]
        elif table_type == "pipes":
            return [[p.date, p.colour] for p in self.pipes]
        elif table_type == "curtains":
            return [[c.from_date, c.to_date, c.colour] for c in self.curtains]
        elif table_type == "text_boxes":
            return [[tb.text, str(tb.x_coordinate), str(tb.y_coordinate), tb.colour]
                    for tb in self.text_boxes]
        return []

    def update_from_table(self, table_type, table_data):
        if table_type == "tasks":
            self.tasks.clear()
            for row in table_data:
                self.add_task(int(row[0] or 1), row[1] or "Unnamed", row[2] or "2025-01-01",
                              row[3] or "2025-01-01", int(row[4] or 1))
        elif table_type == "time_frames":
            self.time_frames.clear()
            for row in table_data:
                width = float(row[2] or 0) / 100  # Convert percentage to proportion
                self.add_time_frame(row[0] or "2025-01-01", row[1] or "2025-01-01",
                                    width, row[3] or "days", row[4] or "weeks")
        elif table_type == "connectors":
            self.connectors.clear()
            for row in table_data:
                self.add_connector(int(row[0]), int(row[1]))
        elif table_type == "swimlanes":
            self.swimlanes.clear()
            for row in table_data:
                self.add_swimlane(int(row[0]), int(row[1]), row[2], row[3])
        elif table_type == "pipes":
            self.pipes.clear()
            for row in table_data:
                self.add_pipe(row[0], row[1])
        elif table_type == "curtains":
            self.curtains.clear()
            for row in table_data:
                self.add_curtain(row[0], row[1], row[2])
        elif table_type == "text_boxes":
            self.text_boxes.clear()
            for row in table_data:
                self.add_text_box(row[0], float(row[1]), float(row[2]), row[3])

