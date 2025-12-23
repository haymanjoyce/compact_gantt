from PyQt5.QtWidgets import (QWidget, QTableWidget, QVBoxLayout, QPushButton, 
                           QHBoxLayout, QHeaderView, QTableWidgetItem, 
                           QMessageBox, QGroupBox, QSizePolicy, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any
import logging
from ui.table_utils import NumericTableWidgetItem, add_row, remove_row, CheckBoxWidget, extract_table_data
from .base_tab import BaseTab

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LinksTab(BaseTab):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data, app_config):
        self.table_config = app_config.get_table_config("links")
        super().__init__(project_data, app_config)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create toolbar with buttons
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        add_btn = QPushButton("Add Link")
        add_btn.setToolTip("Add a new link")
        add_btn.setMinimumWidth(120)
        add_btn.clicked.connect(lambda: add_row(self.links_table, "links", self.app_config.tables, self, "From Task ID"))
        
        remove_btn = QPushButton("Remove Link")
        remove_btn.setToolTip("Remove selected link(s)")
        remove_btn.setMinimumWidth(120)
        remove_btn.clicked.connect(lambda: remove_row(self.links_table, "links", 
                                                    self.app_config.tables, self))
        
        toolbar.addWidget(add_btn)
        toolbar.addWidget(remove_btn)
        toolbar.addStretch()  # Push buttons to the left
        
        # Create group box for table
        table_group = QGroupBox("Links")
        table_group_layout = QVBoxLayout()
        table_group_layout.setSpacing(5)
        table_group_layout.setContentsMargins(5, 10, 5, 5)
        
        # Create table with all columns: Select, From Task ID, To Task ID
        headers = [col.name for col in self.table_config.columns]
        self.links_table = QTableWidget(0, len(headers))
        self.links_table.setHorizontalHeaderLabels(headers)
        
        # Table styling
        self.links_table.setAlternatingRowColors(True)
        self.links_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.links_table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.links_table.setShowGrid(True)
        self.links_table.verticalHeader().setVisible(False)
        
        # Column sizing
        header = self.links_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Select
        self.links_table.setColumnWidth(0, 50)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # From Task ID
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # To Task ID
        
        # Enable horizontal scroll bar
        self.links_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.links_table.setSortingEnabled(True)
        
        # Set table size policy
        self.links_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        table_group_layout.addLayout(toolbar)
        table_group_layout.addWidget(self.links_table)
        table_group.setLayout(table_group_layout)
        
        layout.addWidget(table_group)
        self.setLayout(layout)

    def _connect_signals(self):
        self.links_table.itemChanged.connect(self._on_item_changed)
    
    def _on_item_changed(self, item):
        """Handle item changes - update UserRole for numeric columns to maintain proper sorting."""
        if item is None:
            return
        
        col = item.column()
        col_config = self.table_config.columns[col] if col < len(self.table_config.columns) else None
        
        # Update UserRole for numeric columns (From Task ID, To Task ID)
        if col_config and col_config.name in ["From Task ID", "To Task ID"]:
            try:
                val_str = item.text().strip()
                item.setData(Qt.UserRole, int(val_str) if val_str else 0)
            except (ValueError, AttributeError):
                item.setData(Qt.UserRole, 0)
        
        # Trigger sync
        self._sync_data_if_not_initializing()

    def _load_initial_data_impl(self):
        table_data = self.project_data.get_table_data("links")
        row_count = max(len(table_data), self.table_config.min_rows)
        self.links_table.setRowCount(row_count)
        self._initializing = True

        headers = [col.name for col in self.table_config.columns]
        
        for row_idx in range(row_count):
            # Add checkbox first (Select column)
            checkbox_widget = CheckBoxWidget()
            self.links_table.setCellWidget(row_idx, 0, checkbox_widget)

            if row_idx < len(table_data):
                row_data = table_data[row_idx]
                # row_data structure: [From Task ID, To Task ID]
                for col_idx in range(1, len(headers)):  # Skip Select column (index 0)
                    col_config = self.table_config.columns[col_idx]
                    col_name = col_config.name
                    
                    # Get value from row_data (index 0 = From Task ID, index 1 = To Task ID)
                    value_idx = col_idx - 1  # Adjust for missing Select column in row_data
                    value = row_data[value_idx] if value_idx < len(row_data) else ""
                    
                    # Create appropriate widget/item based on column type
                    if col_config.widget_type == "combo":
                        combo = QComboBox()
                        combo.addItems(col_config.options if hasattr(col_config, 'options') else [])
                        if value:
                            idx = combo.findText(str(value))
                            if idx >= 0:
                                combo.setCurrentIndex(idx)
                        combo.currentTextChanged.connect(self._sync_data_if_not_initializing)
                        self.links_table.setCellWidget(row_idx, col_idx, combo)
                    else:
                        # Numeric columns (From Task ID, To Task ID)
                        if col_name in ["From Task ID", "To Task ID"]:
                            item = NumericTableWidgetItem(str(value))
                            try:
                                item.setData(Qt.UserRole, int(str(value).strip()) if str(value).strip() else 0)
                            except (ValueError, AttributeError):
                                item.setData(Qt.UserRole, 0)
                        else:
                            item = QTableWidgetItem(str(value))
                        self.links_table.setItem(row_idx, col_idx, item)
            else:
                # New row - leave blank (don't use defaults)
                for col_idx in range(1, len(headers)):  # Skip Select column
                    col_config = self.table_config.columns[col_idx]
                    col_name = col_config.name
                    
                    if col_config.widget_type == "combo":
                        combo = QComboBox()
                        combo.addItems(col_config.options if hasattr(col_config, 'options') else [])
                        combo.currentTextChanged.connect(self._sync_data_if_not_initializing)
                        self.links_table.setCellWidget(row_idx, col_idx, combo)
                    else:
                        # Numeric columns - create blank editable items
                        if col_name in ["From Task ID", "To Task ID"]:
                            item = NumericTableWidgetItem("")
                            item.setData(Qt.UserRole, 0)
                        else:
                            item = QTableWidgetItem("")
                        self.links_table.setItem(row_idx, col_idx, item)
        
        # Sort by From Task ID by default
        self.links_table.sortItems(1, Qt.AscendingOrder)  # Column 1 = From Task ID
        
        self._initializing = False

    def _sync_data_impl(self):
        """Extract data from table and update project_data."""
        # Avoid emitting during initialization to prevent recursive updates
        if self._initializing:
            return
        
        # Extract table data (excludes checkbox column)
        data = extract_table_data(self.links_table)
        
        # data structure: [[From Task ID, To Task ID], ...]
        errors = self.project_data.update_from_table("links", data)
        
        if errors:
            # Highlight errors in table
            highlight_table_errors(self.links_table, errors, self.table_config)
        
        # Don't emit data_updated here - chart will update when user clicks "Update Chart" button
        # This matches the behavior of the tasks tab

