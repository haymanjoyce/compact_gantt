from typing import List, Set, Dict, Any
from datetime import datetime
from models import Task
from utils.conversion import is_valid_internal_date


class DataValidator:
    @staticmethod
    def validate_task(task: Task, used_ids: Set[int]) -> List[str]:
        errors = []
        if task.task_id <= 0:
            errors.append("Task ID must be positive")
        if task.task_id in used_ids:
            errors.append("Task ID must be unique")
        if not is_valid_internal_date(task.start_date):
            errors.append("Invalid start date format (should be yyyy-mm-dd)")
        if not is_valid_internal_date(task.finish_date):
            errors.append("Invalid finish date format (should be yyyy-mm-dd)")
        
        # Check if finish date is earlier than start date (only if both dates are valid)
        if is_valid_internal_date(task.start_date) and is_valid_internal_date(task.finish_date):
            try:
                start = datetime.strptime(task.start_date, "%Y-%m-%d")
                finish = datetime.strptime(task.finish_date, "%Y-%m-%d")
                if finish < start:
                    errors.append("Finish date must be on or after start date")
            except (ValueError, TypeError):
                # Date parsing failed - format validation should have caught this, but handle gracefully
                pass
        
        if task.row_number <= 0:
            errors.append("Row number must be positive")
        return errors

    @staticmethod
    def validate_date_format(date_str: str) -> List[str]:
        errors = []
        if not is_valid_internal_date(date_str):
            errors.append("Invalid date format (should be yyyy-mm-dd)")
        return errors

    @staticmethod
    def validate_positive_number(value: float, field_name: str) -> List[str]:
        errors = []
        if value <= 0:
            errors.append(f"{field_name} must be positive")
        return errors

    @staticmethod
    def validate_unique_id(id_value: int, used_ids: Set[int], entity_name: str) -> List[str]:
        errors = []
        if id_value in used_ids:
            errors.append(f"{entity_name} ID must be unique")
        return errors 

