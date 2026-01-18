from dataclasses import dataclass
from typing import Dict


# Mapping of display names to (qt_format, python_format) tuples
DATE_FORMAT_OPTIONS: Dict[str, tuple] = {
    "dd/MM/yyyy": ("dd/MM/yyyy", "%d/%m/%Y"),  # British/European (e.g., 01/01/2025)
    "MM/dd/yyyy": ("MM/dd/yyyy", "%m/%d/%Y"),  # US (e.g., 01/01/2025)
    "yyyy-MM-dd": ("yyyy-MM-dd", "%Y-%m-%d"),  # ISO (e.g., 2025-01-01)
    "dd-MM-yyyy": ("dd-MM-yyyy", "%d-%m-%Y"),  # European with dashes (e.g., 01-01-2025)
    "dd MMM yyyy": ("dd MMM yyyy", "%d %b %Y"),  # Long format (e.g., 01 Jan 2025)
}


@dataclass
class DateConfig:
    """Configuration for date formats used throughout the application.
    
    This centralizes date format strings to ensure consistency across:
    - UI date pickers (Qt QDateEdit)
    - Date parsing and validation (Python strptime/strftime)
    - Excel import/export
    - Internal storage (always ISO format: yyyy-mm-dd)
    """
    # Qt format string for QDateEdit displayFormat (e.g., "dd/MM/yyyy")
    display_format_qt: str = "dd/MM/yyyy"
    
    # Python format string for strptime/strftime (e.g., "%d/%m/%Y")
    display_format_python: str = "%d/%m/%Y"
    
    # Internal storage format (ISO format, always yyyy-mm-dd)
    internal_format: str = "%Y-%m-%d"
    
    def get_qt_format(self) -> str:
        """Get Qt format string for QDateEdit widgets."""
        return self.display_format_qt
    
    def get_python_format(self) -> str:
        """Get Python format string for strptime/strftime operations."""
        return self.display_format_python
    
    def get_internal_format(self) -> str:
        """Get internal storage format (always ISO: yyyy-mm-dd)."""
        return self.internal_format
    
    @classmethod
    def from_format_name(cls, format_name: str) -> 'DateConfig':
        """Create DateConfig from a format name (key in DATE_FORMAT_OPTIONS).
        
        Args:
            format_name: Format name from DATE_FORMAT_OPTIONS (e.g., "dd/MM/yyyy")
            
        Returns:
            DateConfig instance with the specified format
            
        Raises:
            ValueError: If format_name is not in DATE_FORMAT_OPTIONS
        """
        if format_name not in DATE_FORMAT_OPTIONS:
            raise ValueError(f"Unknown format name: {format_name}. Available: {list(DATE_FORMAT_OPTIONS.keys())}")
        
        qt_format, python_format = DATE_FORMAT_OPTIONS[format_name]
        return cls(
            display_format_qt=qt_format,
            display_format_python=python_format,
            internal_format="%Y-%m-%d"  # Always ISO format for internal storage
        )
    
    def get_format_name(self) -> str:
        """Get the format name (key) that matches this DateConfig's formats.
        
        Returns:
            Format name if found in DATE_FORMAT_OPTIONS, or None if no match
        """
        for format_name, (qt_fmt, py_fmt) in DATE_FORMAT_OPTIONS.items():
            if self.display_format_qt == qt_fmt and self.display_format_python == py_fmt:
                return format_name
        return None
