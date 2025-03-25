"""
Defines SVGDisplayWindow, handles SVG rendering.
Why: Separates the output UI into its own module. It’s reusable for any SVG display need, not tied to the data entry.
"""


from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtSvg import QSvgWidget

class SVGDisplayWindow(QDialog):
    def __init__(self, svg_path):
        super().__init__()
        self.setWindowTitle("SVG Display")
        self.setGeometry(150, 150, 400, 300)

        self.svg_widget = QSvgWidget(svg_path)
        self.svg_widget.setGeometry(0, 0, 400, 300)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.svg_widget)
        self.setLayout(self.layout)

