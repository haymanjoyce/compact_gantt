"""
Purpose: Generates an SVG Gantt chart from ProjectData.
Why: Visualizes the layout structure and tasks for project planning.
"""

import svgwrite
from datetime import datetime, timedelta
import calendar
import os
from PyQt5.QtCore import QObject, pyqtSignal
from config import Config

class GanttChartGenerator(QObject):
    svg_generated = pyqtSignal(str)

    def __init__(self, output_folder: str = Config.SVG_OUTPUT_FOLDER,
                 output_filename: str = Config.SVG_OUTPUT_FILENAME):
        super().__init__()
        self.output_folder = output_folder
        self.output_filename = output_filename
        self.dwg = None
        self.data = {"frame_config": {}, "time_frames": [], "tasks": []}
        self.time_scale = None
        self.start_date = None

    def generate_svg(self, data):
        try:
            self.data = data
            width = self.data["frame_config"]["outer_width"]
            height = self.data["frame_config"]["outer_height"]
            self.dwg = svgwrite.Drawing(filename=os.path.abspath(os.path.join(self.output_folder, self.output_filename)),
                                      size=(width, height))
            self.time_scale, self.start_date = self._set_time_scale()
            self.render()
            svg_path = os.path.abspath(os.path.join(self.output_folder, self.output_filename))
            self.svg_generated.emit(svg_path)
            return svg_path
        except Exception as e:
            raise ValueError(f"SVG generation failed: {e}")

    def _calculate_time_range(self):
        if not (self.data["time_frames"] or self.data["tasks"]):
            return datetime.now(), datetime.now() + timedelta(days=7)
        dates = []
        for tf in self.data["time_frames"]:
            dates.append(datetime.strptime(tf["start_date"], "%Y-%m-%d"))
            dates.append(datetime.strptime(tf["end_date"], "%Y-%m-%d"))
        for task in self.data["tasks"]:
            dates.append(datetime.strptime(task["start_date"], "%Y-%m-%d"))
            dates.append(datetime.strptime(task["finish_date"], "%Y-%m-%d"))
        if not dates:
            return datetime.now(), datetime.now() + timedelta(days=7)
        min_date = min(dates)
        max_date = max(dates)
        return min_date - timedelta(days=1), max_date + timedelta(days=1)

    def _set_time_scale(self):
        start_date, end_date = self._calculate_time_range()
        total_days = (end_date - start_date).days
        margins = self.data["frame_config"]["margins"]
        chart_width = self.data["frame_config"]["outer_width"] - margins[1] - margins[3]
        return chart_width / total_days if total_days > 0 else 1, start_date

    def render_outer_frame(self):
        width = self.data["frame_config"]["outer_width"]
        height = self.data["frame_config"]["outer_height"]
        self.dwg.add(self.dwg.rect(insert=(0, 0), size=(width, height), fill="white", stroke="black", stroke_width=2))

    def render_header(self):
        margins = self.data["frame_config"]["margins"]
        width = self.data["frame_config"]["outer_width"] - margins[1] - margins[3]
        height = self.data["frame_config"]["header_height"]
        self.dwg.add(self.dwg.rect(insert=(margins[3], margins[0]), size=(width, height),
                                  fill="lightgray", stroke="black", stroke_width=1))
        if self.data["frame_config"]["header_text"]:
            self.dwg.add(self.dwg.text(self.data["frame_config"]["header_text"],
                                      insert=(margins[3] + width / 2, margins[0] + height / 2),
                                      text_anchor="middle", font_size="14"))

    def render_footer(self):
        margins = self.data["frame_config"]["margins"]
        width = self.data["frame_config"]["outer_width"] - margins[1] - margins[3]
        height = self.data["frame_config"]["footer_height"]
        y = self.data["frame_config"]["outer_height"] - margins[2] - height
        self.dwg.add(self.dwg.rect(insert=(margins[3], y), size=(width, height),
                                  fill="lightgray", stroke="black", stroke_width=1))
        if self.data["frame_config"]["footer_text"]:
            self.dwg.add(self.dwg.text(self.data["frame_config"]["footer_text"],
                                      insert=(margins[3] + width / 2, y + height / 2),
                                      text_anchor="middle", font_size="14"))

    def render_inner_frame(self):
        margins = self.data["frame_config"]["margins"]
        width = self.data["frame_config"]["outer_width"] - margins[1] - margins[3]
        y = margins[0] + self.data["frame_config"]["header_height"]
        height = (self.data["frame_config"]["outer_height"] - self.data["frame_config"]["header_height"] -
                  self.data["frame_config"]["footer_height"] - margins[0] - margins[2])
        self.dwg.add(self.dwg.rect(insert=(margins[3], y), size=(width, height),
                                  fill="none", stroke="blue", stroke_width=1, stroke_dasharray="4"))

    def render_time_frames(self):
        margins = self.data["frame_config"]["margins"]
        inner_y = margins[0] + self.data["frame_config"]["header_height"]
        inner_width = self.data["frame_config"]["outer_width"] - margins[1] - margins[3]
        inner_height = (self.data["frame_config"]["outer_height"] - self.data["frame_config"]["header_height"] -
                        self.data["frame_config"]["footer_height"] - margins[0] - margins[2])
        x_offset = margins[3]

        for tf in self.data["time_frames"]:
            tf_width = inner_width * tf["width_proportion"]
            self.dwg.add(self.dwg.rect(insert=(x_offset, inner_y), size=(tf_width, inner_height),
                                      fill="none", stroke="red", stroke_width=1))
            self.render_scales_and_rows(x_offset, inner_y, tf_width, inner_height, tf)
            x_offset += tf_width

    def render_scales_and_rows(self, x, y, width, height, time_frame):
        upper_height = self.data["frame_config"]["upper_scale_height"]
        lower_height = self.data["frame_config"]["lower_scale_height"]
        row_frame_height = height - upper_height - lower_height

        # Upper Scale
        self.dwg.add(self.dwg.rect(insert=(x, y), size=(width, upper_height),
                                   fill="none", stroke="green", stroke_width=1))

        # Lower Scale
        lower_y = y + upper_height
        self.dwg.add(self.dwg.rect(insert=(x, lower_y), size=(width, lower_height),
                                   fill="none", stroke="orange", stroke_width=1))

        # Row Frame
        row_y = lower_y + lower_height
        self.dwg.add(self.dwg.rect(insert=(x, row_y), size=(width, row_frame_height),
                                   fill="none", stroke="purple", stroke_width=1))

        # Gridlines
        num_rows = self.data["frame_config"]["num_rows"]
        row_height = row_frame_height / num_rows if num_rows > 0 else row_frame_height
        start_date = datetime.strptime(time_frame["start_date"], "%Y-%m-%d")
        end_date = datetime.strptime(time_frame["end_date"], "%Y-%m-%d")
        total_days = max((end_date - start_date).days, 1)
        tf_time_scale = width / total_days if total_days > 0 else width

        print(f"Rendering gridlines for time_frame {time_frame['start_date']} to {time_frame['end_date']}:")
        print(f"x={x}, row_y={row_y}, width={width}, row_frame_height={row_frame_height}, num_rows={num_rows}")
        print(f"total_days={total_days}, tf_time_scale={tf_time_scale}")

        if self.data["frame_config"]["horizontal_gridlines"]:
            print("Drawing horizontal gridlines")
            for i in range(num_rows + 1):
                y_pos = row_y + i * row_height
                print(f"Horizontal line at y={y_pos}")
                self.dwg.add(self.dwg.line((x, y_pos), (x + width, y_pos), stroke="gray", stroke_width=1))

        if self.data["frame_config"]["vertical_gridlines"]:
            print("Drawing vertical gridlines")

            def next_period(date, interval):
                if interval == "days":
                    return date + timedelta(days=1)
                elif interval == "weeks":  # Next Sunday (UK week end)
                    days_to_sunday = (6 - date.weekday()) % 7  # Sunday is 6
                    if days_to_sunday == 0:  # Already Sunday
                        days_to_sunday = 7
                    return date + timedelta(days=days_to_sunday)
                elif interval == "months":  # Last day of month
                    year, month = date.year, date.month
                    last_day = calendar.monthrange(year, month)[1]
                    month_end = datetime(year, month, last_day)
                    if month_end <= date:  # Move to next month if at or past end
                        month += 1
                        if month > 12:
                            month = 1
                            year += 1
                        last_day = calendar.monthrange(year, month)[1]
                        month_end = datetime(year, month, last_day)
                    return month_end
                elif interval == "years":  # Dec 31
                    year_end = datetime(date.year, 12, 31)
                    if year_end <= date:
                        year_end = datetime(date.year + 1, 12, 31)
                    return year_end
                return date

            # Upper scale gridlines (darker/thicker)
            current_date = start_date
            upper_interval = time_frame["upper_scale_intervals"]
            # Move to first period end if start_date isn’t one
            current_date = next_period(current_date, upper_interval)
            while current_date <= end_date:
                x_pos = x + (current_date - start_date).days * tf_time_scale
                if x <= x_pos <= x + width:
                    print(f"Upper scale vertical line at x={x_pos} ({current_date.strftime('%Y-%m-%d')})")
                    self.dwg.add(self.dwg.line((x_pos, row_y), (x_pos, row_y + row_frame_height),
                                               stroke="black", stroke_width=2))
                current_date = next_period(current_date, upper_interval)

            # Lower scale gridlines (lighter/thinner)
            current_date = start_date
            lower_interval = time_frame["lower_scale_intervals"]
            # Move to first period end if start_date isn’t one
            current_date = next_period(current_date, lower_interval)
            while current_date <= end_date:
                x_pos = x + (current_date - start_date).days * tf_time_scale
                if x <= x_pos <= x + width:
                    print(f"Lower scale vertical line at x={x_pos} ({current_date.strftime('%Y-%m-%d')})")
                    self.dwg.add(self.dwg.line((x_pos, row_y), (x_pos, row_y + row_frame_height),
                                               stroke="gray", stroke_width=1))
                current_date = next_period(current_date, lower_interval)

    def render_tasks(self):
        margins = self.data["frame_config"]["margins"]
        inner_y = margins[0] + self.data["frame_config"]["header_height"]
        inner_height = (self.data["frame_config"]["outer_height"] - self.data["frame_config"]["header_height"] -
                        self.data["frame_config"]["footer_height"] - margins[0] - margins[2])
        upper_height = self.data["frame_config"]["upper_scale_height"]
        lower_height = self.data["frame_config"]["lower_scale_height"]
        row_frame_y = inner_y + upper_height + lower_height
        num_rows = self.data["frame_config"]["num_rows"]
        row_height = (inner_height - upper_height - lower_height) / num_rows if num_rows > 0 else inner_height

        for task in self.data["tasks"]:
            row_num = min(task["row_number"] - 1, num_rows - 1)  # 1-based to 0-based, cap at max rows
            start_dt = datetime.strptime(task["start_date"], "%Y-%m-%d")
            finish_dt = datetime.strptime(task["finish_date"], "%Y-%m-%d")
            x = margins[3] + (start_dt - self.start_date).days * self.time_scale
            width = (finish_dt - start_dt).days * self.time_scale
            y = row_frame_y + row_num * row_height
            self.dwg.add(self.dwg.rect(insert=(x, y), size=(width, row_height * 0.8), fill="blue"))
            self.dwg.add(self.dwg.text(task["task_name"], insert=(x + 5, y + row_height * 0.4),
                                      font_size="10", fill="white"))

    def render(self):
        os.makedirs(self.output_folder, exist_ok=True)
        self.render_outer_frame()
        self.render_header()
        self.render_footer()
        self.render_inner_frame()
        self.render_time_frames()
        self.render_tasks()
        self.dwg.save()
        print(f"SVG saved to: {os.path.join(self.output_folder, self.output_filename)}")