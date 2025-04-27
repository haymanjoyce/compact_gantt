from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QPushButton, QGridLayout, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from ..table_utils import add_row, remove_row, show_context_menu

class TextBoxesTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, app_config):
        super().__init__()
        self.project_data = project_data
        self.app_config = app_config
        self.table_config = app_config.get_table_config("text_boxes")
        self.setup_ui()
        self._load_initial_data()
        self.text_boxes_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        self.text_boxes_table = QTableWidget(2, len(self.table_config.columns))
        self.text_boxes_table.setHorizontalHeaderLabels([col.name for col in self.table_config.columns])
        self.text_boxes_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_boxes_table.customContextMenuRequested.connect(
            lambda pos: show_context_menu(pos, self.text_boxes_table, "text_boxes", self, self.app_config.tables))
        self.text_boxes_table.setSortingEnabled(True)
        self.text_boxes_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.text_boxes_table)

        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Text Box")
        remove_btn = QPushButton("Remove Text Box")
        add_btn.clicked.connect(lambda: add_row(self.text_boxes_table, "text_boxes", self.app_config.tables, self))
        remove_btn.clicked.connect(lambda: remove_row(self.text_boxes_table, "text_boxes", self.app_config.tables, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_initial_data(self):
        table_data = self.project_data.get_table_data("text_boxes")
        row_count = max(len(table_data), self.table_config.min_rows)
        self.text_boxes_table.setRowCount(row_count)
        self._initializing = True

        if table_data:
            for row_idx, row_data in enumerate(table_data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.text_boxes_table.setItem(row_idx, col_idx, item)
        else:
            for row_idx in range(row_count):
                defaults = self.table_config.default_generator(row_idx, {})
                for col_idx, default in enumerate(defaults):
                    item = QTableWidgetItem(str(default))
                    self.text_boxes_table.setItem(row_idx, col_idx, item)

        self._initializing = False

    def _sync_data(self):
        text_boxes_data = self._extract_table_data()
        self.project_data.text_boxes.clear()
        for row in text_boxes_data:
            text = row[0] or ""
            x_coord = row[1] or "0"
            y_coord = row[2] or "0"
            colour = row[3] or "black"
            try:
                x_coord = float(x_coord)
                y_coord = float(y_coord)
                self.project_data.add_text_box(text, x_coord, y_coord, colour)
            except ValueError:
                continue
        self.data_updated.emit(self.project_data.to_json())

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