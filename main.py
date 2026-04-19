"""Точка входа SimplyPaste."""

import sys
import os

os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.main_window import MainWindow


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("SimplyPaste")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SimplyPaste")

    app.setFont(QFont("Segoe UI", 10))
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
