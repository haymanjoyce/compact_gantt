# test_refactor.py
"""Quick tests to verify refactoring didn't break anything."""

import sys
from pathlib import Path

# Check for PyQt5 first
try:
    from PyQt5.QtWidgets import QApplication, QTableWidget
    from PyQt5.QtCore import QDate
    PYQT5_AVAILABLE = True
except ImportError:
    print("Warning: PyQt5 not available. Some tests will be skipped.")
    print("Please run this test in your development environment where PyQt5 is installed.\n")
    PYQT5_AVAILABLE = False
    QApplication = None
    QTableWidget = None
    QDate = None

# Add project root to path (go up one level from tests folder)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if PYQT5_AVAILABLE:
    from config.app_config import AppConfig
    from models.project import ProjectData
    from ui.tabs.base_tab import BaseTab
    from ui.tabs.pipes_tab import PipesTab
    from ui.tabs.curtains_tab import CurtainsTab
    from ui.tabs.tasks_tab import TasksTab
    from ui.tabs.swimlanes_tab import SwimlanesTab
    from ui.tabs.links_tab import LinksTab
    from ui.tabs.notes_tab import NotesTab
    from ui.table_utils import create_date_widget, extract_date_from_cell
    from config.date_config import DateConfig

def test_base_tab_methods():
    """Test that BaseTab methods work correctly."""
    if not PYQT5_AVAILABLE:
        print("Skipping BaseTab methods test (PyQt5 not available)\n")
        return
    
    print("Testing BaseTab methods...")
    
    app_config = AppConfig()
    project_data = ProjectData(app_config)
    
    # Create a simple test tab (using PipesTab as it's simple)
    pipes_tab = PipesTab(project_data, app_config)
    
    # Test _get_column_index
    id_col = pipes_tab._get_column_index("ID")
    date_col = pipes_tab._get_column_index("Date")
    name_col = pipes_tab._get_column_index("Name")
    invalid_col = pipes_tab._get_column_index("InvalidColumn")
    
    assert id_col is not None, "ID column should be found"
    assert date_col is not None, "Date column should be found"
    assert name_col is not None, "Name column should be found"
    assert invalid_col is None, "Invalid column should return None"
    
    print(f"  ✓ _get_column_index works: ID={id_col}, Date={date_col}, Name={name_col}")
    
    # Test _get_column_name_from_item
    if pipes_tab.pipes_table.rowCount() > 0:
        item = pipes_tab.pipes_table.item(0, id_col)
        if item:
            col_name = pipes_tab._get_column_name_from_item(item)
            assert col_name == "ID", f"Column name should be 'ID', got '{col_name}'"
            print(f"  ✓ _get_column_name_from_item works: {col_name}")
    
    print("  ✓ BaseTab methods test passed\n")

def test_date_helpers():
    """Test date helper functions."""
    if not PYQT5_AVAILABLE:
        print("Skipping date helpers test (PyQt5 not available)\n")
        return
    
    print("Testing date helpers...")
    
    date_config = DateConfig()
    
    # Test create_date_widget
    widget1 = create_date_widget("2025-01-15", date_config)
    assert widget1.date().toString("yyyy-MM-dd") == "2025-01-15", "Date widget should set correct date"
    
    widget2 = create_date_widget("", date_config)
    # Should default to current date
    assert widget2.date() is not None, "Empty date should default to current date"
    
    print("  ✓ create_date_widget works")
    
    # Test extract_date_from_cell (requires a table with a date widget)
    app_config = AppConfig()
    project_data = ProjectData(app_config)
    pipes_tab = PipesTab(project_data, app_config)
    
    # Add a test row if table is empty
    if pipes_tab.pipes_table.rowCount() == 0:
        from ui.table_utils import add_row
        add_row(pipes_tab.pipes_table, "pipes", app_config.tables, pipes_tab, "ID", 
                date_config=app_config.general.ui_date_config)
    
    if pipes_tab.pipes_table.rowCount() > 0:
        date_col = pipes_tab._get_column_index("Date")
        if date_col is not None:
            # Set a date in the widget
            widget = pipes_tab.pipes_table.cellWidget(0, date_col)
            if widget:
                widget.setDate(QDate(2025, 3, 20))
                extracted = extract_date_from_cell(pipes_tab.pipes_table, 0, date_col, date_config)
                assert extracted == "2025-03-20", f"Extracted date should be '2025-03-20', got '{extracted}'"
                print("  ✓ extract_date_from_cell works")
    
    print("  ✓ Date helpers test passed\n")

def test_tab_instantiation():
    """Test that all tabs can be instantiated without errors."""
    if not PYQT5_AVAILABLE:
        print("Skipping tab instantiation test (PyQt5 not available)\n")
        return
    
    print("Testing tab instantiation...")
    
    app_config = AppConfig()
    project_data = ProjectData(app_config)
    
    tabs = [
        ("PipesTab", lambda: PipesTab(project_data, app_config)),
        ("CurtainsTab", lambda: CurtainsTab(project_data, app_config)),
        ("TasksTab", lambda: TasksTab(project_data, app_config)),
        ("SwimlanesTab", lambda: SwimlanesTab(project_data, app_config)),
        ("LinksTab", lambda: LinksTab(project_data, app_config)),
        ("NotesTab", lambda: NotesTab(project_data, app_config)),
    ]
    
    for tab_name, tab_factory in tabs:
        try:
            tab = tab_factory()
            # Verify table_config exists
            assert hasattr(tab, 'table_config'), f"{tab_name} should have table_config"
            # Verify _get_column_index method exists and works
            assert hasattr(tab, '_get_column_index'), f"{tab_name} should have _get_column_index"
            print(f"  ✓ {tab_name} instantiated successfully")
        except Exception as e:
            print(f"  ✗ {tab_name} failed: {e}")
            raise
    
    print("  ✓ All tabs instantiated successfully\n")

def test_column_index_consistency():
    """Test that column index lookups are consistent across tabs."""
    if not PYQT5_AVAILABLE:
        print("Skipping column index consistency test (PyQt5 not available)\n")
        return
    
    print("Testing column index consistency...")
    
    app_config = AppConfig()
    project_data = ProjectData(app_config)
    
    # Test that all tabs can find their ID column
    tabs = [
        PipesTab(project_data, app_config),
        CurtainsTab(project_data, app_config),
        TasksTab(project_data, app_config),
        SwimlanesTab(project_data, app_config),
        LinksTab(project_data, app_config),
        NotesTab(project_data, app_config),
    ]
    
    for tab in tabs:
        id_col = tab._get_column_index("ID")
        assert id_col is not None, f"{tab.__class__.__name__} should find ID column"
        print(f"  ✓ {tab.__class__.__name__} finds ID column at index {id_col}")
    
    print("  ✓ Column index consistency test passed\n")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Refactoring Verification Tests")
    print("=" * 60 + "\n")
    
    if not PYQT5_AVAILABLE:
        print("PyQt5 is not available in this environment.")
        print("Please run this test in your development environment where PyQt5 is installed.")
        print("=" * 60)
        return 1
    
    # Create QApplication if it doesn't exist (required for Qt widgets)
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        test_base_tab_methods()
        test_date_helpers()
        test_tab_instantiation()
        test_column_index_consistency()
        
        print("=" * 60)
        print("✓ All tests passed! Refactoring appears successful.")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
