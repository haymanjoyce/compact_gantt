from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QBrush
from datetime import datetime, timedelta
from ..table_utils import add_row, remove_row, show_context_menu

class TimeFramesTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, app_config):
        super().__init__()
        self.project_data = project_data
        self.app_config = app_config
        self.table_config = app_config.get_table_config("time_frames")
        self.setup_ui()
        self._load_initial_data()
        self.time_frames_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        self.time_frames_table = QTableWidget(2, len(self.table_config.columns))
        self.time_frames_table.setHorizontalHeaderLabels([col.name for col in self.table_config.columns])
        self.time_frames_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.time_frames_table.customContextMenuRequested.connect(
            lambda pos: show_context_menu(pos, self.time_frames_table, "time_frames", self, self.app_config.tables))
        self.time_frames_table.setSortingEnabled(True)
        self.time_frames_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.time_frames_table.resizeColumnsToContents()
        layout.addWidget(self.time_frames_table)

        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Time Frame")
        remove_btn = QPushButton("Remove Time Frame")
        add_btn.clicked.connect(lambda: add_row(self.time_frames_table, "time_frames", self.app_config.tables, self))
        remove_btn.clicked.connect(lambda: remove_row(self.time_frames_table, "time_frames", self.app_config.tables, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_initial_data(self):
        table_data = self.project_data.get_table_data("time_frames")
        row_count = max(len(table_data), self.table_config.min_rows)
        self.time_frames_table.setRowCount(row_count)
        self._initializing = True

        if table_data:
            for row_idx, row_data in enumerate(table_data):
                for col_idx, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    self.time_frames_table.setItem(row_idx, col_idx, item)
        else:
            for row_idx in range(row_count):
                defaults = self.table_config.default_generator(row_idx, {})
                for col_idx, default in enumerate(defaults):
                    item = QTableWidgetItem(str(default))
                    self.time_frames_table.setItem(row_idx, col_idx, item)

        self._initializing = False

    def _sync_data(self):
        try:
            tf_data = self._extract_table_data()
            if not tf_data:
                raise ValueError("At least one time frame is required")
            invalid_cells = set()
            chart_start = datetime.strptime(self.project_data.frame_config.chart_start_date, "%Y-%m-%d")
            prev_end = chart_start

            for row_idx, row in enumerate(tf_data):
                end = row[0] or "2025-01-01"
                try:
                    end_dt = datetime.strptime(end, "%Y-%m-%d")
                except ValueError:
                    invalid_cells.add((row_idx, 0, "invalid format"))
                    continue
                try:
                    width = float(row[1] or 0) / 100
                    if width <= 0:
                        invalid_cells.add((row_idx, 1, "non-positive"))
                except ValueError:
                    invalid_cells.add((row_idx, 1, "invalid"))
                    continue
                if end_dt < prev_end:
                    invalid_cells.add((row_idx, 0, "before-previous"))
                prev_end = end_dt + timedelta(days=1)

            self.time_frames_table.blockSignals(True)
            for row_idx in range(self.time_frames_table.rowCount()):
                for col in (0, 1):
                    item = self.time_frames_table.item(row_idx, col)
                    tooltip = ""
                    if item:
                        if any((row_idx, col, reason) in invalid_cells for reason in ["invalid format"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Time Frame {row_idx + 1}: Finish Date must be yyyy-MM-dd"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["before-previous"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Time Frame {row_idx + 1}: Finish Date must be after previous"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["invalid"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Time Frame {row_idx + 1}: Width must be a number"
                        elif any((row_idx, col, reason) in invalid_cells for reason in ["non-positive"]):
                            item.setBackground(QBrush(Qt.yellow))
                            tooltip = f"Time Frame {row_idx + 1}: Width must be positive"
                        else:
                            item.setBackground(QBrush())
                    else:
                        item = QTableWidgetItem("")
                        item.setBackground(QBrush(Qt.yellow))
                        tooltip = f"Time Frame {row_idx + 1}: {'Finish Date' if col == 0 else 'Width'} required"
                        self.time_frames_table.setItem(row_idx, col, item)
                    item.setToolTip(tooltip)
            self.time_frames_table.blockSignals(False)

            if invalid_cells:
                raise ValueError("Fix highlighted cells in Time Frames tab")

            self.project_data.time_frames.clear()
            for row in tf_data:
                end = row[0] or "2025-01-01"
                width = float(row[1] or 100) / 100
                self.project_data.add_time_frame(end, width)

            self.data_updated.emit(self.project_data.to_json())
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self):
        data = []
        for row in range(self.time_frames_table.rowCount()):
            row_data = []
            for col in range(self.time_frames_table.columnCount()):
                item = self.time_frames_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data