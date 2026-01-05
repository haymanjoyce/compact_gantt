from dataclasses import dataclass, field
from PyQt5.QtGui import QColor


@dataclass
class UIConfig:
    """Configuration for UI styling and appearance."""
    # Read-only cell background color (light gray - darker to distinguish from inactive selection)
    read_only_bg_color: QColor = field(default_factory=lambda: QColor(220, 220, 220))
    
    # Table header border color
    table_header_border_color: str = "#c0c0c0"
    
    # Table gridline color (darker to be visible against read-only background)
    table_gridline_color: str = "#a0a0a0"
    
    @property
    def table_header_stylesheet(self) -> str:
        """Generate table header stylesheet with border styling."""
        return f"""
            QHeaderView::section {{
                border-bottom: 1px solid {self.table_header_border_color};
                border-right: 1px solid {self.table_header_border_color};
                border-top: none;
                border-left: none;
            }}
        """
    
    @property
    def table_stylesheet(self) -> str:
        """Generate combined table stylesheet with header and gridline styling."""
        return f"""
            QHeaderView::section {{
                border-bottom: 1px solid {self.table_header_border_color};
                border-right: 1px solid {self.table_header_border_color};
                border-top: none;
                border-left: none;
            }}
            QTableWidget {{
                gridline-color: {self.table_gridline_color};
            }}
        """

