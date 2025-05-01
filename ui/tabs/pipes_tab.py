from PyQt5.QtWidgets import (QWidget, QTableWidget, QVBoxLayout, QPushButton, 
                           QGridLayout, QHeaderView, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from typing import List, Dict, Any, Tuple
from datetime import datetime
import logging
from ui.table_utils import add_row, remove_row, CheckBoxWidget

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PipesTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, app_config):
        super().__init__()
        self.project_data = project_data
        self.app_config = app_config
        self.table_config = app_config.get_table_config("pipes")
        self._initializing = True
        self.setup_ui()
        self._load_initial_data()
        self.pipes_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create table
        self.pipes_table = QTableWidget(0, len(self.table_config.columns) + 1)  # +1 for checkbox
        headers = ["Select"] + [col.name for col in self.table_config.columns]
        self.pipes_table.setHorizontalHeaderLabels(headers)
        self.pipes_table.setSortingEnabled(True)
        self.pipes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.pipes_table)

        # Create buttons
        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Pipe")
        remove_btn = QPushButton("Remove Pipe")
        add_btn.clicked.connect(lambda: add_row(self.pipes_table, "pipes", 
                                              self.app_config.tables, self))
        remove_btn.clicked.connect(lambda: remove_row(self.pipes_table, "pipes", 
                                                    self.app_config.tables, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _load_initial_data(self):
        try:
            table_data = self.project_data.get_table_data("pipes")
            row_count = max(len(table_data), self.table_config.min_rows)
            self.pipes_table.setRowCount(row_count)

            for row_idx in range(row_count):
                # Add checkbox first
                checkbox_widget = CheckBoxWidget()
                self.pipes_table.setCellWidget(row_idx, 0, checkbox_widget)

                if row_idx < len(table_data):
                    row_data = table_data[row_idx]
                    # Start from column 1 since column 0 is checkbox
                    for col_idx, value in enumerate(row_data, start=1):
                        item = QTableWidgetItem(str(value))
                        self.pipes_table.setItem(row_idx, col_idx, item)
                else:
                    defaults = self.table_config.default_generator(row_idx, {})
                    # Skip the first default (checkbox state) and start from index 1
                    for col_idx, default in enumerate(defaults[1:], start=1):
                        item = QTableWidgetItem(str(default))
                        self.pipes_table.setItem(row_idx, col_idx, item)

        except Exception as e:
            logging.error(f"Error in _load_initial_data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load initial data: {e}")

    def _validate_date(self, date_str: str) -> Tuple[bool, str]:
        """Validate a date string.
        Returns (is_valid, error_message)"""
        if not date_str.strip():
            return False, "Date is required"
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, ""
        except ValueError:
            return False, "Date must be in YYYY-MM-DD format"

    def _validate_color(self, color: str) -> Tuple[bool, str]:
        """Validate a color value.
        Returns (is_valid, error_message)"""
        if not color.strip():
            return False, "Color is required"
        # Could add more color validation here if needed
        return True, ""

    def _validate_row(self, row_data: List[str], row_idx: int) -> List[Tuple[int, str]]:
        """Validate a single row of pipe data.
        Returns a list of (column_index, error_message) tuples."""
        errors = []

        # Validate Date (column 1)
        if len(row_data) > 0:
            is_valid, error_msg = self._validate_date(row_data[0])
            if not is_valid:
                errors.append((1, error_msg))

        # Validate Color (column 2)
        if len(row_data) > 1:
            is_valid, error_msg = self._validate_color(row_data[1])
            if not is_valid:
                errors.append((2, error_msg))

        return errors

    def _sync_data(self):
        try:
            pipes_data = self._extract_table_data()
            all_errors = []
            
            # Clear all highlights first
            self.pipes_table.blockSignals(True)
            for row in range(self.pipes_table.rowCount()):
                for col in range(1, self.pipes_table.columnCount()):
                    item = self.pipes_table.item(row, col)
                    if item:
                        item.setBackground(QBrush())
                        item.setToolTip("")

            # Validate and highlight errors
            for row_idx, row_data in enumerate(pipes_data):
                row_errors = self._validate_row(row_data, row_idx)
                for col_idx, error_msg in row_errors:
                    all_errors.append(f"Row {row_idx + 1}: {error_msg}")
                    item = self.pipes_table.item(row_idx, col_idx)
                    if item:
                        item.setBackground(QBrush(Qt.yellow))
                        item.setToolTip(error_msg)

            if not all_errors:
                # Only update data if there are no validation errors
                self.project_data.update_from_table("pipes", pipes_data)
            else:
                QMessageBox.critical(self, "Validation Error", "\n".join(all_errors))

            self.pipes_table.blockSignals(False)

        except Exception as e:
            logging.error(f"Error in _sync_data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to sync data: {e}")

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self) -> List[List[str]]:
        """Extract data from table, skipping the checkbox column."""
        data = []
        for row in range(self.pipes_table.rowCount()):
            row_data = []
            # Start from column 1 to skip checkbox column
            for col in range(1, self.pipes_table.columnCount()):
                item = self.pipes_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data