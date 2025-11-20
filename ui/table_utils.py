from PyQt5.QtWidgets import QTableWidgetItem, QComboBox, QCheckBox, QWidget, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QBrush
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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

class CheckBoxWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.checkbox = QCheckBox()
        layout.addWidget(self.checkbox, alignment=Qt.AlignCenter)
        self.setLayout(layout)

def highlight_table_errors(table, errors):
    """
    Common function to highlight errors in table rows.
    
    Args:
        table: QTableWidget to highlight
        errors: List of error messages
    """
    # Clear all highlights first
    table.blockSignals(True)
    for row in range(table.rowCount()):
        for col in range(1, table.columnCount()):  # Skip checkbox column
            item = table.item(row, col)
            if item:
                item.setBackground(QBrush())
                item.setToolTip("")
    
    # Highlight cells with errors
    if errors:
        for error in errors:
            if error.startswith("Row"):
                try:
                    row_str = error.split(":")[0].replace("Row ", "")
                    row_idx = int(row_str) - 1
                    # Highlight the entire row
                    for col in range(1, table.columnCount()):
                        item = table.item(row_idx, col)
                        if item:
                            item.setBackground(QBrush(Qt.yellow))
                            item.setToolTip(error.split(":", 1)[1].strip())
                except (ValueError, IndexError):
                    logging.error(f"Failed to parse error message: {error}")
                    continue
        
        QMessageBox.critical(table.parent(), "Error", "\n".join(errors))
    
    table.blockSignals(False)

def extract_table_data(table, include_widgets=True):
    """
    Common function to extract data from table, skipping the checkbox column.
    
    Args:
        table: QTableWidget to extract data from
        include_widgets: Whether to handle widget cells (like QComboBox)
    
    Returns:
        List of lists containing table data
    """
    data = []
    for row in range(table.rowCount()):
        row_data = []
        # Start from column 1 to skip checkbox column
        for col in range(1, table.columnCount()):
            if include_widgets:
                widget = table.cellWidget(row, col)
                if widget and isinstance(widget, QComboBox):
                    row_data.append(widget.currentText())
                else:
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
            else:
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
        data.append(row_data)
    return data

def add_row(table, table_key, table_configs, parent, id_field_name, row_index=None):
    """Add a row to a table with proper ID and sorting handling, using generic default value logic."""
    logging.debug(f"Starting add_row for {table_key}")
    try:
        config = table_configs.get(table_key)
        if not config:
            logging.error(f"No table config found for key: {table_key}")
            return

        # Save current sort state
        was_sorting = table.isSortingEnabled()
        sort_col = table.horizontalHeader().sortIndicatorSection()
        sort_order = table.horizontalHeader().sortIndicatorOrder()
        
        table.setSortingEnabled(False)
        table.blockSignals(True)

        # Find the ID column index using the provided id_field_name
        id_column = None
        for i in range(table.columnCount()):
            if table.horizontalHeaderItem(i).text() == id_field_name:
                id_column = i
                break

        if id_column is None:
            logging.error(f"Could not find ID column: {id_field_name}")
            return

        # Calculate next available ID
        used_ids = set()
        for row in range(table.rowCount()):
            item = table.item(row, id_column)
            try:
                if item and item.text():
                    used_ids.add(int(item.text()))
            except (ValueError, TypeError):
                continue

        # Find the next available ID
        next_id = 1
        while next_id in used_ids:
            next_id += 1

        # Insert the row at specified index or append
        if row_index is None:
            row_index = table.rowCount()
        table.insertRow(row_index)

        # Add checkbox first (assume first column is always checkbox)
        checkbox_widget = CheckBoxWidget()
        table.setCellWidget(row_index, 0, checkbox_widget)

        # Prepare context for default_generator if available
        context = {"max_id": next_id}
        if hasattr(config, "default_generator"):
            defaults = config.default_generator(row_index, context)
        else:
            # Fallback: just use empty strings
            defaults = [""] * table.columnCount()

        # Set default values for each column (skip checkbox column)
        for col_idx in range(1, table.columnCount()):
            header_text = table.horizontalHeaderItem(col_idx).text()
            col_config = None
            if hasattr(config, "columns"):
                # Find the config for this column (config.columns includes "Select" at index 0)
                try:
                    col_config = config.columns[col_idx]
                except (IndexError, AttributeError):
                    pass

            # Use default from generator if available, else empty string
            default = ""
            if defaults and col_idx < len(defaults):
                default = defaults[col_idx]

            # Set ID column
            if col_idx == id_column:
                id_item = QTableWidgetItem(str(next_id))
                id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row_index, col_idx, id_item)
            # Combo box column
            elif col_config and getattr(col_config, "widget_type", None) == "combo":
                combo = QComboBox()
                combo.addItems(col_config.combo_items)
                combo.setCurrentText(str(default) if default else col_config.combo_items[0])
                # Connect signal to sync data when combo box value changes
                if hasattr(parent, '_sync_data_if_not_initializing'):
                    combo.currentTextChanged.connect(parent._sync_data_if_not_initializing)
                table.setCellWidget(row_index, col_idx, combo)
            # Numeric column (optional: check for numeric type)
            elif col_config and getattr(col_config, "widget_type", None) == "numeric":
                item = NumericTableWidgetItem(str(default))
                table.setItem(row_index, col_idx, item)
            # Generic text column
            else:
                item = QTableWidgetItem(str(default))
                table.setItem(row_index, col_idx, item)

        # Restore table state
        table.blockSignals(False)
        table.setSortingEnabled(was_sorting)
        if was_sorting:
            table.sortByColumn(sort_col, sort_order)

        # Sync data
        parent._sync_data()
        logging.debug(f"Row added successfully at index {row_index}")

    except Exception as e:
        logging.error(f"Error in add_row: {e}", exc_info=True)
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(parent, "Error", f"Failed to add row: {e}")
    finally:
        table.blockSignals(False)
        table.setSortingEnabled(was_sorting)

def remove_row(table, table_key, table_configs, parent):
    """Remove checked rows from the table."""
    logging.debug(f"Starting remove_row for table_key: {table_key}")
    try:
        table_config = table_configs.get(table_key)
        if not table_config:
            return

        # Get all checked rows
        checked_rows = []
        for row in range(table.rowCount()):
            checkbox_widget = table.cellWidget(row, 0)
            if checkbox_widget and isinstance(checkbox_widget, CheckBoxWidget):
                if checkbox_widget.checkbox.isChecked():
                    checked_rows.append(row)

        # Sort in reverse order to avoid index shifting
        checked_rows.sort(reverse=True)

        # Check if we can remove the rows
        if checked_rows and table.rowCount() - len(checked_rows) >= table_config.min_rows:
            for row in checked_rows:
                table.removeRow(row)
            parent._sync_data()
            logging.debug(f"Removed {len(checked_rows)} rows")
        elif not checked_rows:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(parent, "No Selection", "Please select rows to remove by checking their checkboxes.")
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(parent, "Cannot Remove", 
                              f"Cannot remove all selected rows. Table must have at least {table_config.min_rows} row(s).")
    except Exception as e:
        logging.error(f"Error in remove_row: {e}", exc_info=True)
        raise

def renumber_task_orders(table):
    logging.debug("Starting renumber_task_orders")
    try:
        was_sorting = table.isSortingEnabled()
        table.setSortingEnabled(False)
        table.blockSignals(True)
        
        # Find the Task Order column index
        order_column = None
        for i in range(table.columnCount()):
            if table.horizontalHeaderItem(i).text() == "Order":
                order_column = i
                break
        
        if order_column is None:
            logging.error("Could not find Order column")
            return
            
        task_orders = []
        for row in range(table.rowCount()):
            item = table.item(row, order_column)  # Task Order column
            try:
                task_orders.append((row, float(item.text()) if item and item.text() else 0.0))
            except ValueError:
                task_orders.append((row, 0.0))
        task_orders.sort(key=lambda x: x[1])
        for new_order, (row, _) in enumerate(task_orders, 1):
            item = table.item(row, order_column)
            if not item:
                item = NumericTableWidgetItem()
                table.setItem(row, order_column, item)
            item.setText(str(new_order))
            item.setData(Qt.UserRole, float(new_order))
        table.blockSignals(False)
        table.setSortingEnabled(was_sorting)
        logging.debug("renumber_task_orders completed")
    except Exception as e:
        logging.error(f"Error in renumber_task_orders: {e}", exc_info=True)
        raise