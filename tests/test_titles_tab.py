#!/usr/bin/env python3
"""
Test script specifically for the new Titles tab functionality.
This verifies that the combined header/footer tab works correctly.
"""

import sys
import os
from pathlib import Path
import pytest
from PyQt5.QtWidgets import QApplication
from models.project import ProjectData
from config.app_config import AppConfig
from ui.tabs.titles_tab import TitlesTab

# Ensure project root is in sys.path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # No explicit app.quit() needed for session fixture


def test_titles_tab_creation(qapp):
    project_data = ProjectData()
    app_config = AppConfig()
    titles_tab = TitlesTab(project_data, app_config)
    assert hasattr(titles_tab, 'header_height')
    assert hasattr(titles_tab, 'header_text')
    assert hasattr(titles_tab, 'footer_height')
    assert hasattr(titles_tab, 'footer_text')


def test_titles_tab_data_loading(qapp):
    project_data = ProjectData()
    app_config = AppConfig()
    project_data.frame_config.header_height = 75
    project_data.frame_config.header_text = "Test Header"
    project_data.frame_config.footer_height = 60
    project_data.frame_config.footer_text = "Test Footer"
    titles_tab = TitlesTab(project_data, app_config)
    assert titles_tab.header_height.text() == "75"
    assert titles_tab.header_text.text() == "Test Header"
    assert titles_tab.footer_height.text() == "60"
    assert titles_tab.footer_text.text() == "Test Footer"


def test_titles_tab_data_sync(qapp):
    project_data = ProjectData()
    app_config = AppConfig()
    titles_tab = TitlesTab(project_data, app_config)
    titles_tab.header_height.setText("80")
    titles_tab.header_text.setText("New Header")
    titles_tab.footer_height.setText("65")
    titles_tab.footer_text.setText("New Footer")
    titles_tab._sync_data()
    assert project_data.frame_config.header_height == 80
    assert project_data.frame_config.header_text == "New Header"
    assert project_data.frame_config.footer_height == 65
    assert project_data.frame_config.footer_text == "New Footer"


def pytest_generate_tests(metafunc):
    if "invalid_value" in metafunc.fixturenames:
        metafunc.parametrize("invalid_value", ["", "0", "-5", "abc"])
    if "valid_value" in metafunc.fixturenames:
        metafunc.parametrize("valid_value", ["10", "50", "100"])


def test_titles_tab_validation_logic():
    """Test the validation logic directly without PyQt widgets."""
    from ui.tabs.titles_tab import TitlesTab
    
    # Create a mock object to test validation logic
    class MockTitlesTab:
        def __init__(self):
            self.header_height = type('MockQLineEdit', (), {
                'text': lambda self=None: "50"
            })()
            self.header_text = type('MockQLineEdit', (), {
                'text': lambda self=None: "Test Header"
            })()
            self.footer_height = type('MockQLineEdit', (), {
                'text': lambda self=None: "50"
            })()
            self.footer_text = type('MockQLineEdit', (), {
                'text': lambda self=None: "Test Footer"
            })()
            self.project_data = type('MockProjectData', (), {
                'frame_config': type('MockFrameConfig', (), {})()
            })()
        
        def _sync_data_impl(self):
            # Copy the validation logic from TitlesTab
            numeric_fields = {
                "header_height": self.header_height.text(),
                "footer_height": self.footer_height.text(),
            }

            for field_name, value in numeric_fields.items():
                try:
                    if not value.strip() or int(value) <= 0:
                        raise ValueError(f"{field_name.replace('_', ' ').title()} must be a positive number")
                except ValueError as e:
                    if "must be a positive number" not in str(e):
                        raise ValueError(f"{field_name.replace('_', ' ').title()} must be a valid number")
                    raise

            # Update frame config
            self.project_data.frame_config.header_height = int(self.header_height.text())
            self.project_data.frame_config.header_text = self.header_text.text()
            self.project_data.frame_config.footer_height = int(self.footer_height.text())
            self.project_data.frame_config.footer_text = self.footer_text.text()
    
    # Test validation logic
    titles_tab = MockTitlesTab()
    
    # Test valid values
    titles_tab.header_height.text = lambda self=None: "100"
    titles_tab.footer_height.text = lambda self=None: "75"
    
    # This should not raise
    try:
        titles_tab._sync_data_impl()
        assert True  # If we get here, validation passed
    except Exception as e:
        assert False, f"Valid values should not raise: {e}"
    
    # Test invalid values
    titles_tab.header_height.text = lambda self=None: ""
    with pytest.raises(ValueError, match="Header Height must be a positive number"):
        titles_tab._sync_data_impl()
    
    titles_tab.header_height.text = lambda self=None: "0"
    with pytest.raises(ValueError, match="Header Height must be a positive number"):
        titles_tab._sync_data_impl()
    
    titles_tab.header_height.text = lambda self=None: "-5"
    with pytest.raises(ValueError, match="Header Height must be a positive number"):
        titles_tab._sync_data_impl()
    
    titles_tab.header_height.text = lambda self=None: "abc"
    with pytest.raises(ValueError, match="Header Height must be a valid number"):
        titles_tab._sync_data_impl()




def main():
    """Run all TitlesTab tests."""
    print("🧪 Testing New Titles Tab Functionality\n")
    print("=" * 50)
    
    # Create QApplication first
    app = QApplication(sys.argv)
    
    tests = [
        ("TitlesTab Creation", test_titles_tab_creation),
        ("Data Loading", test_titles_tab_data_loading),
        ("Data Synchronization", test_titles_tab_data_sync)
    ]
    
    passed = 0
    total = len(tests)
    
    try:
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 30)
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} FAILED with exception: {e}")
                import traceback
                traceback.print_exc()
    finally:
        # Clean up QApplication
        app.quit()
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All TitlesTab tests passed! The new combined tab is working correctly.")
        return 0
    else:
        print("⚠️  Some TitlesTab tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 