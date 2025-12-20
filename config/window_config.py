from dataclasses import dataclass

@dataclass
class WindowConfig:
    """Configuration for application window sizes and positioning."""
    # Main window (data entry) settings
    data_entry_width: int = 400
    data_entry_height: int = 500
    data_entry_screen: int = 0  # Which screen to display on (0 = primary screen)
    data_entry_position: str = "center"  # Options: "center", "top_left", "top_right", "bottom_left", "bottom_right", "custom"
    data_entry_x: int = 100  # Custom X position (used when position is "custom")
    data_entry_y: int = 100  # Custom Y position (used when position is "custom")

    # SVG display window settings
    svg_display_width: int = 800
    svg_display_height: int = 600
    svg_display_screen: int = 1  # Which screen to display on (1 = secondary screen if available)
    svg_display_position: str = "center"  # Options: "center", "top_left", "top_right", "bottom_left", "bottom_right", "custom"
    svg_display_x: int = 100  # Custom X position (used when position is "custom")
    svg_display_y: int = 100  # Custom Y position (used when position is "custom")

    def __post_init__(self):
        # Validate positive integers
        for field_name in ["data_entry_width", "data_entry_height", "svg_display_width",
                          "svg_display_height", "data_entry_screen", "data_entry_x", 
                          "data_entry_y", "svg_display_screen", "svg_display_x", "svg_display_y"]:
            value = getattr(self, field_name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative integer")

        # Validate position string
        valid_positions = ["center", "top_left", "top_right", "bottom_left", "bottom_right", "custom"]
        if self.data_entry_position not in valid_positions:
            raise ValueError(f"data_entry_position must be one of: {valid_positions}")
        if self.svg_display_position not in valid_positions:
            raise ValueError(f"svg_display_position must be one of: {valid_positions}")

