from PyQt5.QtWidgets import (QWidget, QTableWidget, QVBoxLayout, QPushButton, 
                           QGridLayout, QHeaderView, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from typing import List, Dict, Any, Set, Tuple
import logging
from ui.table_utils import add_row, remove_row, CheckBoxWidget

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SwimlanesTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, app_config):
        super().__init__()
        self.project_data = project_data
        self.app_config = app_config
        self.table_config = app_config.get_table_config("swimlanes")
        self._initializing = True
        self.setup_ui()
        self._load_initial_data()
        self.swimlanes_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create table
        self.swimlanes_table = QTableWidget(0, len(self.table_config.columns) + 1)  # +1 for checkbox
        headers = ["Select"] + [col.name for col in self.table_config.columns]
        self.swimlanes_table.setHorizontalHeaderLabels(headers)
        self.swimlanes_table.setSortingEnabled(True)
        self.swimlanes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.swimlanes_table)

        # Create buttons
        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Swimlane")
        remove_btn = QPushButton("Remove Swimlane")
        add_btn.clicked.connect(lambda: add_row(self.swimlanes_table, "swimlanes", 
                                              self.app_config.tables, self))
        remove_btn.clicked.connect(lambda: remove_row(self.swimlanes_table, "swimlanes", 
                                                    self.app_config.tables, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _load_initial_data(self):
        try:
            table_data = self.project_data.get_table_data("swimlanes")
            row_count = max(len(table_data), self.table_config.min_rows)
            self.swimlanes_table.setRowCount(row_count)

            for row_idx in range(row_count):
                # Add checkbox first
                checkbox_widget = CheckBoxWidget()
                self.swimlanes_table.setCellWidget(row_idx, 0, checkbox_widget)

                if row_idx < len(table_data):
                    row_data = table_data[row_idx]
                    # Start from column 1 since column 0 is checkbox
                    for col_idx, value in enumerate(row_data, start=1):
                        item = QTableWidgetItem(str(value))
                        self.swimlanes_table.setItem(row_idx, col_idx, item)
                else:
                    defaults = self.table_config.default_generator(row_idx, {})
                    # Skip the first default (checkbox state) and start from index 1
                    for col_idx, default in enumerate(defaults[1:], start=1):
                        item = QTableWidgetItem(str(default))
                        self.swimlanes_table.setItem(row_idx, col_idx, item)

        except Exception as e:
            logging.error(f"Error in _load_initial_data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load initial data: {e}")

    def _validate_row(self, row_data: List[str], row_idx: int) -> List[Tuple[int, str]]:
        """Validate a single row of swimlane data.
        Returns a list of (column_index, error_message) tuples."""
        errors = []
        try:
            # Validate From Row
            from_row = int(row_data[0])
            if from_row <= 0:
                errors.append((1, "From Row must be positive"))

            # Validate To Row
            to_row = int(row_data[1])
            if to_row <= 0:
                errors.append((2, "To Row must be positive"))
            elif to_row < from_row:
                errors.append((2, "To Row must be greater than or equal to From Row"))

            # Validate Title (optional)
            # No validation needed for title as it's optional

            # Validate Color
            color = row_data[3].strip()
            if not color:
                errors.append((4, "Color must not be empty"))

        except (ValueError, IndexError) as e:
            # If we can't parse the numbers, add error messages
            if len(row_data) > 0 and not row_data[0].strip().isdigit():
                errors.append((1, "From Row must be a number"))
            if len(row_data) > 1 and not row_data[1].strip().isdigit():
                errors.append((2, "To Row must be a number"))

        return errors

    def _sync_data(self):
        try:
            swimlanes_data = self._extract_table_data()
            all_errors = []
            
            # Clear all highlights first
            self.swimlanes_table.blockSignals(True)
            for row in range(self.swimlanes_table.rowCount()):
                for col in range(1, self.swimlanes_table.columnCount()):
                    item = self.swimlanes_table.item(row, col)
                    if item:
                        item.setBackground(QBrush())
                        item.setToolTip("")

            # Validate and highlight errors
            for row_idx, row_data in enumerate(swimlanes_data):
                row_errors = self._validate_row(row_data, row_idx)
                for col_idx, error_msg in row_errors:
                    all_errors.append(f"Row {row_idx + 1}: {error_msg}")
                    item = self.swimlanes_table.item(row_idx, col_idx)
                    if item:
                        item.setBackground(QBrush(Qt.yellow))
                        item.setToolTip(error_msg)

            if not all_errors:
                # Only update data if there are no validation errors
                self.project_data.update_from_table("swimlanes", swimlanes_data)
            else:
                QMessageBox.critical(self, "Validation Error", "\n".join(all_errors))

            self.swimlanes_table.blockSignals(False)

        except Exception as e:
            logging.error(f"Error in _sync_data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to sync data: {e}")

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self) -> List[List[str]]:
        """Extract data from table, skipping the checkbox column."""
        data = []
        for row in range(self.swimlanes_table.rowCount()):
            row_data = []
            # Start from column 1 to skip checkbox column
            for col in range(1, self.swimlanes_table.columnCount()):
                item = self.swimlanes_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data