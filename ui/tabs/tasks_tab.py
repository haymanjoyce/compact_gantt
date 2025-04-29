from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QPushButton, QGridLayout, QComboBox, QHeaderView, QTableWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush
from ..table_utils import NumericTableWidgetItem, add_row, remove_row, show_context_menu, renumber_task_orders
import logging

class TasksTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, app_config):
        super().__init__()
        self.project_data = project_data
        self.app_config = app_config
        self.table_config = app_config.get_table_config("tasks")
        self.setup_ui()
        self._load_initial_data()
        self.tasks_table.itemChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        layout = QVBoxLayout()
        self.tasks_table = QTableWidget(self.app_config.general.tasks_rows, len(self.table_config.columns))
        self.tasks_table.setHorizontalHeaderLabels([col.name for col in self.table_config.columns])
        self.tasks_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tasks_table.customContextMenuRequested.connect(
            lambda pos: show_context_menu(pos, self.tasks_table, "tasks", self, self.app_config.tables))
        self.tasks_table.setSortingEnabled(True)
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.tasks_table.setColumnWidth(0, 80)  # Task ID
        self.tasks_table.setColumnWidth(1, 80)  # Task Order
        self.tasks_table.setColumnWidth(2, 150)  # Task Name
        self.tasks_table.setColumnWidth(6, 120)  # Label Placement
        self.tasks_table.setColumnWidth(8, 100)  # Label Alignment
        self.tasks_table.setColumnWidth(9, 80)  # Horiz Offset
        self.tasks_table.setColumnWidth(10, 80)  # Vert Offset
        layout.addWidget(self.tasks_table)

        btn_layout = QGridLayout()
        add_btn = QPushButton("Add Task")
        remove_btn = QPushButton("Remove Task")
        add_btn.clicked.connect(lambda: add_row(self.tasks_table, "tasks", self.app_config.tables, self))
        remove_btn.clicked.connect(lambda: remove_row(self.tasks_table, "tasks", self.app_config.tables, self))
        btn_layout.addWidget(add_btn, 0, 0)
        btn_layout.addWidget(remove_btn, 0, 1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_initial_data(self):
        table_data = self.project_data.get_table_data("tasks")
        row_count = max(len(table_data), self.table_config.min_rows)
        self.tasks_table.setRowCount(row_count)
        self._initializing = True

        if table_data:
            for row_idx, row_data in enumerate(table_data):
                for col_idx, value in enumerate(row_data):
                    col_config = self.table_config.columns[col_idx]
                    if col_config.widget_type == "combo":
                        combo = QComboBox()
                        combo.addItems(col_config.combo_items)
                        combo.setCurrentText(str(value) or col_config.combo_items[0])
                        self.tasks_table.setCellWidget(row_idx, col_idx, combo)
                    else:
                        item = NumericTableWidgetItem(str(value)) if col_idx in (0, 1) else QTableWidgetItem(str(value))
                        if col_idx == 0:  # Task ID read-only
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                            item.setData(Qt.UserRole, int(value) if str(value).isdigit() else 0)
                        elif col_idx == 1:  # Task Order numeric
                            item.setData(Qt.UserRole, float(value) if value else 0.0)
                        self.tasks_table.setItem(row_idx, col_idx, item)
        else:
            max_task_id = 0
            max_task_order = 0
            for row_idx in range(row_count):
                defaults = self.table_config.default_generator(row_idx, {
                    "max_task_id": max_task_id,
                    "max_task_order": max_task_order
                })
                max_task_id += 1
                max_task_order += 1
                for col_idx, default in enumerate(defaults):
                    col_config = self.table_config.columns[col_idx]
                    if isinstance(default, dict) and default.get("type") == "combo":
                        combo = QComboBox()
                        combo.addItems(default["items"])
                        combo.setCurrentText(default["default"])
                        self.tasks_table.setCellWidget(row_idx, col_idx, combo)
                    else:
                        item = NumericTableWidgetItem(str(default)) if col_idx in (0, 1) else QTableWidgetItem(str(default))
                        if col_idx == 0:
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                            item.setData(Qt.UserRole, int(default) if str(default).isdigit() else 0)
                        elif col_idx == 1:
                            item.setData(Qt.UserRole, float(default) if default else 0.0)
                        self.tasks_table.setItem(row_idx, col_idx, item)

        renumber_task_orders(self.tasks_table)
        self.tasks_table.sortByColumn(1, Qt.AscendingOrder)
        self._initializing = False

    def _sync_data(self):
        tasks_data = self._extract_table_data()
        invalid_cells = set()
        task_order_counts = {}
        for row_idx, row in enumerate(tasks_data):
            try:
                task_order = float(row[1] or 0)
                task_order_counts[task_order] = task_order_counts.get(task_order, 0) + 1
                if task_order <= 0:
                    invalid_cells.add((row_idx, 1, "non-positive"))
            except ValueError:
                invalid_cells.add((row_idx, 1, "invalid"))

        non_unique_orders = {k for k, v in task_order_counts.items() if v > 1}
        self.tasks_table.blockSignals(True)
        for row_idx in range(self.tasks_table.rowCount()):
            item = self.tasks_table.item(row_idx, 1)
            tooltip = ""
            task_id = self.tasks_table.item(row_idx, 0).text() if self.tasks_table.item(row_idx, 0) else "Unknown"
            if item and item.text():
                try:
                    task_order = float(item.text())
                    if task_order in non_unique_orders:
                        item.setBackground(QBrush(Qt.yellow))
                        tooltip = f"Task {task_id}: Task Order must be unique"
                    elif task_order <= 0:
                        item.setBackground(QBrush(Qt.yellow))
                        tooltip = f"Task {task_id}: Task Order must be positive"
                    else:
                        item.setBackground(QBrush())
                except ValueError:
                    item.setBackground(QBrush(Qt.yellow))
                    tooltip = f"Task {task_id}: Task Order must be a number"
            else:
                item = NumericTableWidgetItem("0")
                item.setData(Qt.UserRole, 0.0)
                item.setBackground(QBrush(Qt.yellow))
                tooltip = f"Task {task_id}: Task Order required"
                self.tasks_table.setItem(row_idx, 1, item)
            item.setToolTip(tooltip)
        self.tasks_table.blockSignals(False)

        self.project_data.tasks.clear()
        for row in tasks_data:
            try:
                task_id = int(row[0] or 0)
                task_order = float(row[1] or 0)
                task_name = row[2] or "Unnamed"
                start_date = row[3] or ""
                finish_date = row[4] or ""
                row_number = int(row[5] or 1)
                label_placement = row[6] or "Inside"
                label_hide = row[7] or "No"
                label_alignment = row[8] or "Left"
                label_horizontal_offset = float(row[9] or 1.0)
                label_vertical_offset = float(row[10] or 0.5)
                label_text_colour = row[11] or "black"
                self.project_data.add_task(
                    task_id, task_name, start_date, finish_date, row_number,
                    label_placement=label_placement, label_hide=label_hide,
                    label_alignment=label_alignment, label_horizontal_offset=label_horizontal_offset,
                    label_vertical_offset=label_vertical_offset, label_text_colour=label_text_colour,
                    task_order=task_order
                )
            except (ValueError, TypeError):
                continue

        self.data_updated.emit(self.project_data.to_json())

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()

    def _extract_table_data(self):
        data = []
        for row in range(self.tasks_table.rowCount()):
            row_data = []
            for col in range(self.tasks_table.columnCount()):
                widget = self.tasks_table.cellWidget(row, col)
                if widget and isinstance(widget, QComboBox):
                    row_data.append(widget.currentText())
                else:
                    item = self.tasks_table.item(row, col)
                    row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

def add_row(table, table_key, table_configs, parent, context=None):
    print(f"add_row called for {table_key}")
    logging.debug(f"Starting add_row for table_key: {table_key}, context: {context}")
    try:
        was_sorting = table.isSortingEnabled()
        sort_col = table.horizontalHeader().sortIndicatorSection()
        sort_order = table.horizontalHeader().sortIndicatorOrder()

        table.setSortingEnabled(False)
        table.blockSignals(True)

        table_config = table_configs.get(table_key)
        print("table_config:", table_config)
        if not table_config:
            logging.error(f"No table config found for key: {table_key}")
            table.blockSignals(False)
            table.setSortingEnabled(was_sorting)
            return
        row_idx = table.rowCount()
        table.insertRow(row_idx)

        context = context or {}
        if table_key == "tasks":
            max_task_id = 0
            max_task_order = 0
            for row in range(table.rowCount()):
                item_id = table.item(row, 0)
                item_order = table.item(row, 1)
                if item_id and item_id.text().isdigit():
                    max_task_id = max(max_task_id, int(item_id.text()))
                if item_order:
                    try:
                        max_task_order = max(max_task_order, float(item_order.text()))
                    except ValueError:
                        pass
            context["max_task_id"] = max_task_id
            context["max_task_order"] = max_task_order

        defaults = table_config.default_generator(row_idx, context)
        print("defaults:", defaults)
        for col_idx, default in enumerate(defaults):
            item = QTableWidgetItem(str(default))
            if table_key == "time_frames" and col_idx == 0:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row_idx, col_idx, item)
        print("add_row: row added successfully")

        table.blockSignals(False)
        table.setSortingEnabled(was_sorting)
        if was_sorting:
            table.sortByColumn(sort_col, sort_order)
    except Exception as e:
        print("add_row exception:", e)
        logging.error(f"Error in add_row: {e}", exc_info=True)
        table.blockSignals(False)
        table.setSortingEnabled(True)
        raise