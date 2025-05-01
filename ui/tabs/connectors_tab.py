from PyQt5.QtWidgets import (QWidget, QTableWidget, QVBoxLayout, QPushButton, 
                           QGridLayout, QHeaderView, QTableWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from typing import List, Dict, Any
import logging
from ui.table_utils import add_row, remove_row, CheckBoxWidget

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConnectorsTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, app_config):
        super().__init__()
        self.project_data = project_data
        self.app_config = app_config
        self.table_config = app_config.get_table_config("connectors")
        self._initializing = True
        self.setup_ui()
        self._load_initial_data()
        self.connectors_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create table
        self.connectors_table = QTableWidget(0, len(self.table_config.columns) + 1)  # +1 for checkbox
        headers = ["Select"] + [col.name for col in self.table_config.columns]
        self.connectors_table.setHorizontalHeaderLabels(headers)
        self.connectors_table.setSortingEnabled(True)
        self.connectors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.connectors_table)

        # Create buttons
        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Connector")
        remove_btn = QPushButton("Remove Connector")
        add_btn.clicked.connect(lambda: add_row(self.connectors_table, "connectors", 
                                              self.app_config.tables, self))
        remove_btn.clicked.connect(lambda: remove_row(self.connectors_table, "connectors", 
                                                    self.app_config.tables, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _load_initial_data(self):
        try:
            table_data = self.project_data.get_table_data("connectors")
            row_count = max(len(table_data), self.table_config.min_rows)
            self.connectors_table.setRowCount(row_count)

            for row_idx in range(row_count):
                # Add checkbox first
                checkbox_widget = CheckBoxWidget()
                self.connectors_table.setCellWidget(row_idx, 0, checkbox_widget)

                if row_idx < len(table_data):
                    row_data = table_data[row_idx]
                    # Start from column 1 since column 0 is checkbox
                    for col_idx, value in enumerate(row_data, start=1):
                        item = QTableWidgetItem(str(value))
                        self.connectors_table.setItem(row_idx, col_idx, item)
                else:
                    defaults = self.table_config.default_generator(row_idx, {})
                    # Skip the first default (checkbox state) and start from index 1
                    for col_idx, default in enumerate(defaults[1:], start=1):
                        item = QTableWidgetItem(str(default))
                        self.connectors_table.setItem(row_idx, col_idx, item)

        except Exception as e:
            logging.error(f"Error in _load_initial_data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to load initial data: {e}")

    def _sync_data(self):
        try:
            connectors_data = self._extract_table_data()
            errors = self.project_data.update_from_table("connectors", connectors_data)

            # Clear all highlights first
            self.connectors_table.blockSignals(True)
            for row in range(self.connectors_table.rowCount()):
                for col in range(1, self.connectors_table.columnCount()):  # Skip checkbox column
                    item = self.connectors_table.item(row, col)
                    if item:
                        item.setBackground(QBrush())
                        item.setToolTip("")

            # Highlight cells with errors
            if errors:
                for error in errors:
                    if error.startswith("Row"):
                        try:
                            row_str = error.split(":")[0].replace("Row ", "")
                            row_idx = int(row_str) - 1
                            # Highlight the entire row
                            for col in range(1, self.connectors_table.columnCount()):
                                item = self.connectors_table.item(row_idx, col)
                                if item:
                                    item.setBackground(QBrush(Qt.yellow))
                                    item.setToolTip(error.split(":", 1)[1].strip())
                        except (ValueError, IndexError):
                            logging.error(f"Failed to parse error message: {error}")
                            continue

                QMessageBox.critical(self, "Error", "\n".join(errors))

            self.connectors_table.blockSignals(False)

        except Exception as e:
            logging.error(f"Error in _sync_data: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to sync data: {e}")

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self) -> List[List[str]]:
        """Extract data from table, skipping the checkbox column."""
        data = []
        for row in range(self.connectors_table.rowCount()):
            row_data = []
            # Start from column 1 to skip checkbox column
            for col in range(1, self.connectors_table.columnCount()):
                item = self.connectors_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data