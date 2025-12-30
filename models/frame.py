from dataclasses import dataclass, field
from typing import Tuple
from datetime import datetime
from dateutil.relativedelta import relativedelta


def _default_start_date() -> str:
    """Calculate start date as current date minus 1 month."""
    today = datetime.now().date()
    start_date = today - relativedelta(months=1)
    return start_date.strftime("%Y-%m-%d")


def _default_end_date() -> str:
    """Calculate end date as current date plus 3 months."""
    today = datetime.now().date()
    end_date = today + relativedelta(months=3)
    return end_date.strftime("%Y-%m-%d")


@dataclass
class FrameConfig:
    outer_width: int = 800
    outer_height: int = 600
    header_height: int = 20
    footer_height: int = 20
    margins: Tuple[int, int, int, int] = (10, 10, 10, 10)
    num_rows: int = 1
    header_text: str = ""
    footer_text: str = ""
    horizontal_gridlines: bool = True
    vertical_gridline_years: bool = True
    vertical_gridline_months: bool = True
    vertical_gridline_weeks: bool = False
    vertical_gridline_days: bool = False
    show_row_numbers: bool = False
    chart_start_date: str = field(default_factory=_default_start_date)
    chart_end_date: str = field(default_factory=_default_end_date)
    show_years: bool = True
    show_months: bool = True
    show_weeks: bool = True
    show_days: bool = True
