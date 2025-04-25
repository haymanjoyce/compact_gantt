from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from datetime import datetime
from ..table_utils import add_row, remove_row, show_context_menu

class PipesTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, table_configs):
        super().__init__()
        self.project_data = project_data
        self.table_configs = table_configs
        self.setup_ui()
        self._load_initial_data()
        self.pipes_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        self.pipes_table = QTableWidget(2, len(self.table_configs["pipes"]["columns"]))
        self.pipes_table.setHorizontalHeaderLabels(self.table_configs["pipes"]["columns"])
        self.pipes_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pipes_table.customContextMenuRequested.connect(
            lambda pos: show_context_menu(pos, self.pipes_table, "pipes", self, self.table_configs))
        self.pipes_table.setSortingEnabled(True)
        self.pipes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.pipes_table.resizeColumnsToContents()
        layout.addWidget(self.pipes_table)

        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Pipe")
        remove_btn = QPushButton("Remove Pipe")
        add_btn.clicked.connect(lambda: add_row(self.pipes_table, "pipes", self.table_configs, self))
        remove_btn.clicked.connect(lambda: remove_row(self.pipes_table, "pipes", self.table_configs, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_initial_data(self):
        config = self.table_configs["pipes"]
        table_data = self.project_data.get_table_data("pipes")
        row_count = max(len(table_data), config["min_rows"])
        self.pipes_table.setRowCount(row_count)
        self._initializing = True

        if table_data:
            for row_idx, row_data in enumerate(table_data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.pipes_table.setItem(row_idx, col_idx, item)
        else:
            for row_idx in range(row_count):
                defaults = config["defaults"](row_idx)
                for col_idx, default in enumerate(defaults):
                    item = QTableWidgetItem(str(default))
                    self.pipes_table.setItem(row_idx, col_idx, item)

        self._initializing = False

    def _sync_data(self):
        try:
            pipes_data = self._extract_table_data()
            invalid_cells = set()
            for row_idx, row in enumerate(pipes_data):
                date = row[0] or ""
                if date:
                    try:
                        datetime.strptime(date, "%Y-%m-%d")
                    except ValueError:
                        invalid_cells.add((row_idx, 0, "invalid format"))

            self.pipes_table.blockSignals(True)
            for row_idx in range(self.pipes_table.rowCount()):
                item = self.pipes_table.item(row_idx, 0)
                tooltip = ""
                if item and item.text():
                    if any((row_idx, 0, reason) in invalid_cells for reason in ["invalid format"]):
                        item.setBackground(QBrush(Qt.yellow))
                        tooltip = f"Pipe {row_idx + 1}: Date must be yyyy-MM-dd"
                    else:
                        item.setBackground(QBrush())
                else:
                    item = QTableWidgetItem("")
                    item.setBackground(QBrush(Qt.yellow))
                    tooltip = f"Pipe {row_idx + 1}: Date required"
                    self.pipes_table.setItem(row_idx, 0, item)
                item.setToolTip(tooltip)
            self.pipes_table.blockSignals(False)

            if invalid_cells:
                raise ValueError("Fix highlighted cells in Pipes tab")

            self.project_data.update_from_table("pipes", pipes_data)
            self.data_updated.emit(self.project_data.to_json())
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self):
        data = []
        for row in range(self.pipes_table.rowCount()):
            row_data = []
            for col in range(self.pipes_table.columnCount()):
                item = self.pipes_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data