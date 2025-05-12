from PyQt5.QtWidgets import QDialog, QVBoxLayout, QMainWindow, QWidget, QLabel, QScrollArea, QPushButton, QHBoxLayout
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os
from config.app_config import AppConfig
from ui.window_utils import move_window_to_screen_center, move_window_to_screen_right_of
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPainter


class ZoomableSvgWidget(QSvgWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 1.0

    def setZoom(self, zoom):
        self._zoom = zoom
        self.updateGeometry()
        self.update()

    def zoomIn(self):
        self.setZoom(self._zoom * 1.2)

    def zoomOut(self):
        self.setZoom(self._zoom / 1.2)

    def sizeHint(self):
        base = self.renderer().defaultSize()
        return QSize(int(base.width() * self._zoom), int(base.height() * self._zoom))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.scale(self._zoom, self._zoom)
        self.renderer().render(painter)


class SVGDisplayWindow(QDialog):
    def __init__(self, app_config, initial_path=None, reference_window=None):
        super().__init__()
        self.setWindowTitle("SVG Display")
        self.setWindowIcon(QIcon("assets/logo.png"))  # Add window icon

        # Set window size using display window variables
        width = app_config.general.svg_display_width
        height = app_config.general.svg_display_height
        self.resize(width, height)

        self.svg_widget = ZoomableSvgWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.svg_widget)
        self.scroll_area.setWidgetResizable(False)  # Important: don't scale SVG
        self.scroll_area.setAlignment(Qt.AlignCenter)  # <-- Center the SVG

        # Add zoom buttons
        zoom_in_btn = QPushButton("Zoom In")
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_in_btn.clicked.connect(lambda: [self.svg_widget.zoomIn(), self.center_scroll_area_on_svg()])
        zoom_out_btn.clicked.connect(lambda: [self.svg_widget.zoomOut(), self.center_scroll_area_on_svg()])
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(zoom_in_btn)
        btn_layout.addWidget(zoom_out_btn)

        self.layout = QVBoxLayout()
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

        if initial_path and os.path.exists(initial_path):
            self.load_svg(initial_path)

        # Try to open on screen 2 (index 1)
        app = QApplication.instance()
        screens = app.screens()
        if len(screens) > 1:
            move_window_to_screen_center(self, screen_number=1, width=width, height=height)
        else:
            # Open to the right of DataEntryWindow on screen 1
            if reference_window is not None:
                move_window_to_screen_right_of(self, reference_window, screen_number=0, width=width, height=height)
            else:
                move_window_to_screen_center(self, screen_number=0, width=width, height=height)

    def load_svg(self, svg_path):
        print("Received SVG path:", svg_path)  # Debug
        absolute_path = os.path.abspath(svg_path)
        if os.path.exists(absolute_path):
            print(f"Loading SVG from: {absolute_path}")
            self.svg_widget.load(absolute_path)
            # Set the widget to the SVG's native size
            renderer = self.svg_widget.renderer()
            size = renderer.defaultSize()
            self.svg_widget.setFixedSize(size)
            self.svg_widget.setZoom(1.0)  # Reset zoom on load
            self.show()
        else:
            print(f"SVG file not found: {absolute_path}")

    def center_scroll_area_on_svg(self):
        area = self.scroll_area
        widget = self.svg_widget
        h_bar = area.horizontalScrollBar()
        v_bar = area.verticalScrollBar()
        widget_center_x = widget.width() // 2
        widget_center_y = widget.height() // 2
        viewport_width = area.viewport().width()
        viewport_height = area.viewport().height()
        h_bar.setValue(widget_center_x - viewport_width // 2)
        v_bar.setValue(widget_center_y - viewport_height // 2)
