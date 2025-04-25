from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from ..table_utils import add_row, remove_row, show_context_menu

class TextBoxesTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, table_configs):
        super().__init__()
        self.project_data = project_data
        self.table_configs = table_configs
        self.setup_ui()
        self._load_initial_data()
        self.text_boxes_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        self.text_boxes_table = QTableWidget(2, len(self.table_configs["text_boxes"]["columns"]))
        self.text_boxes_table.setHorizontalHeaderLabels(self.table_configs["text_boxes"]["columns"])
        self.text_boxes_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_boxes_table.customContextMenuRequested.connect(
            lambda pos: show_context_menu(pos, self.text_boxes_table, "text_boxes", self, self.table_configs))
        self.text_boxes_table.setSortingEnabled(True)
        self.text_boxes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.text_boxes_table.resizeColumnsToContents()
        layout.addWidget(self.text_boxes_table)

        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Text Box")
        remove_btn = QPushButton("Remove Text Box")
        add_btn.clicked.connect(lambda: add_row(self.text_boxes_table, "text_boxes", self.table_configs, self))
        remove_btn.clicked.connect(lambda: remove_row(self.text_boxes_table, "text_boxes", self.table_configs, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_initial_data(self):
        config = self.table_configs["text_boxes"]
        table_data = self.project_data.get_table_data("text_boxes")
        row_count = max(len(table_data), config["min_rows"])
        self.text_boxes_table.setRowCount(row_count)
        self._initializing = True

        if table_data:
            for row_idx, row_data in enumerate(table_data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.text_boxes_table.setItem(row_idx, col_idx, item)
        else:
            for row_idx in range(row_count):
                defaults = config["defaults"](row_idx)
                for col_idx, default in enumerate(defaults):
                    item = QTableWidgetItem(str(default))
                    self.text_boxes_table.setItem(row_idx, col_idx, item)

        self._initializing = False

    def _sync_data(self):
        try:
            text_boxes_data = self._extract_table_data()
            invalid_cells = set()
            for row_idx, row in enumerate(text_boxes_data):
                x_coord, y_coord = row[1], row[2]
                try:
                    float(x_coord) if x_coord else 0
                except ValueError:
                    invalid_cells.add((row_idx, 1, "invalid"))
                try:
                    float(y_coord) if y_coord else 0
                except ValueError:
                    invalid_cells.add((row_idx, 2, "invalid"))

            self.text_boxes_table.blockSignals(True)
            for row_idx in range(self.text_boxes_table.rowCount()):
                for col in (1, 2):
                    item = self.text_boxes_table.item(row_idx, col)
                    tooltip = ""
                    if item and item.text():
                        if any((row_idx, col, reason) in invalid_cells for reason in ["invalid"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Text Box {row_idx + 1}: {'X' if col == 1 else 'Y'} Coordinate must be a number"
                        else:
                            item.setBackground(QBrush())
                    else:
                        item = QTableWidgetItem("")
                        item.setBackground(QBrush(Qt.yellow))
                        tooltip = f"Text Box {row_idx + 1}: {'X' if col == 1 else 'Y'} Coordinate required"
                        self.text_boxes_table.setItem(row_idx, col, item)
                    item.setToolTip(tooltip)
            self.text_boxes_table.blockSignals(False)

            if invalid_cells:
                raise ValueError("Fix highlighted cells in Text Boxes tab")

            self.project_data.update_from_table("text_boxes", text_boxes_data)
            self.data_updated.emit(self.project_data.to_json())
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self):
        data = []
        for row in range(self.text_boxes_table.rowCount()):
            row_data = []
            for col in range(self.text_boxes_table.columnCount()):
                item = self.text_boxes_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data