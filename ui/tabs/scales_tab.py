from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QGridLayout, QCheckBox
from PyQt5.QtCore import pyqtSignal, Qt
from .base_tab import BaseTab

class ScalesTab(BaseTab):
    def setup_ui(self):
        layout = QVBoxLayout()
        scales_group = self._create_scales_settings_group()
        layout.addWidget(scales_group)
        
        # Add stretch at the end to push all groups to the top
        layout.addStretch(1)
        
        self.setLayout(layout)

    def _create_scales_settings_group(self) -> QGroupBox:
        group = QGroupBox("Scale Settings")
        layout = QGridLayout()
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(5)

        self.show_years = QCheckBox("Show Years")
        self.show_months = QCheckBox("Show Months")
        self.show_weeks = QCheckBox("Show Weeks")
        self.show_days = QCheckBox("Show Days")
        
        self.show_years.setToolTip("Display the years scale in the chart")
        self.show_months.setToolTip("Display the months scale in the chart")
        self.show_weeks.setToolTip("Display the weeks scale in the chart")
        self.show_days.setToolTip("Display the days scale in the chart")

        layout.addWidget(self.show_years, 0, 0)
        layout.addWidget(self.show_months, 1, 0)
        layout.addWidget(self.show_weeks, 2, 0)
        layout.addWidget(self.show_days, 3, 0)
        group.setLayout(layout)
        return group

    def _connect_signals(self):
        self.show_years.stateChanged.connect(self._sync_data_if_not_initializing)
        self.show_months.stateChanged.connect(self._sync_data_if_not_initializing)
        self.show_weeks.stateChanged.connect(self._sync_data_if_not_initializing)
        self.show_days.stateChanged.connect(self._sync_data_if_not_initializing)

    def _load_initial_data_impl(self):
        frame_config = self.project_data.frame_config
        self.show_years.setChecked(getattr(frame_config, 'show_years', True))
        self.show_months.setChecked(getattr(frame_config, 'show_months', True))
        self.show_weeks.setChecked(getattr(frame_config, 'show_weeks', True))
        self.show_days.setChecked(getattr(frame_config, 'show_days', True))

    def _sync_data_impl(self):
        self.project_data.frame_config.show_years = self.show_years.isChecked()
        self.project_data.frame_config.show_months = self.show_months.isChecked()
        self.project_data.frame_config.show_weeks = self.show_weeks.isChecked()
        self.project_data.frame_config.show_days = self.show_days.isChecked()
        self.data_updated.emit({
            "show_years": self.show_years.isChecked(),
            "show_months": self.show_months.isChecked(),
            "show_weeks": self.show_weeks.isChecked(),
            "show_days": self.show_days.isChecked()
        })
