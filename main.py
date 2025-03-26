"""
Purpose: Launches the app, ties everything together.
Why: Keeps the startup logic separate, making it easy to test or swap UIs later.
"""


import sys
from PyQt5.QtWidgets import QApplication
from data_entry import DataEntryWindow

def main():
    app = QApplication(sys.argv)
    window = DataEntryWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()


# TODO:
#  output svg to svg folder
#  load and save to json
#  import and export xlsx
#  Start adding non-tabular UI for project start/end dates
#  error dialogues
#  Add “New Project” or “Exit” to the File menu
#  File Management: Auto-name CSV/SVG files or add a "Save As" history.
#  Validation: Check CSV dimensions against table size before importing.
#  UI Feedback: Use QMessageBox for errors instead of print.
#  Table Flexibility: Let users resize the table (add/remove rows/columns).
#  Menu Bar: Move import/export to a File menu (self.menuBar().addMenu("File")) for a cleaner UI.
#  Next?: Add shortcuts (e.g., Ctrl+R for “Add Row”), non-tabular UI, or start the Gantt SVG?
#  svg calculations
#  tabs
#  interface for non tabular data
#  menu bar
#  dynamic update
#  export raster and pdf
#  print
#  try except
#  packaging (.exe, PyPI)
#  logging
#  testing
#  documentation
#  versioning
#  licensing
#  internationalization
#  accessibility
