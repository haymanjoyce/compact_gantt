from dataclasses import dataclass
from typing import Tuple


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
    vertical_gridlines: bool = True
    chart_start_date: str = "2024-12-30"
