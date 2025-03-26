"""
Purpose: Defines DataEntryWindow, handles user input via tabs and file management.
Why: Manages multiple data tables and metadata for a complex Gantt chart, using JSON for persistence.
"""

from PyQt5.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog, QTabWidget, QMenuBar, QAction, QApplication, QToolBar
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDate
from svg_display import SVGDisplayWindow
from svg_generator import generate_svg
import json
from datetime import datetime

class DataEntryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gantt Chart Data Entry")
        self.setGeometry(100, 100, 800, 500)

        # Menu bar setup
        self.menu_bar = self.menuBar()

        # File menu
        self.file_menu = self.menu_bar.addMenu("File")
        self.save_action = QAction("Save Project", self)
        self.save_action.triggered.connect(self.save_to_json)
        self.file_menu.addAction(self.save_action)
        self.load_action = QAction("Load Project", self)
        self.load_action.triggered.connect(self.load_from_json)
        self.file_menu.addAction(self.load_action)

        # Tools menu
        self.tools_menu = self.menu_bar.addMenu("Tools")
        self.add_row_action = QAction("Add Row to Current Tab", self)
        self.add_row_action.triggered.connect(self.add_row)
        self.tools_menu.addAction(self.add_row_action)
        self.remove_row_action = QAction("Remove Last Row from Current Tab", self)
        self.remove_row_action.triggered.connect(self.remove_row)
        self.tools_menu.addAction(self.remove_row_action)
        self.generate_action = QAction("Generate Gantt Chart", self)
        self.generate_action.triggered.connect(self.generate_and_show_svg)
        self.tools_menu.addAction(self.generate_action)

        # Toolbar setup
        self.toolbar = QToolBar("Tools")
        self.addToolBar(self.toolbar)  # Adds it below the menu bar by default
        style = QApplication.style()  # Get app’s style for standard icons

        self.add_row_tool = QAction(QIcon(style.standardIcon(style.SP_FileIcon)), "Add Row", self)
        self.add_row_tool.triggered.connect(self.add_row)
        self.toolbar.addAction(self.add_row_tool)

        self.remove_row_tool = QAction(QIcon(style.standardIcon(style.SP_TrashIcon)), "Remove Row", self)
        self.remove_row_tool.triggered.connect(self.remove_row)
        self.toolbar.addAction(self.remove_row_tool)

        self.generate_tool = QAction(QIcon(style.standardIcon(style.SP_ArrowRight)), "Generate Gantt Chart", self)
        self.generate_tool.triggered.connect(self.generate_and_show_svg)
        self.toolbar.addAction(self.generate_tool)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Tab widget for multiple tables
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Tasks table
        self.tasks_table = QTableWidget(5, 3)
        self.tasks_table.setHorizontalHeaderLabels(["Task Name", "Start Date", "Duration (days)"])
        self.tabs.addTab(self.tasks_table, "Tasks")

        # Pipes table (vertical bars)
        self.pipes_table = QTableWidget(3, 2)
        self.pipes_table.setHorizontalHeaderLabels(["Pipe Name", "Date"])
        self.tabs.addTab(self.pipes_table, "Pipes")

        # Curtains table (shaded areas)
        self.curtains_table = QTableWidget(3, 4)
        self.curtains_table.setHorizontalHeaderLabels(["Curtain Name", "Start Pipe", "End Pipe", "Color"])
        self.tabs.addTab(self.curtains_table, "Curtains")

        # Initialize svg_window
        self.svg_window = None

    def add_row(self):
        """Add a row to the current tab’s table."""
        current_table = self.tabs.currentWidget()
        current_rows = current_table.rowCount()
        current_table.insertRow(current_rows)
        if current_table == self.tasks_table:
            current_table.setItem(current_rows, 0, QTableWidgetItem(f"Task {current_rows + 1}"))
            current_table.setItem(current_rows, 1, QTableWidgetItem(QDate.currentDate().toString("yyyy-MM-dd")))
            current_table.setItem(current_rows, 2, QTableWidgetItem("1"))
        elif current_table == self.pipes_table:
            current_table.setItem(current_rows, 0, QTableWidgetItem(f"Pipe {current_rows + 1}"))
            current_table.setItem(current_rows, 1, QTableWidgetItem(QDate.currentDate().toString("yyyy-MM-dd")))
        elif current_table == self.curtains_table:
            current_table.setItem(current_rows, 0, QTableWidgetItem(f"Curtain {current_rows + 1}"))
            current_table.setItem(current_rows, 1, QTableWidgetItem("Pipe 1"))
            current_table.setItem(current_rows, 2, QTableWidgetItem("Pipe 2"))
            current_table.setItem(current_rows, 3, QTableWidgetItem("rgba(255, 0, 0, 0.3)"))

    def remove_row(self):
        """Remove the last row from the current tab’s table."""
        current_table = self.tabs.currentWidget()
        if current_table.rowCount() > 1:
            current_table.removeRow(current_table.rowCount() - 1)

    def _get_table_data(self, table):
        """Extract and validate data from a given table."""
        data = []
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            if table == self.tasks_table:
                try:
                    if row_data[1]:  # Start Date
                        datetime.strptime(row_data[1], "%Y-%m-%d")
                    if row_data[2]:  # Duration
                        float(row_data[2])
                except ValueError as e:
                    print(f"Invalid task data in row {row + 1}: {e}")
                    return None
            elif table == self.pipes_table:
                try:
                    if row_data[1]:  # Date
                        datetime.strptime(row_data[1], "%Y-%m-%d")
                except ValueError as e:
                    print(f"Invalid pipe data in row {row + 1}: {e}")
                    return None
            data.append(row_data)
        return data

    def generate_and_show_svg(self):
        """Generate and display the Gantt chart."""
        data = {
            "tasks": self._get_table_data(self.tasks_table),
            "pipes": self._get_table_data(self.pipes_table),
            "curtains": self._get_table_data(self.curtains_table)
        }
        if None in data.values():
            print("Cannot generate SVG due to invalid data.")
            return
        svg_path = generate_svg(data, output_folder="svg", output_filename="gantt_chart.svg")
        self.svg_window = SVGDisplayWindow(svg_path)
        self.svg_window.show()

    def save_to_json(self):
        """Save all table data to a JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Files (*.json)")
        if file_path:
            try:
                data = {
                    "tasks": self._get_table_data(self.tasks_table),
                    "pipes": self._get_table_data(self.pipes_table),
                    "curtains": self._get_table_data(self.curtains_table)
                }
                if None in data.values():
                    print("Cannot save due to invalid data.")
                    return
                with open(file_path, 'w') as jsonfile:
                    json.dump(data, jsonfile, indent=4)
            except Exception as e:
                print(f"Error saving JSON: {e}")

    def load_from_json(self):
        """Load table data from a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as jsonfile:
                    data = json.load(jsonfile)
                for table_name, table in [("tasks", self.tasks_table), ("pipes", self.pipes_table), ("curtains", self.curtains_table)]:
                    table_data = data.get(table_name, [])
                    if table_data:
                        table.setRowCount(len(table_data))
                        for row_idx, row_data in enumerate(table_data):
                            for col_idx, value in enumerate(row_data):
                                table.setItem(row_idx, col_idx, QTableWidgetItem(value))
            except Exception as e:
                print(f"Error loading JSON: {e}")

