from PyQt5.QtWidgets import (QWidget, QTableWidget, QVBoxLayout, QPushButton, 
                             QHBoxLayout, QHeaderView, QTableWidgetItem, 
                             QMessageBox, QGroupBox, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QBrush, QColor
from typing import List, Dict, Any, Optional
import logging
from ui.table_utils import NumericTableWidgetItem, add_row, remove_row, CheckBoxWidget
from .base_tab import BaseTab
from models.swimlane import Swimlane
from utils.conversion import safe_int

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SwimlanesTab(BaseTab):
    data_updated = pyqtSignal(dict)
    
    # Read-only cell background color (light gray)
    READ_ONLY_BG = QColor(240, 240, 240)

    def __init__(self, project_data, app_config):
        self.table_config = app_config.get_table_config("swimlanes")
        self._selected_row = None  # Track currently selected row
        self._updating_form = False  # Prevent circular updates
        super().__init__(project_data, app_config)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create toolbar with buttons
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        add_btn = QPushButton("Add Swimlane")
        add_btn.setToolTip("Add a new swimlane")
        add_btn.setMinimumWidth(120)
        add_btn.clicked.connect(lambda: add_row(self.swimlanes_table, "swimlanes", self.app_config.tables, self, "ID"))
        
        remove_btn = QPushButton("Remove Swimlane")
        remove_btn.setToolTip("Remove selected swimlane(s)")
        remove_btn.setMinimumWidth(120)
        remove_btn.clicked.connect(lambda: remove_row(self.swimlanes_table, "swimlanes", 
                                                    self.app_config.tables, self))
        
        toolbar.addWidget(add_btn)
        toolbar.addWidget(remove_btn)
        toolbar.addStretch()  # Push buttons to the left
        
        # Create group box for table
        table_group = QGroupBox("Swimlanes")
        table_group_layout = QVBoxLayout()
        table_group_layout.setSpacing(5)
        table_group_layout.setContentsMargins(5, 10, 5, 5)
        
        # Create table with all columns: Select, ID, First Row, Last Row, Name
        headers = [col.name for col in self.table_config.columns]
        self.swimlanes_table = QTableWidget(0, len(headers))
        self.swimlanes_table.setHorizontalHeaderLabels(headers)
        
        # Table styling
        self.swimlanes_table.setAlternatingRowColors(False)
        self.swimlanes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.swimlanes_table.setSelectionMode(QTableWidget.SingleSelection)
        self.swimlanes_table.setShowGrid(True)
        self.swimlanes_table.verticalHeader().setVisible(False)
        
        # Add bottom border to header row
        self.swimlanes_table.setStyleSheet("""
            QHeaderView::section {
                border-bottom: 1px solid #c0c0c0;
                border-top: none;
                border-left: none;
                border-right: none;
            }
        """)
        
        # Column sizing
        header = self.swimlanes_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Select
        self.swimlanes_table.setColumnWidth(0, 50)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # First Row
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Last Row
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Name
        
        # Enable horizontal scroll bar
        self.swimlanes_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.swimlanes_table.setSortingEnabled(True)
        
        # Set table size policy
        self.swimlanes_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        table_group_layout.addLayout(toolbar)
        table_group_layout.addWidget(self.swimlanes_table)
        table_group.setLayout(table_group_layout)
        
        # Add table group with stretch factor so it expands to fill available space
        layout.addWidget(table_group, 1)
        
        # Create detail form group box (empty for now, reserved for future properties)
        detail_group = self._create_detail_form()
        layout.addWidget(detail_group)
        
        self.setLayout(layout)

    def _create_detail_form(self) -> QGroupBox:
        """Create the detail form for editing swimlane properties (empty for now)."""
        group = QGroupBox("Swimlane Properties")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        # Empty for now - reserved for future properties
        group.setLayout(layout)
        return group

    def _connect_signals(self):
        self.swimlanes_table.itemChanged.connect(self._on_item_changed)
    
    def _get_column_index(self, column_name: str) -> Optional[int]:
        """Get the column index for a given column name."""
        for idx, col_config in enumerate(self.table_config.columns):
            if col_config.name == column_name:
                return idx
        return None
    
    def _get_column_name_from_item(self, item) -> Optional[str]:
        """Get the column name (key) from a table item."""
        if item is None:
            return None
        try:
            col_idx = item.column()
            if not isinstance(col_idx, int) or col_idx < 0 or col_idx >= len(self.table_config.columns):
                return None
            return self.table_config.columns[col_idx].name
        except (IndexError, AttributeError):
            return None
    
    def _on_item_changed(self, item):
        """Handle item changes - update UserRole for numeric columns."""
        if item is None:
            return
        
        # CRITICAL: Disconnect signal BEFORE modifying item to prevent infinite loop
        was_connected = False
        try:
            self.swimlanes_table.itemChanged.disconnect(self._on_item_changed)
            was_connected = True
        except:
            pass  # Signal might not be connected
        
        try:
            # Get column name (key) from item
            col_name = self._get_column_name_from_item(item)
            if col_name is None:
                return
            
            # Don't trigger sync for ID column changes (it's read-only)
            if col_name == "ID":
                return
            
            # Update UserRole for numeric columns (ID, First Row, Last Row)
            if col_name in ["ID", "First Row", "Last Row"]:
                try:
                    val_str = item.text().strip()
                    item.setData(Qt.UserRole, int(val_str) if val_str else 0)
                except (ValueError, AttributeError):
                    item.setData(Qt.UserRole, 0)
            
            # Trigger sync
            self._sync_data_if_not_initializing()
        except Exception as e:
            # Catch any unexpected exceptions to prevent crashes
            logging.error(f"Error in _on_item_changed: {e}", exc_info=True)
            # Don't re-raise - just log and continue
        finally:
            # Reconnect signal if it was connected
            if was_connected:
                try:
                    self.swimlanes_table.itemChanged.connect(self._on_item_changed)
                except:
                    pass

    def _load_initial_data_impl(self):
        """Load initial data into the table using Swimlane objects directly."""
        swimlanes = self.project_data.swimlanes
        row_count = len(swimlanes)
        self.swimlanes_table.setRowCount(row_count)
        self._initializing = True

        for row_idx in range(row_count):
            # Add checkbox first (Select column)
            checkbox_widget = CheckBoxWidget()
            self.swimlanes_table.setCellWidget(row_idx, 0, checkbox_widget)

            # Use helper method to populate row from Swimlane object
            swimlane = swimlanes[row_idx]
            self._update_table_row_from_swimlane(row_idx, swimlane)
        
        # Sort by ID by default
        id_col = self._get_column_index("ID")
        if id_col is not None:
            self.swimlanes_table.sortItems(id_col, Qt.AscendingOrder)
        
        self._initializing = False

    def _update_table_row_from_swimlane(self, row_idx: int, swimlane: Swimlane) -> None:
        """Populate a table row from a Swimlane object."""
        # Get column indices
        id_col = self._get_column_index("ID")
        first_row_col = self._get_column_index("First Row")
        last_row_col = self._get_column_index("Last Row")
        name_col = self._get_column_index("Name")
        
        # Update ID column
        if id_col is not None:
            item = self.swimlanes_table.item(row_idx, id_col)
            if item:
                item.setText(str(swimlane.swimlane_id))
                item.setData(Qt.UserRole, swimlane.swimlane_id)
            else:
                item = NumericTableWidgetItem(str(swimlane.swimlane_id))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                item.setBackground(QBrush(self.READ_ONLY_BG))
                item.setData(Qt.UserRole, swimlane.swimlane_id)
                self.swimlanes_table.setItem(row_idx, id_col, item)
        
        # Update First Row column
        if first_row_col is not None:
            item = self.swimlanes_table.item(row_idx, first_row_col)
            if item:
                item.setText(str(swimlane.first_row))
                item.setData(Qt.UserRole, swimlane.first_row)
            else:
                item = NumericTableWidgetItem(str(swimlane.first_row))
                item.setData(Qt.UserRole, swimlane.first_row)
                self.swimlanes_table.setItem(row_idx, first_row_col, item)
        
        # Update Last Row column
        if last_row_col is not None:
            item = self.swimlanes_table.item(row_idx, last_row_col)
            if item:
                item.setText(str(swimlane.last_row))
                item.setData(Qt.UserRole, swimlane.last_row)
            else:
                item = NumericTableWidgetItem(str(swimlane.last_row))
                item.setData(Qt.UserRole, swimlane.last_row)
                self.swimlanes_table.setItem(row_idx, last_row_col, item)
        
        # Update Name column
        if name_col is not None:
            item = self.swimlanes_table.item(row_idx, name_col)
            if item:
                item.setText(swimlane.name if swimlane.name else "")
            else:
                item = QTableWidgetItem(swimlane.name if swimlane.name else "")
                self.swimlanes_table.setItem(row_idx, name_col, item)

    def _swimlane_from_table_row(self, row_idx: int) -> Optional[Swimlane]:
        """Extract a Swimlane object from a table row."""
        try:
            id_col = self._get_column_index("ID")
            first_row_col = self._get_column_index("First Row")
            last_row_col = self._get_column_index("Last Row")
            name_col = self._get_column_index("Name")
            
            if id_col is None or first_row_col is None or last_row_col is None:
                return None
            
            # Extract ID
            id_item = self.swimlanes_table.item(row_idx, id_col)
            if not id_item:
                return None
            swimlane_id = safe_int(id_item.text())
            if swimlane_id <= 0:
                return None
            
            # Extract First Row
            first_row_item = self.swimlanes_table.item(row_idx, first_row_col)
            if not first_row_item or not first_row_item.text().strip():
                return None
            first_row = safe_int(first_row_item.text())
            if first_row <= 0:
                return None
            
            # Extract Last Row
            last_row_item = self.swimlanes_table.item(row_idx, last_row_col)
            if not last_row_item or not last_row_item.text().strip():
                return None
            last_row = safe_int(last_row_item.text())
            if last_row <= 0:
                return None
            
            # Extract Name
            name = ""
            if name_col is not None:
                name_item = self.swimlanes_table.item(row_idx, name_col)
                if name_item:
                    name = name_item.text().strip()
            
            return Swimlane(
                swimlane_id=swimlane_id,
                first_row=first_row,
                last_row=last_row,
                name=name
            )
        except (ValueError, AttributeError, Exception) as e:
            logging.error(f"Error extracting swimlane from table row {row_idx}: {e}")
            return None

    def _validate_swimlane(self, swimlane: Swimlane, existing_swimlanes: List[Swimlane]) -> List[str]:
        """Validate a swimlane and return list of error messages."""
        errors = []
        num_rows = self.project_data.frame_config.num_rows
        
        # Check first_row <= last_row
        if swimlane.first_row > swimlane.last_row:
            errors.append(f"First Row ({swimlane.first_row}) must be <= Last Row ({swimlane.last_row})")
        
        # Check valid range (1-based row numbers)
        if swimlane.first_row < 1 or swimlane.first_row > num_rows:
            errors.append(f"First Row ({swimlane.first_row}) must be between 1 and {num_rows}")
        if swimlane.last_row < 1 or swimlane.last_row > num_rows:
            errors.append(f"Last Row ({swimlane.last_row}) must be between 1 and {num_rows}")
        
        # Check for overlaps with other swimlanes (exclude self)
        for other in existing_swimlanes:
            if other.swimlane_id == swimlane.swimlane_id:
                continue  # Skip self
            
            # Check if ranges overlap: (first_row, last_row) overlaps with (other.first_row, other.last_row)
            # Two ranges overlap if: first_row <= other.last_row AND last_row >= other.first_row
            if (swimlane.first_row <= other.last_row and swimlane.last_row >= other.first_row):
                errors.append(f"Swimlane overlaps with swimlane ID {other.swimlane_id} (rows {other.first_row}-{other.last_row})")
        
        return errors

    def _sync_data_impl(self):
        """Extract data from table and update project_data using Swimlane objects directly."""
        if self._initializing:
            return
        
        try:
            # Extract Swimlane objects from table rows
            swimlanes = []
            for row_idx in range(self.swimlanes_table.rowCount()):
                try:
                    swimlane = self._swimlane_from_table_row(row_idx)
                    if swimlane:
                        swimlanes.append(swimlane)
                except Exception as e:
                    # Log error for this specific row but continue processing other rows
                    logging.error(f"Error extracting swimlane from row {row_idx}: {e}")
                    continue
            
            # Validate all swimlanes for overlaps
            validation_errors = []
            for swimlane in swimlanes:
                errors = self._validate_swimlane(swimlane, swimlanes)
                if errors:
                    validation_errors.extend([f"Swimlane ID {swimlane.swimlane_id}: {err}" for err in errors])
            
            if validation_errors:
                error_msg = "Validation errors:\n" + "\n".join(validation_errors)
                QMessageBox.warning(self, "Validation Error", error_msg)
                # Don't update project_data if validation fails
                return
            
            # Update project data with Swimlane objects directly
            self.project_data.swimlanes = swimlanes
        except Exception as e:
            # Catch any unexpected exceptions during sync
            logging.error(f"Error in _sync_data_impl: {e}", exc_info=True)
            raise  # Re-raise so BaseTab can show error message
