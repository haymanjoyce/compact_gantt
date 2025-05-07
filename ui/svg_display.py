from PyQt5.QtWidgets import QDialog, QVBoxLayout, QMainWindow, QWidget, QLabel, QScrollArea
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os
from config.app_config import AppConfig
from ui.window_utils import move_window_to_screen_center, move_window_to_screen_right_of
from PyQt5.QtWidgets import QApplication


class SVGDisplayWindow(QDialog):
    def __init__(self, app_config, initial_path=None):
        super().__init__()
        self.setWindowTitle("SVG Display")
        self.setWindowIcon(QIcon("assets/logo.png"))  # Add window icon

        self.svg_widget = QSvgWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.svg_widget)
        self.setLayout(self.layout)

        if initial_path and os.path.exists(initial_path):
            self.load_svg(initial_path)

        # Try to open on screen 2 (index 1)
        width = app_config.general.svg_display_width
        height = app_config.general.svg_display_height
        app = QApplication.instance()
        screens = app.screens()
        if len(screens) > 1:
            move_window_to_screen_center(self, screen_number=1, width=width, height=height)
        else:
            # Open to the right of DataEntryWindow on screen 1
            move_window_to_screen_right_of(self, self, screen_number=0, width=width, height=height)

    def load_svg(self, svg_path):
        print("Received SVG path:", svg_path)  # Debug
        absolute_path = os.path.abspath(svg_path)
        if os.path.exists(absolute_path):
            print(f"Loading SVG from: {absolute_path}")
            self.svg_widget.load(absolute_path)
            self.show()
        else:
            print(f"SVG file not found: {absolute_path}")
