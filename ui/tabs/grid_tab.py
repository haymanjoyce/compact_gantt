from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QGridLayout, QCheckBox, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from .base_tab import BaseTab

class GridTab(BaseTab):
    def setup_ui(self):
        layout = QVBoxLayout()
        grid_group = self._create_grid_settings_group()
        layout.addWidget(grid_group)
        self.setLayout(layout)

    def _create_grid_settings_group(self) -> QGroupBox:
        group = QGroupBox("Grid Settings")
        layout = QGridLayout()
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(5)

        self.horizontal_gridlines = QCheckBox("Show Horizontal Gridlines")
        self.vertical_gridlines = QCheckBox("Show Vertical Gridlines")
        self.horizontal_gridlines.setToolTip("Display horizontal gridlines in the chart")
        self.vertical_gridlines.setToolTip("Display vertical gridlines in the chart")

        layout.addWidget(self.horizontal_gridlines, 0, 0)
        layout.addWidget(self.vertical_gridlines, 1, 0)
        layout.setRowStretch(2, 1)  # Add row stretch after the last field
        group.setLayout(layout)
        return group

    def _connect_signals(self):
        self.horizontal_gridlines.stateChanged.connect(self._sync_data_if_not_initializing)
        self.vertical_gridlines.stateChanged.connect(self._sync_data_if_not_initializing)

    def _load_initial_data_impl(self):
        frame_config = self.project_data.frame_config
        self.horizontal_gridlines.setChecked(frame_config.horizontal_gridlines)
        self.vertical_gridlines.setChecked(frame_config.vertical_gridlines)

    def _sync_data_impl(self):
        self.project_data.frame_config.horizontal_gridlines = self.horizontal_gridlines.isChecked()
        self.project_data.frame_config.vertical_gridlines = self.vertical_gridlines.isChecked()
        self.data_updated.emit({
            "horizontal_gridlines": self.horizontal_gridlines.isChecked(),
            "vertical_gridlines": self.vertical_gridlines.isChecked()
        })
