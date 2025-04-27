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


def renumber_task_orders(table):
    """Renumber task orders to ensure they are unique and sequential."""
    was_sorting = table.isSortingEnabled()
    table.setSortingEnabled(False)
    table.blockSignals(True)

    # Collect existing task orders
    task_orders = []
    for row in range(table.rowCount()):
        item = table.item(row, 1)  # Task Order column
        try:
            task_orders.append((row, float(item.text()) if item and item.text() else 0.0))
        except ValueError:
            task_orders.append((row, 0.0))

    # Sort by current task order
    task_orders.sort(key=lambda x: x[1])

    # Assign new sequential task orders
    for new_order, (row, _) in enumerate(task_orders, start=1):
        item = NumericTableWidgetItem(str(new_order))
        item.setData(Qt.UserRole, float(new_order))
        table.setItem(row, 1, item)

    table.blockSignals(False)
    table.setSortingEnabled(was_sorting)


def add_row(table, config_key, table_configs, tab):
    config = table_configs.get(config_key, None)
    if not config:
        return
    row_count = table.rowCount()
    was_sorting = table.isSortingEnabled()
    table.setSortingEnabled(False)
    table.blockSignals(True)
    table.insertRow(row_count)

    context = {}
    if config_key == "tasks":
        max_task_id = 0
        max_task_order = 0
        for row in range(row_count):
            item_id = table.item(row, 0)
            item_order = table.item(row, 1)
            if item_id and item_id.text().isdigit():
                max_task_id = max(max_task_id, int(item_id.text()))
            if item_order:
                try:
                    max_task_order = max(max_task_order, float(item_order.text()))
                except ValueError:
                    pass
        context = {"max_task_id": max_task_id, "max_task_order": max_task_order}

    defaults = config.default_generator(row_count, context)
    for col_idx, default in enumerate(defaults):
        col_config = config.columns[col_idx]
        if isinstance(default, dict) and default.get("type") == "combo":
            combo = QComboBox()
            combo.addItems(default["items"])
            combo.setCurrentText(default["default"])
            table.setCellWidget(row_count, col_idx, combo)
        else:
            item = NumericTableWidgetItem(str(default)) if config_key == "tasks" and col_idx in (0,
                                                                                                 1) else QTableWidgetItem(
                str(default))
            if config_key == "tasks" and col_idx == 0:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setData(Qt.UserRole, int(default))
            elif config_key == "tasks" and col_idx == 1:
                item.setData(Qt.UserRole, float(default))
            table.setItem(row_count, col_idx, item)

    if config_key == "tasks":
        renumber_task_orders(table)
    table.blockSignals(False)
    table.setSortingEnabled(was_sorting)
    if config_key == "tasks":
        table.sortByColumn(1, Qt.AscendingOrder)
    tab._sync_data_if_not_initializing()


def remove_row(table, config_key, table_configs, tab):
    config = table_configs.get(config_key, None)
    if not config:
        return
    if table.rowCount() > config.min_rows:
        table.removeRow(table.rowCount() - 1)
        if config_key == "tasks":
            renumber_task_orders(table)
        tab._sync_data_if_not_initializing()


def show_context_menu(pos, table, config_key, tab, table_configs):
    print(f"Showing context menu for {config_key} at position {pos}")
    try:
        menu = QMenu(tab)
        insert_action = QAction("Insert Row Above", tab)
        delete_action = QAction("Delete Row", tab)
        row_index = table.indexAt(pos).row()
        if row_index < 0 or row_index >= table.rowCount():
            row_index = 0
        menu.addAction(insert_action)
        menu.addAction(delete_action)
        insert_action.triggered.connect(lambda: insert_row(table, config_key, table_configs, tab, row_index))
        delete_action.triggered.connect(lambda: delete_row(table, config_key, table_configs, tab, row_index))
        global_pos = table.viewport().mapToGlobal(pos)
        menu.exec_(global_pos)
    except Exception as e:
        print(f"Error in show_context_menu: {e}")
        raise


def insert_row(table, config_key, table_configs, tab, row_index):
    config = table_configs.get(config_key, None)
    if not config:
        return
    was_sorting = table.isSortingEnabled()
    table.setSortingEnabled(False)
    table.blockSignals(True)
    table.insertRow(row_index)

    context = {}
    if config_key == "tasks":
        max_task_id = 0
        max_task_order = 0
        for row in range(table.rowCount()):
            if row != row_index:
                item_id = table.item(row, 0)
                item_order = table.item(row, 1)
                if item_id and item_id.text().isdigit():
                    max_task_id = max(max_task_id, int(item_id.text()))
                if item_order:
                    try:
                        max_task_order = max(max_task_order, float(item_order.text()))
                    except ValueError:
                        pass
        context = {"max_task_id": max_task_id, "max_task_order": max_task_order}

    defaults = config.default_generator(row_index, context)
    for col_idx, default in enumerate(defaults):
        col_config = config.columns[col_idx]
        if isinstance(default, dict) and default.get("type") == "combo":
            combo = QComboBox()
            combo.addItems(default["items"])
            combo.setCurrentText(default["default"])
            table.setCellWidget(row_index, col_idx, combo)
        else:
            item = NumericTableWidgetItem(str(default)) if config_key == "tasks" and col_idx in (0,
                                                                                                 1) else QTableWidgetItem(
                str(default))
            if config_key == "tasks" and col_idx == 0:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setData(Qt.UserRole, int(default))
            elif config_key == "tasks" and col_idx == 1:
                item.setData(Qt.UserRole, float(default))
            table.setItem(row_index, col_idx, item)

    if config_key == "tasks":
        renumber_task_orders(table)
    table.blockSignals(False)
    table.setSortingEnabled(was_sorting)
    if config_key == "tasks":
        table.sortByColumn(1, Qt.AscendingOrder)
    tab._sync_data_if_not_initializing()


def delete_row(table, config_key, table_configs, tab, row_index):
    config = table_configs.get(config_key, None)
    if not config:
        return
    if table.rowCount() > config.min_rows:
        table.removeRow(row_index)
        if config_key == "tasks":
            renumber_task_orders(table)
        tab._sync_data_if_not_initializing()