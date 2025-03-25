"""
Purpose: Handles SVG creation, decoupled from UI.
Why: Moves SVG logic out of the UI class, making it a standalone utility. You can tweak the SVG design here (e.g., add shapes) without touching UI code.
"""


import svgwrite

def generate_svg(data, output_path="output.svg"):
    dwg = svgwrite.Drawing(output_path, size=("400px", "300px"))
    for i, row in enumerate(data):
        dwg.add(dwg.text(f"Row {i}: {row}", insert=(10, 20 + i * 20), fill="black"))
    dwg.save()
    return output_path

