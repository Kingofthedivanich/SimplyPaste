"""
main.py — точка входа SimplyPaste.
Инициализирует Qt-приложение и запускает главное окно.
"""

import sys
import os

# Убираем лишние предупреждения Qt на Windows 11
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from gui.main_window import MainWindow


def main():
    # Включаем поддержку High-DPI для чётких шрифтов на 4K-мониторах
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("SimplyPaste")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SimplyPaste")

    # Глобальный шрифт
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Запрещаем выход при закрытии последнего окна (работаем в трее)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
