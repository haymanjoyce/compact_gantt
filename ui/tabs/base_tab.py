from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidget, QHeaderView, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional
import logging

class BaseTab(QWidget):
    """Base class for all tab widgets to eliminate code duplication."""
    
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, app_config):
        super().__init__()
        self.project_data = project_data
        self.app_config = app_config
        self._initializing = True
        self.setup_ui()
        self._load_initial_data()
        self._initializing = False
        self._connect_signals()
    
    def _get_column_index(self, column_name: str) -> Optional[int]:
        """Get the column index for a given column name using key-based lookup.
        
        Args:
            column_name: Name of the column to find (key-based, not index-based)
            
        Returns:
            Column index if found, None otherwise
        """
        if not hasattr(self, 'table_config') or not self.table_config:
            return None
        for idx, col_config in enumerate(self.table_config.columns):
            if col_config.name == column_name:
                return idx
        return None
    
    def _get_column_name_from_item(self, item) -> Optional[str]:
        """Get the column name (key) from a table item using key-based lookup.
        
        Args:
            item: QTableWidgetItem to get column name for
            
        Returns:
            Column name if found, None otherwise
        """
        if item is None:
            return None
        if not hasattr(self, 'table_config') or not self.table_config:
            return None
        try:
            col_idx = item.column()
            if not isinstance(col_idx, int) or col_idx < 0 or col_idx >= len(self.table_config.columns):
                return None
            return self.table_config.columns[col_idx].name
        except (IndexError, AttributeError):
            return None

    def setup_ui(self):
        """Override this method to set up the UI for each tab."""
        raise NotImplementedError("Subclasses must implement setup_ui")

    def _load_initial_data(self):
        """Override this method to load initial data for each tab."""
        try:
            self._load_initial_data_impl()
        except Exception as e:
            logging.error(f"Error in _load_initial_data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load initial data: {e}")

    def _load_initial_data_impl(self):
        """Override this method to implement specific data loading logic."""
        pass

    def _connect_signals(self):
        """Override this method to connect signals for each tab."""
        pass

    def _sync_data_if_not_initializing(self):
        """Common method to prevent data sync during initialization."""
        if not self._initializing:
            self._sync_data()

    def _sync_data(self):
        """Override this method to implement specific data synchronization logic."""
        try:
            self._sync_data_impl()
        except ValueError as e:
            # Validation errors are expected user input errors - show message but don't crash
            logging.error(f"Error in _sync_data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")
        except Exception as e:
            # Unexpected errors - log, show message, and re-raise for tests
            logging.error(f"Error in _sync_data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to save data: {e}")
            raise  # Re-raise the exception so tests can catch it

    def _sync_data_impl(self):
        """Override this method to implement specific data sync logic."""
        pass
    
    def _set_detail_form_enabled(self, widgets, enabled):
        """Helper method to enable/disable multiple detail form widgets.
        
        Args:
            widgets: List of QWidget objects (QComboBox, QLineEdit, etc.) to enable/disable.
                     Can also be a single widget or None (will be safely ignored).
            enabled: Boolean indicating whether widgets should be enabled
        """
        if widgets is None:
            return
        if not isinstance(widgets, list):
            widgets = [widgets]
        for widget in widgets:
            if widget is not None:
                widget.setEnabled(enabled)
    
    def _setup_table_base(self, table: QTableWidget, selection_mode: int = QTableWidget.SingleSelection):
        """Apply common table styling and behavior settings.
        
        Args:
            table: QTableWidget to configure
            selection_mode: Selection mode (QTableWidget.SingleSelection or QTableWidget.ExtendedSelection)
        """
        table.setAlternatingRowColors(False)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(selection_mode)
        table.setShowGrid(True)
        table.verticalHeader().setVisible(False)
        table.setStyleSheet(self.app_config.general.table_stylesheet)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setSortingEnabled(True)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)