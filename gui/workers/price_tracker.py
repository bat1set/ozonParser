from PyQt6.QtCore import QThread, pyqtSignal
from moduls.ParserJson import JsonParser
from moduls.Driver import SeleniumDriver
from moduls.Scraper import OzonPriceScraper
from selenium.webdriver.edge.options import Options


def _product(url):
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


class PriceTrackerWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.json_parser = JsonParser()

    def run(self):
        try:
            # Получаем данные о товаре
            product_data = _product(self.url)

            # Обновляем данные в JSON файлах
            updated_data = self.json_parser.update_product_data(product_data)

            # Добавляем URL в данные
            updated_data['url'] = self.url
            updated_data['name'] = product_data['name']

            self.finished.emit(updated_data)
        except Exception as e:
            self.finished.emit({'error': str(e)})