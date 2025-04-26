from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QComboBox, QAction
from PyQt5.QtCore import Qt

class NumericTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        self_data = self.data(Qt.UserRole)
        other_data = other.data(Qt.UserRole)
        if self_data is not None and other_data is not None:
            try:
                return float(self_data) < float(other_data)
            except (TypeError, ValueError):
                pass
        return super().__lt__(other)

def add_row(table, config_key, table_configs, tab):
    print(f"Adding row to {config_key}, row count: {table.rowCount()}")
    config = table_configs.get(config_key, {})
    row_count = table.rowCount()
    was_sorting = table.isSortingEnabled()
    table.setSortingEnabled(False)
    table.blockSignals(True)
    table.insertRow(row_count)
    if config_key == "tasks":
        max_task_id = 0
        for row in range(row_count):
            item = table.item(row, 0)
            if item and item.text().isdigit():
                max_task_id = max(max_task_id, int(item.text()))
        task_id = max_task_id + 1
        max_task_order = 0
        for row in range(row_count):
            item = table.item(row, 1)
            try:
                max_task_order = max(max_task_order, float(item.text()) if item and item.text() else 0)
            except ValueError:
                pass
        task_order = max_task_order + 1
        print(f"Task ID: {task_id}, Task Order: {task_order}")
        defaults = config.get("defaults", lambda x, y: [])(task_id, task_order)
    else:
        defaults = config.get("defaults", lambda x: [])(row_count)
    print(f"Defaults: {defaults}")
    for col, default in enumerate(defaults):
        if isinstance(default, dict) and default.get("type") == "combo":
            combo = QComboBox()
            combo.addItems(default["items"])
            combo.setCurrentText(default["default"])
            table.setCellWidget(row_count, col, combo)
        else:
            item = NumericTableWidgetItem(str(default)) if config_key == "tasks" and col in (0, 1) else QTableWidgetItem(str(default))
            if config_key == "tasks" and col == 0:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setData(Qt.UserRole, int(default))
            elif config_key == "tasks" and col == 1:
                item.setData(Qt.UserRole, float(default))
            table.setItem(row_count, col, item)
    if config_key == "tasks":
        print("Renumbering task orders")
        renumber_task_orders(table)
    table.blockSignals(False)
    table.setSortingEnabled(was_sorting)
    table.sortByColumn(1, Qt.AscendingOrder) if config_key == "tasks" else None
    print("Syncing data")
    tab._sync_data_if_not_initializing()

# def add_row(table, config_key, table_configs, tab):
#     config = table_configs.get(config_key, {})
#     row_count = table.rowCount()
#     was_sorting = table.isSortingEnabled()
#     table.setSortingEnabled(False)
#     table.blockSignals(True)
#     table.insertRow(row_count)
#     if config_key == "tasks":
#         max_task_id = 0
#         for row in range(row_count):
#             item = table.item(row, 0)
#             if item and item.text().isdigit():
#                 max_task_id = max(max_task_id, int(item.text()))
#         task_id = max_task_id + 1
#         max_task_order = 0
#         for row in range(row_count):
#             item = table.item(row, 1)
#             try:
#                 max_task_order = max(max_task_order, float(item.text()) if item and item.text() else 0)
#             except ValueError:
#                 pass
#         task_order = max_task_order + 1
#         defaults = config.get("defaults", lambda x, y: [])(task_id, task_order)
#     else:
#         defaults = config.get("defaults", lambda x: [])(row_count)
#     for col, default in enumerate(defaults):
#         if isinstance(default, dict) and default.get("type") == "combo":
#             combo = QComboBox()
#             combo.addItems(default["items"])
#             combo.setCurrentText(default["default"])
#             table.setCellWidget(row_count, col, combo)
#         else:
#             item = NumericTableWidgetItem(str(default)) if config_key == "tasks" and col in (0, 1) else QTableWidgetItem(str(default))
#             if config_key == "tasks" and col == 0:
#                 item.setFlags(item.flags() & ~Qt.ItemIsEditable)
#                 item.setData(Qt.UserRole, int(default))
#             elif config_key == "tasks" and col == 1:
#                 item.setData(Qt.UserRole, float(default))
#             table.setItem(row_count, col, item)
#     if config_key == "tasks":
#         renumber_task_orders(table)
#     table.blockSignals(False)
#     table.setSortingEnabled(was_sorting)
#     table.sortByColumn(1, Qt.AscendingOrder) if config_key == "tasks" else None
#     tab._sync_data_if_not_initializing()

def remove_row(table, config_key, table_configs, tab):
    config = table_configs.get(config_key, {})
    min_rows = config.get("min_rows", 1)
    if table.rowCount() > min_rows:
        table.removeRow(table.rowCount() - 1)
        if config_key == "tasks":
            renumber_task_orders(table)
        tab._sync_data_if_not_initializing()

def show_context_menu(pos, table, config_key, tab, table_configs):
    print(f"Showing context menu for {config_key} at position {pos}")
    try:
        print(f"Table: {table}, Tab: {tab}, Configs: {table_configs}")
        menu = QMenu(tab)  # Add parent for safety
        print("Created main QMenu")

        insert_action = QAction("Insert Row Above", tab)  # Use QAction instead of QMenu
        delete_action = QAction("Delete Row", tab)  # Use QAction instead of QMenu
        print("Created QActions")

        row_index = table.indexAt(pos).row()
        print(f"Calculated row_index: {row_index}")
        if row_index < 0 or row_index >= table.rowCount():
            row_index = 0
            print(f"Adjusted row_index to: {row_index}")

        menu.addAction(insert_action)
        menu.addAction(delete_action)
        print("Added actions to menu")

        print("Connecting insert_action signal")
        insert_action.triggered.connect(lambda: insert_row(table, config_key, table_configs, tab, row_index))
        print("Connecting delete_action signal")
        delete_action.triggered.connect(lambda: delete_row(table, config_key, table_configs, tab, row_index))

        global_pos = table.viewport().mapToGlobal(pos)
        print(f"Executing menu at global position {global_pos}")
        menu.exec_(global_pos)
    except Exception as e:
        print(f"Error in show_context_menu: {e}")
        raise

# def show_context_menu(pos, table, config_key, tab, table_configs):
#     menu = QMenu()
#     insert_action = QMenu("Insert Row Above", tab)
#     delete_action = QMenu("Delete Row", tab)
#     row_index = table.indexAt(pos).row()
#     if row_index < 0 or row_index >= table.rowCount():
#         row_index = 0
#     insert_action.triggered.connect(lambda: insert_row(table, config_key, table_configs, tab, row_index))
#     delete_action.triggered.connect(lambda: delete_row(table, config_key, table_configs, tab, row_index))
#     menu.addAction(insert_action)
#     menu.addAction(delete_action)
#     menu.exec_(table.viewport().mapToGlobal(pos))

def insert_row(table, config_key, table_configs, tab, row_index):
    config = table_configs.get(config_key, {})
    was_sorting = table.isSortingEnabled()
    table.setSortingEnabled(False)
    table.blockSignals(True)
    table.insertRow(row_index)
    if config_key == "tasks":
        max_task_id = 0
        for row in range(table.rowCount()):
            if row != row_index:
                item = table.item(row, 0)
                if item and item.text().isdigit():
                    max_task_id = max(max_task_id, int(item.text()))
        task_id = max_task_id + 1
        prev_order = 0
        curr_order = float('inf')
        if row_index > 0:
            prev_item = table.item(row_index - 1, 1)
            prev_order = float(prev_item.text()) if prev_item and prev_item.text() else row_index
        if row_index < table.rowCount() - 1:
            curr_item = table.item(row_index + 1, 1)
            curr_order = float(curr_item.text()) if curr_item and curr_item.text() else row_index + 1
        task_order = (prev_order + curr_order) / 2 if curr_order != float('inf') else prev_order + 1
        defaults = config.get("defaults", lambda x, y: [])(task_id, task_order)
    else:
        defaults = config.get("defaults", lambda x: [])(table.rowCount())
    for col, default in enumerate(defaults):
        if isinstance(default, dict) and default.get("type") == "combo":
            combo = QComboBox()
            combo.addItems(default["items"])
            combo.setCurrentText(default["default"])
            table.setCellWidget(row_index, col, combo)
        else:
            item = NumericTableWidgetItem(str(default)) if config_key == "tasks" and col in (0, 1) else QTableWidgetItem(str(default))
            if config_key == "tasks" and col == 0:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setData(Qt.UserRole, int(default))
            elif config_key == "tasks" and col == 1:
                item.setData(Qt.UserRole, float(default))
            table.setItem(row_index, col, item)
    if config_key == "tasks":
        renumber_task_orders(table)
    table.blockSignals(False)
    table.setSortingEnabled(was_sorting)
    table.sortByColumn(1, Qt.AscendingOrder) if config_key == "tasks" else None
    tab._sync_data_if_not_initializing()

def delete_row(table, config_key, table_configs, tab, row_index):
    config = table_configs.get(config_key, {})
    min_rows = config.get("min_rows", 1)
    if table.rowCount() > min_rows:
        was_sorting = table.isSortingEnabled()
        table.setSortingEnabled(False)
        table.removeRow(row_index)
        if config_key == "tasks":
            renumber_task_orders(table)
        table.setSortingEnabled(was_sorting)
        tab._sync_data_if_not_initializing()

def renumber_task_orders(table):
    tasks = []
    for row in range(table.rowCount()):
        task_id_item = table.item(row, 0)
        task_order_item = table.item(row, 1)
        try:
            task_order = float(task_order_item.text()) if task_order_item and task_order_item.text() else row + 1
        except ValueError:
            task_order = row + 1
        tasks.append((row, task_order))
    tasks.sort(key=lambda x: x[1])
    table.blockSignals(True)
    for i, (row, _) in enumerate(tasks, 1):
        item = NumericTableWidgetItem(str(i))
        item.setData(Qt.UserRole, float(i))
        table.setItem(row, 1, item)
    table.blockSignals(False)