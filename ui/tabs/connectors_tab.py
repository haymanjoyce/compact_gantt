from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from ..table_utils import add_row, remove_row, show_context_menu

class ConnectorsTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, table_configs):
        super().__init__()
        self.project_data = project_data
        self.table_configs = table_configs
        self.setup_ui()
        self._load_initial_data()
        self.connectors_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        self.connectors_table = QTableWidget(2, len(self.table_configs["connectors"]["columns"]))
        self.connectors_table.setHorizontalHeaderLabels(self.table_configs["connectors"]["columns"])
        self.connectors_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.connectors_table.customContextMenuRequested.connect(
            lambda pos: show_context_menu(pos, self.connectors_table, "connectors", self, self.table_configs))
        self.connectors_table.setSortingEnabled(True)
        self.connectors_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.connectors_table.resizeColumnsToContents()
        layout.addWidget(self.connectors_table)

        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Connector")
        remove_btn = QPushButton("Remove Connector")
        add_btn.clicked.connect(lambda: add_row(self.connectors_table, "connectors", self.table_configs, self))
        remove_btn.clicked.connect(lambda: remove_row(self.connectors_table, "connectors", self.table_configs, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_initial_data(self):
        config = self.table_configs["connectors"]
        table_data = self.project_data.get_table_data("connectors")
        row_count = max(len(table_data), config["min_rows"])
        self.connectors_table.setRowCount(row_count)
        self._initializing = True

        if table_data:
            for row_idx, row_data in enumerate(table_data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.connectors_table.setItem(row_idx, col_idx, item)
        else:
            for row_idx in range(row_count):
                defaults = config["defaults"](row_idx)
                for col_idx, default in enumerate(defaults):
                    item = QTableWidgetItem(str(default))
                    self.connectors_table.setItem(row_idx, col_idx, item)

        self._initializing = False

    def _sync_data(self):
        try:
            connectors_data = self._extract_table_data()
            invalid_cells = set()
            task_ids = {task.task_id for task in self.project_data.tasks}
            connector_pairs = set()

            for row_idx, row in enumerate(connectors_data):
                from_id, to_id = row[0], row[1]
                try:
                    from_id_val = int(from_id) if from_id else 0
                    if from_id_val <= 0:
                        invalid_cells.add((row_idx, 0, "non-positive"))
                    elif from_id_val not in task_ids:
                        invalid_cells.add((row_idx, 0, "invalid-task"))
                    elif from_id_val == int(to_id or 0):
                        invalid_cells.add((row_idx, 0, "self-reference"))
                except ValueError:
                    invalid_cells.add((row_idx, 0, "invalid"))

                try:
                    to_id_val = int(to_id) if to_id else 0
                    if to_id_val <= 0:
                        invalid_cells.add((row_idx, 1, "non-positive"))
                    elif to_id_val not in task_ids:
                        invalid_cells.add((row_idx, 1, "invalid-task"))
                    elif to_id_val == int(from_id or 0):
                        invalid_cells.add((row_idx, 1, "self-reference"))
                except ValueError:
                    invalid_cells.add((row_idx, 1, "invalid"))

                if from_id and to_id and (from_id, to_id) in connector_pairs:
                    invalid_cells.add((row_idx, 0, "duplicate"))
                    invalid_cells.add((row_idx, 1, "duplicate"))
                else:
                    connector_pairs.add((from_id, to_id))

            self.connectors_table.blockSignals(True)
            for row_idx in range(self.connectors_table.rowCount()):
                for col in (0, 1):
                    item = self.connectors_table.item(row_idx, col)
                    tooltip = ""
                    if item:
                        if any((row_idx, col, reason) in invalid_cells for reason in ["non-positive"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Connector {row_idx + 1}: {'From' if col == 0 else 'To'} Task ID must be positive"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["invalid"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Connector {row_idx + 1}: {'From' if col == 0 else 'To'} Task ID must be an integer"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["invalid-task"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Connector {row_idx + 1}: {'From' if col == 0 else 'To'} Task ID does not exist"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["self-reference"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Connector {row_idx + 1}: From and To Task IDs cannot be the same"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["duplicate"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Connector {row_idx + 1}: Duplicate connector"
                        else:
                            item.setBackground(QBrush())
                    else:
                        item = QTableWidgetItem("")
                        item.setBackground(QBrush(Qt.yellow))
                        tooltip = f"Connector {row_idx + 1}: {'From' if col == 0 else 'To'} Task ID required"
                        self.connectors_table.setItem(row_idx, col, item)
                    item.setToolTip(tooltip)
            self.connectors_table.blockSignals(False)

            if invalid_cells:
                raise ValueError("Fix highlighted cells in Connectors tab")

            self.project_data.update_from_table("connectors", connectors_data)
            self.data_updated.emit(self.project_data.to_json())
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

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