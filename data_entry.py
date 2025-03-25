"""
Purpose: Defines DataEntryWindow, handles user input and button actions.
Why: Isolates the input UI logic. It imports generate_svg and SVGDisplayWindow to delegate tasks, keeping it focused on UI.
"""


import os
from PyQt5.QtWidgets import QMainWindow, QTableWidget, QPushButton, QVBoxLayout, QWidget, QTabWidget
from svg_display import SVGDisplayWindow
from svg_generator import generate_svg

class DataEntryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Data")
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.create_tab("Tab 1")
        self.create_tab("Tab 2")

        # Initialize svg_window attribute
        self.svg_window = None

    def create_tab(self, tab_name):
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
        tab_layout.addWidget(table)

        generate_btn = QPushButton("Generate SVG")
        generate_btn.clicked.connect(lambda: self.generate_and_show_svg(table))
        tab_layout.addWidget(generate_btn)

        self.tab_widget.addTab(tab, tab_name)

    def generate_and_show_svg(self, table):
        # Ensure the svg directory exists
        svg_dir = "svg"
        os.makedirs(svg_dir, exist_ok=True)

        # Extract data from table
        data = []
        for row in range(table.rowCount()):
            row_data = []
            for col in range(table.columnCount()):
                item = table.item(row, col)
                row_data.append(item.text() if item else "0")
            data.append(row_data)

        # Generate SVG and display
        svg_path = os.path.join(svg_dir, "output.svg")
        generate_svg(data, svg_path)
        self.svg_window = SVGDisplayWindow(svg_path)
        self.svg_window.show()

