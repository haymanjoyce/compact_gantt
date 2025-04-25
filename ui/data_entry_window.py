from PyQt5.QtWidgets import QMainWindow, QTabWidget, QToolBar, QAction, QFileDialog, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QDate
from data_model import ProjectData
from .tabs.layout_tab import LayoutTab
from .tabs.tasks_tab import TasksTab
from .tabs.time_frames_tab import TimeFramesTab
from .tabs.connectors_tab import ConnectorsTab
from .tabs.swimlanes_tab import SwimlanesTab
from .tabs.pipes_tab import PipesTab
from .tabs.curtains_tab import CurtainsTab
from .tabs.text_boxes_tab import TextBoxesTab
import json

class DataEntryWindow(QMainWindow):
    data_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Planning Tool")
        self.setMinimumSize(600, 400)
        self.project_data = ProjectData()
        self.table_configs = {
            "time_frames": {
                "columns": ["Finish Date", "Width (%)"],
                "defaults": lambda row: [
                    (QDate.currentDate().addDays(7 * (row + 1))).toString("yyyy-MM-dd"),
                    str(100 / (row + 2))
                ],
                "min_rows": 1
            },
            "tasks": {
                "columns": ["Task ID", "Task Order", "Task Name", "Start Date", "Finish Date", "Row Number",
                            "Label Placement", "Label Hide", "Label Alignment",
                            "Horiz Offset", "Vert Offset", "Label Colour"],
                "defaults": lambda task_id, task_order: [
                    str(task_id), str(task_order), "New Task",
                    QDate.currentDate().toString("yyyy-MM-dd"),
                    QDate.currentDate().toString("yyyy-MM-dd"), "1",
                    {"type": "combo", "items": ["Inside", "To left", "To right", "Above", "Below"], "default": "Inside"},
                    "No", {"type": "combo", "items": ["Left", "Centre", "Right"], "default": "Left"},
                    "1.0", "0.5", "black"
                ],
                "min_rows": 1
            },
            "connectors": {
                "columns": ["From Task ID", "To Task ID"],
                "defaults": lambda row: ["1", "2"],
                "min_rows": 0
            },
            "swimlanes": {
                "columns": ["From Row Number", "To Row Number", "Title", "Colour"],
                "defaults": lambda row: ["1", "2", f"Swimlane {row + 1}", "lightblue"],
                "min_rows": 0
            },
            "pipes": {
                "columns": ["Date", "Colour"],
                "defaults": lambda row: [QDate.currentDate().toString("yyyy-MM-dd"), "red"],
                "min_rows": 0
            },
            "curtains": {
                "columns": ["From Date", "To Date", "Colour"],
                "defaults": lambda row: [
                    QDate.currentDate().toString("yyyy-MM-dd"),
                    QDate.currentDate().toString("yyyy-MM-dd"), "gray"
                ],
                "min_rows": 0
            },
            "text_boxes": {
                "columns": ["Text", "X Coordinate", "Y Coordinate", "Colour"],
                "defaults": lambda row: [f"Text {row + 1}", "100", "100", "black"],
                "min_rows": 0
            }
        }
        self.setup_ui()
        self._connect_signals()

    def setup_ui(self):
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu("File")
        self.save_action = QAction("Save Project", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_to_json)
        file_menu.addAction(self.save_action)
        self.load_action = QAction("Load Project", self)
        self.load_action.setShortcut("Ctrl+O")
        self.load_action.triggered.connect(self.load_from_json)
        file_menu.addAction(self.load_action)

        self.toolbar = QToolBar("Tools")
        self.addToolBar(self.toolbar)
        style = self.style()
        self.generate_tool = QAction(QIcon(style.standardIcon(style.SP_ArrowRight)), "Generate Gantt Chart", self)
        self.generate_tool.setShortcut("Ctrl+G")
        self.generate_tool.triggered.connect(self._emit_data_updated)
        self.toolbar.addAction(self.generate_tool)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        self.tab_widget = QTabWidget()
        self.layout_tab = LayoutTab(self.project_data)
        self.time_frames_tab = TimeFramesTab(self.project_data, self.table_configs)
        self.tasks_tab = TasksTab(self.project_data, self.table_configs)
        self.connectors_tab = ConnectorsTab(self.project_data, self.table_configs)
        self.swimlanes_tab = SwimlanesTab(self.project_data, self.table_configs)
        self.pipes_tab = PipesTab(self.project_data, self.table_configs)
        self.curtains_tab = CurtainsTab(self.project_data, self.table_configs)
        self.text_boxes_tab = TextBoxesTab(self.project_data, self.table_configs)
        self.tab_widget.addTab(self.layout_tab, "Layout")
        self.tab_widget.addTab(self.time_frames_tab, "Time Frames")
        self.tab_widget.addTab(self.tasks_tab, "Tasks")
        self.tab_widget.addTab(self.connectors_tab, "Connectors")
        self.tab_widget.addTab(self.swimlanes_tab, "Swimlanes")
        self.tab_widget.addTab(self.pipes_tab, "Pipes")
        self.tab_widget.addTab(self.curtains_tab, "Curtains")
        self.tab_widget.addTab(self.text_boxes_tab, "Text Boxes")
        self.setCentralWidget(self.tab_widget)

    def _connect_signals(self):
        for tab in [self.layout_tab, self.time_frames_tab, self.tasks_tab, self.connectors_tab,
                    self.swimlanes_tab, self.pipes_tab, self.curtains_tab, self.text_boxes_tab]:
            tab.data_updated.connect(self.data_updated.emit)

    def save_to_json(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "JSON Files (*.json)")
        if file_path:
            try:
                json_str = json.dumps(self.project_data.to_json(), indent=4)
                with open(file_path, "w") as jsonfile:
                    jsonfile.write(json_str)
                QMessageBox.information(self, "Success", "Project saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving JSON: {e}")

    def load_from_json(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as jsonfile:
                    data = json.load(jsonfile)
                self.project_data = ProjectData.from_json(data)
                for tab in [self.layout_tab, self.time_frames_tab, self.tasks_tab, self.connectors_tab,
                            self.swimlanes_tab, self.pipes_tab, self.curtains_tab, self.text_boxes_tab]:
                    tab._load_initial_data()
                self.data_updated.emit(self.project_data.to_json())
                QMessageBox.information(self, "Success", "Project loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading JSON: {e}")

    def _emit_data_updated(self):
        self.data_updated.emit(self.project_data.to_json())