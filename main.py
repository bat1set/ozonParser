from moduls.utils import *
from moduls.Driver import SeleniumDriver
from moduls.Scraper import OzonPriceScraper
from moduls.VirtualEnvManager import VirtualEnvManager
from selenium.webdriver.edge.options import Options
from PyQt6.QtWidgets import QApplication
import sys

# Импорты GUI компонентов
from gui.windows.main_window import MainWindow

def product(url):
    """Функция для получения информации о товаре с сайта"""
    # Настройка опций для драйвера
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Создание экземпляра драйвера
    driver = SeleniumDriver(options)

    # Создание экземпляра парсера
    scraper = OzonPriceScraper(url, driver)

    return scraper.get_product_details()

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