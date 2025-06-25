from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import Qt
from .base_tab import BaseTab

class PlaceholderTab(BaseTab):
    def __init__(self, project_data, app_config, tab_name):
        self.tab_name = tab_name
        super().__init__(project_data, app_config)

    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel(f"{self.tab_name} functionality will be implemented in a future version.")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

    def _load_initial_data_impl(self):
        pass  # Placeholder method to maintain interface compatibility
