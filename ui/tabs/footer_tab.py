from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QGroupBox, QLineEdit, 
                           QLabel, QMessageBox)
from PyQt5.QtCore import pyqtSignal, Qt
from typing import Dict, Any
import logging
from .base_tab import BaseTab

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FooterTab(BaseTab):
    def setup_ui(self):
        layout = QVBoxLayout()
        LABEL_WIDTH = 120  # Consistent label width

        # Footer Group
        footer_group = self._create_footer_group(LABEL_WIDTH)
        layout.addWidget(footer_group)

        self.setLayout(layout)

    def _create_footer_group(self, label_width: int) -> QGroupBox:
        group = QGroupBox("Footer Settings")
        layout = QGridLayout()
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(5)

        # Footer height
        footer_height_label = QLabel("Footer Height:")
        footer_height_label.setFixedWidth(label_width)
        self.footer_height = QLineEdit("50")
        self.footer_height.setToolTip("Height of the footer section in pixels")

        # Footer text
        footer_text_label = QLabel("Footer Text:")
        footer_text_label.setFixedWidth(label_width)
        self.footer_text = QLineEdit()
        self.footer_text.setToolTip("Text to display in the footer")

        layout.addWidget(footer_height_label, 0, 0)
        layout.addWidget(self.footer_height, 0, 1)
        layout.addWidget(footer_text_label, 1, 0)
        layout.addWidget(self.footer_text, 1, 1)
        layout.setColumnStretch(1, 1)
        group.setLayout(layout)
        return group

    def _connect_signals(self):
        self.footer_height.textChanged.connect(self._sync_data_if_not_initializing)
        self.footer_text.textChanged.connect(self._sync_data_if_not_initializing)

    def _load_initial_data_impl(self):
        frame_config = self.project_data.frame_config

        # Load Footer settings
        self.footer_height.setText(str(frame_config.footer_height))
        self.footer_text.setText(frame_config.footer_text)

    def _sync_data_impl(self):
        # Validate numeric inputs
        numeric_fields = {
            "footer_height": self.footer_height.text(),
        }

        for field_name, value in numeric_fields.items():
            try:
                if not value.strip() or int(value) <= 0:
                    raise ValueError(f"{field_name.replace('_', ' ').title()} must be a positive number")
            except ValueError as e:
                if "must be a positive number" not in str(e):
                    raise ValueError(f"{field_name.replace('_', ' ').title()} must be a valid number")
                raise

        # Update frame config
        self.project_data.frame_config.footer_height = int(self.footer_height.text())
        self.project_data.frame_config.footer_text = self.footer_text.text()

        # Emit data updated signal
        self.data_updated.emit({
            'footer_height': self.project_data.frame_config.footer_height,
            'footer_text': self.project_data.frame_config.footer_text
        })
