"""
Purpose: Handles SVG creation, decoupled from UI.
Why: Moves SVG logic out of the UI class, making it a standalone utility. You can tweak the SVG design here (e.g., add shapes) without touching UI code.
"""


import svgwrite
import os

def generate_svg(data, output_folder="svg", output_filename="gantt_chart.svg"):
    # Ensure the svg folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Construct full path
    output_path = os.path.join(output_folder, output_filename)

    # Placeholder Gantt chart (to be expanded later)
    dwg = svgwrite.Drawing(output_path, size=("800px", "400px"))
    dwg.add(dwg.text("Gantt placeholder with tabs", insert=(10, 20), fill="black"))
    dwg.save()

    return output_path

