from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from ..table_utils import add_row, remove_row, show_context_menu

class SwimlanesTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, table_configs):
        super().__init__()
        self.project_data = project_data
        self.table_configs = table_configs
        self.setup_ui()
        self._load_initial_data()
        self.swimlanes_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        self.swimlanes_table = QTableWidget(2, len(self.table_configs["swimlanes"]["columns"]))
        self.swimlanes_table.setHorizontalHeaderLabels(self.table_configs["swimlanes"]["columns"])
        self.swimlanes_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.swimlanes_table.customContextMenuRequested.connect(
            lambda pos: show_context_menu(pos, self.swimlanes_table, "swimlanes", self, self.table_configs))
        self.swimlanes_table.setSortingEnabled(True)
        self.swimlanes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.swimlanes_table.resizeColumnsToContents()
        layout.addWidget(self.swimlanes_table)

        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Swimlane")
        remove_btn = QPushButton("Remove Swimlane")
        add_btn.clicked.connect(lambda: add_row(self.swimlanes_table, "swimlanes", self.table_configs, self))
        remove_btn.clicked.connect(lambda: remove_row(self.swimlanes_table, "swimlanes", self.table_configs, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_initial_data(self):
        config = self.table_configs["swimlanes"]
        table_data = self.project_data.get_table_data("swimlanes")
        row_count = max(len(table_data), config["min_rows"])
        self.swimlanes_table.setRowCount(row_count)
        self._initializing = True

        if table_data:
            for row_idx, row_data in enumerate(table_data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.swimlanes_table.setItem(row_idx, col_idx, item)
        else:
            for row_idx in range(row_count):
                defaults = config["defaults"](row_idx)
                for col_idx, default in enumerate(defaults):
                    item = QTableWidgetItem(str(default))
                    self.swimlanes_table.setItem(row_idx, col_idx, item)

        self._initializing = False

    def _sync_data(self):
        try:
            swimlanes_data = self._extract_table_data()
            invalid_cells = set()
            for row_idx, row in enumerate(swimlanes_data):
                try:
                    from_row = int(row[0] or 1)
                    to_row = int(row[1] or 1)
                    if from_row <= 0 or to_row <= 0:
                        invalid_cells.add((row_idx, 0, "non-positive"))
                        invalid_cells.add((row_idx, 1, "non-positive"))
                    elif from_row > to_row:
                        invalid_cells.add((row_idx, 0, "from-greater-than-to"))
                        invalid_cells.add((row_idx, 1, "from-greater-than-to"))
                    elif to_row > self.project_data.frame_config.num_rows:
                        invalid_cells.add((row_idx, 1, "exceeds-num-rows"))
                except ValueError:
                    invalid_cells.add((row_idx, 0, "invalid"))
                    invalid_cells.add((row_idx, 1, "invalid"))

            self.swimlanes_table.blockSignals(True)
            for row_idx in range(self.swimlanes_table.rowCount()):
                for col in (0, 1):
                    item = self.swimlanes_table.item(row_idx, col)
                    tooltip = ""
                    if item:
                        if any((row_idx, col, reason) in invalid_cells for reason in ["non-positive"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Swimlane {row_idx + 1}: {'From' if col == 0 else 'To'} Row Number must be positive"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["invalid"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Swimlane {row_idx + 1}: {'From' if col == 0 else 'To'} Row Number must be an integer"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["from-greater-than-to"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Swimlane {row_idx + 1}: From Row Number must not exceed To Row Number"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["exceeds-num-rows"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Swimlane {row_idx + 1}: To Row Number exceeds chart rows"
                        else:
                            item.setBackground(QBrush())
                    else:
                        item = QTableWidgetItem("")
                        item.setBackground(QBrush(Qt.yellow))
                        tooltip = f"Swimlane {row_idx + 1}: {'From' if col == 0 else 'To'} Row Number required"
                        self.swimlanes_table.setItem(row_idx, col, item)
                    item.setToolTip(tooltip)
            self.swimlanes_table.blockSignals(False)

            if invalid_cells:
                raise ValueError("Fix highlighted cells in Swimlanes tab")

            self.project_data.update_from_table("swimlanes", swimlanes_data)
            self.data_updated.emit(self.project_data.to_json())
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self):
        data = []
        for row in range(self.swimlanes_table.rowCount()):
            row_data = []
            for col in range(self.swimlanes_table.columnCount()):
                item = self.swimlanes_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data