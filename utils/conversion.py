from typing import Union, Optional
from datetime import datetime
from config.date_config import DateConfig

def safe_int(value: Union[str, int, float, None], default: int = 0) -> int:
    """Safely convert a value to int, returning default if conversion fails."""
    if value is None:
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_float(value: Union[str, int, float, None], default: float = 0.0) -> float:
    """Safely convert a value to float, returning default if conversion fails."""
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def normalize_display_date(date_str: str, date_config: Optional[DateConfig] = None) -> str:
    """
    Normalize a date string to display format, handling flexible input formats.
    
    Supports:
    - Single or double digit days/months: 1/1/25, 01/01/25, 1/01/2025
    - 2-digit years (assumes 20xx): 25 → 2025, 99 → 2099
    - 4-digit years: 2025 → 2025
    
    Args:
        date_str: Date string in flexible d/m/yy or d/m/yyyy format
        date_config: Optional DateConfig instance. If None, uses default dd/mm/yyyy format.
        
    Returns:
        Date string in normalized display format (from date_config or default)
        
    Raises:
        ValueError: If the date cannot be normalized
    """
    if not date_str or not date_str.strip():
        return ""
    
    # Use default config if not provided (backward compatibility)
    if date_config is None:
        date_config = DateConfig()
    
    date_str = date_str.strip()
    parts = date_str.split('/')
    
    if len(parts) != 3:
        raise ValueError(f"Invalid date format. Expected d/m/yyyy or d/m/yy, got: {date_str}")
    
    try:
        day = int(parts[0])
        month = int(parts[1])
        year_str = parts[2]
        
        # Normalize day and month to 2 digits
        day_str = f"{day:02d}"
        month_str = f"{month:02d}"
        
        # Handle year - if 2 digits, assume 20xx
        if len(year_str) == 2:
            year_int = int(year_str)
            year_str = f"20{year_int:02d}"  # 25 → 2025, 99 → 2099
        elif len(year_str) == 4:
            # Already 4 digits, use as-is
            pass
        else:
            raise ValueError(f"Invalid year format. Expected 2 or 4 digits, got: {year_str}")
        
        # Validate the normalized date by parsing it with the config format
        normalized = f"{day_str}/{month_str}/{year_str}"
        datetime.strptime(normalized, date_config.get_python_format())  # Validate
        return normalized
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid date format. Expected d/m/yyyy or d/m/yy, got: {date_str}") from e

def display_to_internal_date(display_date: str, date_config: Optional[DateConfig] = None) -> str:
    """
    Convert date from flexible display format to yyyy-mm-dd internal format.
    
    Args:
        display_date: Date string in flexible d/m/yy or d/m/yyyy format
        date_config: Optional DateConfig instance. If None, uses default dd/mm/yyyy format.
        
    Returns:
        Date string in yyyy-mm-dd format (ISO format)
        
    Raises:
        ValueError: If the date format is invalid
    """
    if not display_date or not display_date.strip():
        return ""
    
    # Use default config if not provided (backward compatibility)
    if date_config is None:
        date_config = DateConfig()
    
    try:
        # Normalize to display format first
        normalized = normalize_display_date(display_date, date_config)
        # Parse normalized format using config
        date_obj = datetime.strptime(normalized, date_config.get_python_format())
        # Return in yyyy-mm-dd format (always ISO format for internal storage)
        return date_obj.strftime(date_config.get_internal_format())
    except ValueError as e:
        raise ValueError(f"Invalid date format. Expected d/m/yyyy or d/m/yy, got: {display_date}") from e

def internal_to_display_date(internal_date: str, date_config: Optional[DateConfig] = None) -> str:
    """
    Convert date from yyyy-mm-dd internal format to display format.
    
    Args:
        internal_date: Date string in yyyy-mm-dd format (ISO format)
        date_config: Optional DateConfig instance. If None, uses default dd/mm/yyyy format.
        
    Returns:
        Date string in display format (from date_config or default)
        
    Raises:
        ValueError: If the date format is invalid
    """
    if not internal_date or not internal_date.strip():
        return ""
    
    # Use default config if not provided (backward compatibility)
    if date_config is None:
        date_config = DateConfig()
    
    try:
        # Parse yyyy-mm-dd format (always ISO format for internal storage)
        date_obj = datetime.strptime(internal_date.strip(), date_config.get_internal_format())
        # Return in display format from config
        return date_obj.strftime(date_config.get_python_format())
    except ValueError:
        raise ValueError(f"Invalid date format. Expected yyyy-mm-dd, got: {internal_date}")

def is_valid_display_date(date_str: str, date_config: Optional[DateConfig] = None) -> bool:
    """
    Check if a date string is in valid flexible date format.
    
    Args:
        date_str: Date string to validate
        date_config: Optional DateConfig instance. If None, uses default dd/mm/yyyy format.
        
    Returns:
        True if valid, False otherwise
    """
    if not date_str or not date_str.strip():
        return False
    
    try:
        normalize_display_date(date_str, date_config)
        return True
    except ValueError:
        return False

def is_valid_internal_date(date_str: str) -> bool:
    """
    Check if a date string is in valid yyyy-mm-dd format.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not date_str or not date_str.strip():
        return False
    
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False

def parse_internal_date(date_str: str) -> Optional[datetime]:
    """
    Safely parse an internal date string (yyyy-mm-dd format), returning None if invalid.
    
    This is a centralized function to replace all hardcoded datetime.strptime(..., "%Y-%m-%d") calls.
    
    Args:
        date_str: Date string in yyyy-mm-dd format (internal format)
        
    Returns:
        datetime object if valid, None otherwise
    """
    if not date_str or not date_str.strip():
        return None
    
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d")
    except (ValueError, TypeError):
        return None

def compare_internal_dates(date1_str: str, date2_str: str) -> Optional[bool]:
    """
    Compare two internal date strings (yyyy-mm-dd format).
    
    Args:
        date1_str: First date string in yyyy-mm-dd format
        date2_str: Second date string in yyyy-mm-dd format
        
    Returns:
        True if date1 < date2, False if date1 >= date2, None if either date is invalid
    """
    date1 = parse_internal_date(date1_str)
    date2 = parse_internal_date(date2_str)
    if date1 and date2:
        return date1 < date2
    return None