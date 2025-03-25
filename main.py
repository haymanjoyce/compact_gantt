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

