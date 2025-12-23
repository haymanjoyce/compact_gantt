from typing import List, Dict, Any, Set
from models import FrameConfig, Task
from validators import DataValidator
from datetime import datetime
import logging
from config.app_config import AppConfig
from utils.conversion import safe_int, safe_float, display_to_internal_date, internal_to_display_date

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProjectData:
    def __init__(self):
        app_config = AppConfig()
        self.frame_config = FrameConfig(num_rows=app_config.general.tasks_rows)
        self.tasks: List[Task] = []
        self.links: List[List[str]] = []
        self.swimlanes: List[List[str]] = []
        self.pipes: List[List[str]] = []
        self.curtains: List[List[str]] = []
        self.text_boxes: List[List[str]] = []
        self.validator = DataValidator()

    def to_json(self) -> Dict[str, Any]:
        for t in self.tasks:
            assert hasattr(t, "__dict__"), f"Non-class instance in self.tasks: {t} ({type(t)})"
        
        # Serialize tasks with only necessary fields (exclude redundant defaults)
        tasks_data = []
        for task in self.tasks:
            task_dict = {
                "task_id": task.task_id,
                "task_order": task.task_order,
                "task_name": task.task_name,
                "start_date": task.start_date,
                "finish_date": task.finish_date,
                "row_number": task.row_number,
                "label_placement": task.label_placement,
                "label_hide": task.label_hide,
            }
            # Only save is_milestone if it's explicitly True (auto-detected from dates otherwise)
            if task.is_milestone:
                task_dict["is_milestone"] = True
            # Only save non-default values for backward compatibility fields
            if task.label_alignment != "Centre":
                task_dict["label_alignment"] = task.label_alignment
            if task.label_horizontal_offset != 1.0:
                task_dict["label_horizontal_offset"] = task.label_horizontal_offset
            if task.label_text_colour != "black":
                task_dict["label_text_colour"] = task.label_text_colour
            tasks_data.append(task_dict)
        
        # FrameConfig: save all fields (all are necessary)
        return {
            "frame_config": vars(self.frame_config),
            "tasks": tasks_data,
            "links": self.links,
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
        
        # Handle backward compatibility: migrate old vertical_gridlines to new individual flags
        if "vertical_gridlines" in frame_config_data and "vertical_gridline_years" not in frame_config_data:
            old_value = frame_config_data.pop("vertical_gridlines")
            frame_config_data["vertical_gridline_years"] = old_value
            frame_config_data["vertical_gridline_months"] = old_value
            frame_config_data["vertical_gridline_weeks"] = old_value
            frame_config_data["vertical_gridline_days"] = old_value
        
        project.frame_config = FrameConfig(**frame_config_data)
        
        # Load tasks
        for task_data in data.get("tasks", []):
            project.tasks.append(Task.from_dict(task_data))
        
        # Load other data
        project.links = data.get("links", [])
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
                        # Skip validation for empty rows (ID is empty or 0, or row is too short)
                        if not row or len(row) < 8:
                            continue
                        
                        # Check if ID field is empty - skip this row
                        task_id_str = str(row[0]).strip() if len(row) > 0 else ""
                        if not task_id_str or safe_int(task_id_str) <= 0:
                            continue
                        
                        # extract_table_data already skips checkbox column, so data is 0-indexed
                        # Column order: ID, Order, Row, Name, Start Date, Finish Date, Label, Placement
                        # Convert display format to internal format for dates (handles empty strings)
                        start_date_internal = display_to_internal_date(row[4]) if len(row) > 4 and row[4].strip() else ""
                        finish_date_internal = display_to_internal_date(row[5]) if len(row) > 5 and row[5].strip() else ""
                        # Convert old placement values to new ones for backward compatibility
                        placement_value = row[7] if len(row) > 7 else "Outside"
                        if placement_value in ["To left", "To right"]:
                            placement_value = "Outside"
                        task = Task(
                            task_id=safe_int(row[0]),  # ID is at index 0
                            task_order=safe_float(row[1]),  # Order is at index 1
                            row_number=safe_int(row[2], 1),  # Row is at index 2
                            task_name=row[3] if len(row) > 3 else "",  # Name is at index 3
                            start_date=start_date_internal,  # Store in internal format
                            finish_date=finish_date_internal,  # Store in internal format
                            label_hide=row[6] if len(row) > 6 else "Yes",  # Label is at index 6 (No = Hide, Yes = Show)
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
                    except ValueError as e:
                        # Handle date conversion errors - avoid duplicate "Row X:" prefix
                        error_msg = str(e)
                        # Check if error already has "Row" prefix to avoid duplication
                        if error_msg.startswith("Row "):
                            errors.append(error_msg)
                        else:
                            errors.append(f"Row {row_idx}: {error_msg}")
                    except (IndexError, AttributeError) as e:
                        errors.append(f"Row {row_idx}: {str(e)}")
                if not errors:
                    self.tasks = new_tasks
            elif key == "links":
                # Validate links: check Finish-to-Start constraint and set Valid field
                new_links = []
                for row_idx, row in enumerate(data, 1):
                    try:
                        # Skip empty rows - now expects: [ID, From Task ID, To Task ID, Valid]
                        if not row or len(row) < 4:
                            continue
                        
                        # Extract fields (ID is at index 0, From Task ID at index 1, To Task ID at index 2)
                        from_task_id_str = str(row[1]).strip() if len(row) > 1 else ""
                        to_task_id_str = str(row[2]).strip() if len(row) > 2 else ""
                        
                        # Skip if either ID is empty or invalid
                        from_task_id = safe_int(from_task_id_str)
                        to_task_id = safe_int(to_task_id_str)
                        
                        if from_task_id <= 0 or to_task_id <= 0:
                            # Invalid IDs - set Valid to "No" but still save the link
                            valid_status = "No"
                            if len(row) >= 4:
                                row[3] = valid_status  # Valid is at index 3
                            else:
                                # Ensure row has 4 elements
                                while len(row) < 4:
                                    row.append("")
                                row[3] = valid_status
                            new_links.append(row)
                            continue
                        
                        # Find the tasks to check their dates
                        from_task = None
                        to_task = None
                        for task in self.tasks:
                            if task.task_id == from_task_id:
                                from_task = task
                            if task.task_id == to_task_id:
                                to_task = task
                        
                        # Validate that both tasks exist
                        if not from_task or not to_task:
                            # Task not found - set Valid to "No" but still save the link
                            valid_status = "No"
                            if len(row) >= 4:
                                row[3] = valid_status  # Valid is at index 3
                            else:
                                # Ensure row has 4 elements
                                while len(row) < 4:
                                    row.append("")
                                row[3] = valid_status
                            new_links.append(row)
                            continue
                        
                        # Validate Finish-to-Start constraint: To Task start date must be >= From Task finish date
                        # For milestones, use the single date as both start and finish
                        from_finish_date = from_task.finish_date
                        if not from_finish_date:
                            from_finish_date = from_task.start_date
                        
                        to_start_date = to_task.start_date
                        if not to_start_date:
                            to_start_date = to_task.finish_date
                        
                        # Determine validity
                        valid_status = "Yes"
                        if not from_finish_date or not to_start_date:
                            # Missing dates - cannot validate, set to "No"
                            valid_status = "No"
                        else:
                            try:
                                from_finish = datetime.strptime(from_finish_date, "%Y-%m-%d")
                                to_start = datetime.strptime(to_start_date, "%Y-%m-%d")
                                
                                # Check Finish-to-Start: target task must start on or after source task finishes
                                if to_start < from_finish:
                                    valid_status = "No"
                            except (ValueError, TypeError):
                                # Invalid date format - set to "No"
                                valid_status = "No"
                        
                        # Update or add Valid field (at index 3)
                        if len(row) >= 4:
                            row[3] = valid_status
                        else:
                            # Ensure row has 4 elements: [ID, From Task ID, To Task ID, Valid]
                            while len(row) < 4:
                                row.append("")
                            row[3] = valid_status
                        
                        # Link is saved regardless of validity
                        new_links.append(row)
                    except (IndexError, AttributeError) as e:
                        errors.append(f"Row {row_idx}: {str(e)}")
                
                # Always update links (even if some are invalid)
                self.links = new_links
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
        elif key == "links":
            # Ensure all links have 4 elements: [ID, From Task ID, To Task ID, Valid]
            result = []
            for link in getattr(self, key, []):
                if len(link) >= 2:  # At minimum need From Task ID
                    # Ensure all 4 fields exist
                    if len(link) >= 4:
                        result.append(link[:4])  # Take first 4 elements
                    elif len(link) == 3:
                        # Old format without ID - generate one
                        max_id = max([int(l[0]) for l in result if len(l) > 0 and l[0].isdigit()], default=0) if result else 0
                        result.append([str(max_id + 1), link[0], link[1], link[2] if len(link) > 2 else "Yes"])
                    elif len(link) == 2:
                        # Old format without ID and Valid - generate both
                        max_id = max([int(l[0]) for l in result if len(l) > 0 and l[0].isdigit()], default=0) if result else 0
                        result.append([str(max_id + 1), link[0], link[1], "Yes"])
                    else:
                        # Default with ID
                        max_id = max([int(l[0]) for l in result if len(l) > 0 and l[0].isdigit()], default=0) if result else 0
                        result.append([str(max_id + 1), "", "", "Yes"])
            return result
        return getattr(self, key, [])
