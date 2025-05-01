from typing import List, Set, Dict, Any
from datetime import datetime
from models import TimeFrame, Task

class DataValidator:
    @staticmethod
    def validate_time_frame(time_frame: TimeFrame, used_ids: Set[int]) -> List[str]:
        errors = []
        if time_frame.time_frame_id <= 0:
            errors.append("Time Frame ID must be positive")
        if time_frame.time_frame_id in used_ids:
            errors.append("Time Frame ID must be unique")
        try:
            datetime.strptime(time_frame.finish_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Invalid date format")
        if time_frame.width_proportion <= 0:
            errors.append("Width proportion must be positive")
        return errors

    @staticmethod
    def validate_task(task: Task, used_ids: Set[int]) -> List[str]:
        errors = []
        if task.task_id <= 0:
            errors.append("Task ID must be positive")
        if task.task_id in used_ids:
            errors.append("Task ID must be unique")
        try:
            datetime.strptime(task.start_date, "%Y-%m-%d")
            datetime.strptime(task.finish_date, "%Y-%m-%d")
        except ValueError:
            errors.append("Invalid date format")
        if task.row_number <= 0:
            errors.append("Row number must be positive")
        if task.task_order <= 0:
            errors.append("Task order must be positive")
        return errors 