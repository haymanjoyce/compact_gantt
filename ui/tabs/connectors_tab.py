from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QPushButton, QGridLayout, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from ..table_utils import add_row, remove_row, show_context_menu

class ConnectorsTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, app_config):
        super().__init__()
        self.project_data = project_data
        self.app_config = app_config
        self.table_config = app_config.get_table_config("connectors")
        self.setup_ui()
        self._load_initial_data()
        self.connectors_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        self.connectors_table = QTableWidget(2, len(self.table_config.columns))
        self.connectors_table.setHorizontalHeaderLabels([col.name for col in self.table_config.columns])
        self.connectors_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connectors_table.customContextMenuRequested.connect(
            lambda pos: show_context_menu(pos, self.connectors_table, "connectors", self, self.app_config.tables))
        self.connectors_table.setSortingEnabled(True)
        self.connectors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.connectors_table)

        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Connector")
        remove_btn = QPushButton("Remove Connector")
        add_btn.clicked.connect(lambda: add_row(self.connectors_table, "connectors", self.app_config.tables, self))
        remove_btn.clicked.connect(lambda: remove_row(self.connectors_table, "connectors", self.app_config.tables, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_initial_data(self):
        table_data = self.project_data.get_table_data("connectors")
        row_count = max(len(table_data), self.table_config.min_rows)
        self.connectors_table.setRowCount(row_count)
        self._initializing = True

        if table_data:
            for row_idx, row_data in enumerate(table_data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.connectors_table.setItem(row_idx, col_idx, item)
        else:
            for row_idx in range(row_count):
                defaults = self.table_config.default_generator(row_idx, {})
                for col_idx, default in enumerate(defaults):
                    item = QTableWidgetItem(str(default))
                    self.connectors_table.setItem(row_idx, col_idx, item)

        self._initializing = False

    def _sync_data(self):
        connectors_data = self._extract_table_data()
        self.project_data.connectors.clear()
        for row in connectors_data:
            from_task_id = row[0] or "0"
            to_task_id = row[1] or "0"
            try:
                from_task_id = int(from_task_id)
                to_task_id = int(to_task_id)
                self.project_data.add_connector(from_task_id, to_task_id)
            except ValueError:
                continue
        self.data_updated.emit(self.project_data.to_json())

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self):
        data = []
        for row in range(self.connectors_table.rowCount()):
            row_data = []
            for col in range(self.connectors_table.columnCount()):
                item = self.connectors_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data