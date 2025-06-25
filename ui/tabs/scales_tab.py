from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from .base_tab import BaseTab

class ScalesTab(BaseTab):
    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Scales functionality will be implemented in a future version.")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

    def _load_initial_data_impl(self):
        pass
