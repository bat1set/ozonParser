from moduls.utils import *
from moduls.VirtualEnvManager import VirtualEnvManager
from PyQt6.QtWidgets import QApplication
import sys

# Импорты GUI компонентов
from gui.windows.main_window import MainWindow


def main():
    # Создание виртуального окружения
    VirtualEnvManager(
        mod='default',
        libs=[
            'selenium',
            'webdriver-manager',
            'fake-useragent',
            'PyQt6',
            'pyqtgraph',
            'requests'
        ]
    )
    clear()

    # Запуск GUI приложения
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()