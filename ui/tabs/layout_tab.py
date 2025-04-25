from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGroupBox, QGridLayout, QLineEdit, QLabel, QCheckBox, QDateEdit
from PyQt5.QtCore import pyqtSignal, QDate
from data_model import FrameConfig

class LayoutTab(QWidget):
    data_updated = pyqtSignal(dict)

    def __init__(self, project_data):
        super().__init__()
        self.project_data = project_data
        self.setup_ui()
        self._load_initial_data()
        for widget in [self.outer_width_input, self.outer_height_input, self.header_height_input,
                       self.footer_height_input, self.top_margin_input, self.right_margin_input,
                       self.bottom_margin_input, self.left_margin_input, self.header_text_input,
                       self.footer_text_input, self.num_rows_input]:
            widget.textChanged.connect(self._sync_data_if_not_initializing)
        self.horizontal_gridlines_input.stateChanged.connect(self._sync_data_if_not_initializing)
        self.vertical_gridlines_input.stateChanged.connect(self._sync_data_if_not_initializing)
        self.chart_start_date_input.dateChanged.connect(self._sync_data_if_not_initializing)
        self._initializing = False

    def setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        # Dimensions group
        dim_group = QGroupBox("Dimensions")
        dim_layout = QGridLayout()
        dim_layout.addWidget(QLabel("Outer Width:"), 0, 0)
        self.outer_width_input = QLineEdit()
        dim_layout.addWidget(self.outer_width_input, 0, 1)
        dim_layout.addWidget(QLabel("Outer Height:"), 1, 0)
        self.outer_height_input = QLineEdit()
        dim_layout.addWidget(self.outer_height_input, 1, 1)
        dim_layout.addWidget(QLabel("Header Height:"), 2, 0)
        self.header_height_input = QLineEdit()
        dim_layout.addWidget(self.header_height_input, 2, 1)
        dim_layout.addWidget(QLabel("Footer Height:"), 3, 0)
        self.footer_height_input = QLineEdit()
        dim_layout.addWidget(self.footer_height_input, 3, 1)
        dim_group.setLayout(dim_layout)
        layout.addWidget(dim_group)

        # Margins group
        margins_group = QGroupBox("Margins")
        margins_layout = QGridLayout()
        margins_layout.addWidget(QLabel("Top:"), 0, 0)
        self.top_margin_input = QLineEdit()
        margins_layout.addWidget(self.top_margin_input, 0, 1)
        margins_layout.addWidget(QLabel("Right:"), 1, 0)
        self.right_margin_input = QLineEdit()
        margins_layout.addWidget(self.right_margin_input, 1, 1)
        margins_layout.addWidget(QLabel("Bottom:"), 2, 0)
        self.bottom_margin_input = QLineEdit()
        margins_layout.addWidget(self.bottom_margin_input, 2, 1)
        margins_layout.addWidget(QLabel("Left:"), 3, 0)
        self.left_margin_input = QLineEdit()
        margins_layout.addWidget(self.left_margin_input, 3, 1)
        margins_group.setLayout(margins_layout)
        layout.addWidget(margins_group)

        # Text group
        text_group = QGroupBox("Text")
        text_layout = QGridLayout()
        text_layout.addWidget(QLabel("Header Text:"), 0, 0)
        self.header_text_input = QLineEdit()
        text_layout.addWidget(self.header_text_input, 0, 1)
        text_layout.addWidget(QLabel("Footer Text:"), 1, 0)
        self.footer_text_input = QLineEdit()
        text_layout.addWidget(self.footer_text_input, 1, 1)
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)

        # Gridlines group
        grid_group = QGroupBox("Gridlines")
        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel("Horizontal:"), 0, 0)
        self.horizontal_gridlines_input = QCheckBox()
        grid_layout.addWidget(self.horizontal_gridlines_input, 0, 1)
        grid_layout.addWidget(QLabel("Vertical:"), 1, 0)
        self.vertical_gridlines_input = QCheckBox()
        grid_layout.addWidget(self.vertical_gridlines_input, 1, 1)
        grid_group.setLayout(grid_layout)
        layout.addWidget(grid_group)

        # Setup group
        setup_group = QGroupBox("Setup")
        setup_layout = QGridLayout()
        setup_layout.addWidget(QLabel("Chart Start Date:"), 0, 0)
        self.chart_start_date_input = QDateEdit()
        self.chart_start_date_input.setCalendarPopup(True)
        self.chart_start_date_input.setDisplayFormat("yyyy-MM-dd")
        setup_layout.addWidget(self.chart_start_date_input, 0, 1)
        setup_layout.addWidget(QLabel("Number of Rows:"), 1, 0)
        self.num_rows_input = QLineEdit()
        setup_layout.addWidget(self.num_rows_input, 1, 1)
        setup_group.setLayout(setup_layout)
        layout.addWidget(setup_group)

        layout.addStretch()
        scroll.setWidget(content_widget)
        scroll_layout = QVBoxLayout()
        scroll_layout.addWidget(scroll)
        self.setLayout(scroll_layout)

    def _load_initial_data(self):
        self._initializing = True
        frame_config = self.project_data.frame_config
        self.outer_width_input.setText(str(float(frame_config.outer_width or 800)))
        self.outer_height_input.setText(str(float(frame_config.outer_height or 600)))
        self.header_height_input.setText(str(float(frame_config.header_height or 50)))
        self.footer_height_input.setText(str(float(frame_config.footer_height or 50)))
        self.top_margin_input.setText(str(float(frame_config.margins[0] or 10)))
        self.right_margin_input.setText(str(float(frame_config.margins[1] or 10)))
        self.bottom_margin_input.setText(str(float(frame_config.margins[2] or 10)))
        self.left_margin_input.setText(str(float(frame_config.margins[3] or 10)))
        self.header_text_input.setText(str(frame_config.header_text or ""))
        self.footer_text_input.setText(str(frame_config.footer_text or ""))
        self.num_rows_input.setText(str(int(frame_config.num_rows or 1)))
        self.horizontal_gridlines_input.setChecked(bool(frame_config.horizontal_gridlines))
        self.vertical_gridlines_input.setChecked(bool(frame_config.vertical_gridlines))
        chart_start_date = frame_config.chart_start_date or "2025-01-01"
        self.chart_start_date_input.setDate(QDate.fromString(chart_start_date, "yyyy-MM-dd"))
        self._initializing = False

    def _sync_data(self):
        try:
            margins = (
                float(self.top_margin_input.text() or 0),
                float(self.right_margin_input.text() or 0),
                float(self.bottom_margin_input.text() or 0),
                float(self.left_margin_input.text() or 0)
            )
            self.project_data.frame_config = FrameConfig(
                float(self.outer_width_input.text() or 800),
                float(self.outer_height_input.text() or 600),
                float(self.header_height_input.text() or 50),
                float(self.footer_height_input.text() or 50),
                margins,
                int(self.num_rows_input.text() or 1),
                self.header_text_input.text(),
                self.footer_text_input.text(),
                self.horizontal_gridlines_input.isChecked(),
                self.vertical_gridlines_input.isChecked(),
                self.chart_start_date_input.date().toString("yyyy-MM-dd")
            )
            self.data_updated.emit(self.project_data.to_json())
        except ValueError as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Invalid input: {e}")

    def _sync_data_if_not_initializing(self):
        if not self._initializing:
            self._sync_data()