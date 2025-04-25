from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from datetime import datetime
from ..table_utils import add_row, remove_row, show_context_menu

class CurtainsTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, table_configs):
        super().__init__()
        self.project_data = project_data
        self.table_configs = table_configs
        self.setup_ui()
        self._load_initial_data()
        self.curtains_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        self.curtains_table = QTableWidget(2, len(self.table_configs["curtains"]["columns"]))
        self.curtains_table.setHorizontalHeaderLabels(self.table_configs["curtains"]["columns"])
        self.curtains_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.curtains_table.customContextMenuRequested.connect(
            lambda pos: show_context_menu(pos, self.curtains_table, "curtains", self, self.table_configs))
        self.curtains_table.setSortingEnabled(True)
        self.curtains_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.curtains_table.resizeColumnsToContents()
        layout.addWidget(self.curtains_table)

        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Curtain")
        remove_btn = QPushButton("Remove Curtain")
        add_btn.clicked.connect(lambda: add_row(self.curtains_table, "curtains", self.table_configs, self))
        remove_btn.clicked.connect(lambda: remove_row(self.curtains_table, "curtains", self.table_configs, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_initial_data(self):
        config = self.table_configs["curtains"]
        table_data = self.project_data.get_table_data("curtains")
        row_count = max(len(table_data), config["min_rows"])
        self.curtains_table.setRowCount(row_count)
        self._initializing = True

        if table_data:
            for row_idx, row_data in enumerate(table_data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.curtains_table.setItem(row_idx, col_idx, item)
        else:
            for row_idx in range(row_count):
                defaults = config["defaults"](row_idx)
                for col_idx, default in enumerate(defaults):
                    item = QTableWidgetItem(str(default))
                    self.curtains_table.setItem(row_idx, col_idx, item)

        self._initializing = False

    def _sync_data(self):
        try:
            curtains_data = self._extract_table_data()
            invalid_cells = set()
            for row_idx, row in enumerate(curtains_data):
                from_date, to_date = row[0], row[1]
                try:
                    from_dt = datetime.strptime(from_date, "%Y-%m-%d") if from_date else None
                except ValueError:
                    invalid_cells.add((row_idx, 0, "invalid format"))
                    from_dt = None
                try:
                    to_dt = datetime.strptime(to_date, "%Y-%m-%d") if to_date else None
                except ValueError:
                    invalid_cells.add((row_idx, 1, "invalid format"))
                    to_dt = None
                if from_dt and to_dt and from_dt > to_dt:
                    invalid_cells.add((row_idx, 0, "from-after-to"))
                    invalid_cells.add((row_idx, 1, "from-after-to"))

            self.curtains_table.blockSignals(True)
            for row_idx in range(self.curtains_table.rowCount()):
                for col in (0, 1):
                    item = self.curtains_table.item(row_idx, col)
                    tooltip = ""
                    if item and item.text():
                        if any((row_idx, col, reason) in invalid_cells for reason in ["invalid format"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Curtain {row_idx + 1}: {'From' if col == 0 else 'To'} Date must be yyyy-MM-dd"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["from-after-to"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Curtain {row_idx + 1}: From Date cannot be after To Date"
                        else:
                            item.setBackground(QBrush())
                    else:
                        item = QTableWidgetItem("")
                        item.setBackground(QBrush(Qt.yellow))
                        tooltip = f"Curtain {row_idx + 1}: {'From' if col == 0 else 'To'} Date required"
                        self.curtains_table.setItem(row_idx, col, item)
                    item.setToolTip(tooltip)
            self.curtains_table.blockSignals(False)

            if invalid_cells:
                raise ValueError("Fix highlighted cells in Curtains tab")

            self.project_data.update_from_table("curtains", curtains_data)
            self.data_updated.emit(self.project_data.to_json())
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self):
        data = []
        for row in range(self.curtains_table.rowCount()):
            row_data = []
            for col in range(self.curtains_table.columnCount()):
                item = self.curtains_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data