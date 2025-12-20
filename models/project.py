from typing import List, Dict, Any, Set
from models import FrameConfig, Task
from validators import DataValidator
import logging
from config.app_config import AppConfig
from utils.conversion import safe_int, safe_float, display_to_internal_date, internal_to_display_date

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProjectData:
    def __init__(self):
        app_config = AppConfig()
        self.frame_config = FrameConfig(num_rows=app_config.general.tasks_rows)
        self.tasks: List[Task] = []
        self.connectors: List[List[str]] = []
        self.swimlanes: List[List[str]] = []
        self.pipes: List[List[str]] = []
        self.curtains: List[List[str]] = []
        self.text_boxes: List[List[str]] = []
        self.validator = DataValidator()

    def to_json(self) -> Dict[str, Any]:
        for t in self.tasks:
            assert hasattr(t, "__dict__"), f"Non-class instance in self.tasks: {t} ({type(t)})"
        return {
            "frame_config": vars(self.frame_config),
            "tasks": [vars(task) for task in self.tasks],
            "connectors": self.connectors,
            "swimlanes": self.swimlanes,
            "pipes": self.pipes,
            "curtains": self.curtains,
            "text_boxes": self.text_boxes
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ProjectData':
        project = cls()
        frame_config_data = data.get("frame_config", {})
        # Convert margins list back to tuple (JSON converts tuples to lists)
        if "margins" in frame_config_data and isinstance(frame_config_data["margins"], list):
            frame_config_data["margins"] = tuple(frame_config_data["margins"])
        project.frame_config = FrameConfig(**frame_config_data)
        
        # Load tasks
        for task_data in data.get("tasks", []):
            project.tasks.append(Task.from_dict(task_data))
        
        # Load other data
        project.connectors = data.get("connectors", [])
        project.swimlanes = data.get("swimlanes", [])
        project.pipes = data.get("pipes", [])
        project.curtains = data.get("curtains", [])
        project.text_boxes = data.get("text_boxes", [])
        
        return project
    
    def update_from_table(self, key: str, data: List[List[str]]) -> List[str]:
        """Update project data from table data. Returns list of validation errors."""
        errors = []
        try:
            if key == "tasks":
                new_tasks = []
                used_ids: Set[int] = set()
                for row_idx, row in enumerate(data, 1):
                    try:
                        # extract_table_data already skips checkbox column, so data is 0-indexed
                        # Column order: ID, Order, Row, Name, Start Date, Finish Date, Label, Placement
                        # Convert display format to internal format for dates
                        start_date_internal = display_to_internal_date(row[4])  # Start Date is at index 4
                        finish_date_internal = display_to_internal_date(row[5])  # Finish Date is at index 5
                        # Convert old placement values to new ones for backward compatibility
                        placement_value = row[7]  # Placement is at index 7
                        if placement_value in ["To left", "To right"]:
                            placement_value = "Outside"
                        task = Task(
                            task_id=safe_int(row[0]),  # ID is at index 0
                            task_order=safe_float(row[1]),  # Order is at index 1
                            row_number=safe_int(row[2], 1),  # Row is at index 2
                            task_name=row[3],  # Name is at index 3
                            start_date=start_date_internal,  # Store in internal format
                            finish_date=finish_date_internal,  # Store in internal format
                            label_hide=row[6],  # Label is at index 6 (No = Hide, Yes = Show)
                            label_placement=placement_value,  # Placement is at index 7
                            label_alignment="Centre",  # Always use Centre for inside labels (backward compatibility)
                            label_horizontal_offset=1.0,  # Default value (backward compatibility - now uses config value)
                            label_text_colour="black"  # Default color (backward compatibility - not used in rendering)
                        )
                        row_errors = self.validator.validate_task(task, used_ids)
                        if not row_errors:
                            new_tasks.append(task)
                            used_ids.add(task.task_id)
                        else:
                            errors.extend(f"Row {row_idx}: {err}" for err in row_errors)
                    except (ValueError, IndexError) as e:
                        errors.append(f"Row {row_idx}: {str(e)}")
                if not errors:
                    self.tasks = new_tasks
            else:
                setattr(self, key, data)
        except Exception as e:
            logging.error(f"Error in update_from_table: {e}", exc_info=True)
            errors.append(f"Internal error: {str(e)}")
        return errors

    def get_table_data(self, key: str) -> List[List[str]]:
        """Get table data for a given key. Returns list of rows."""
        if key == "tasks":
            return [[str(t.task_id), str(t.task_order), str(t.row_number), t.task_name, 
                    internal_to_display_date(t.start_date),  # Convert to display format
                    internal_to_display_date(t.finish_date),  # Convert to display format
                    t.label_hide, t.label_placement]
                   for t in self.tasks]
        return getattr(self, key, [])
