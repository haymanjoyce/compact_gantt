# Compact Gantt

A PyQt5-based tool for creating compact Gantt charts with SVG output.

## Features
- Customizable chart dimensions, margins, and gridlines
- Time frames with proportional widths
- Tasks and milestones with flexible label placement
- Multiple scales (years, months, weeks, days)
- Import/export project data as JSON

## Quick Start
```bash
# Install dependencies
pip install -r requirements-minimal.txt

# Run the application
python main.py
```

## Requirements
- Python 3.8+
- PyQt5
- svgwrite

## Usage
1. Launch the application
2. Configure chart settings in the Layout tab
3. Add time frames and tasks
4. Click "Update Image" to generate the SVG chart

## Development
```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python tests/test_environment.py
```

## Project Structure
- `ui/` - User interface components
- `services/` - Business logic
- `models/` - Data structures
- `repositories/` - File I/O
- `tests/` - Test files