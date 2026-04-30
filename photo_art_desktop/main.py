"""
PhotoArt Desktop - Main Entry Point
PySide6 + qfluentwidgets based desktop application
"""
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from qfluentwidgets import setTheme, Theme

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setObjectName("PhotoArtDesktop")
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    # Apply Fluent light theme
    setTheme(Theme.LIGHT)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
