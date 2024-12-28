from PyQt6.QtCore import QThread, pyqtSignal
from moduls.ParserJson import JsonParser


class PriceTrackerWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, url, product_func):
        super().__init__()
        self.url = url
        self.product_func = product_func
        self.json_parser = JsonParser()

    def run(self):
        try:
            # Получаем данные о товаре
            product_data = self.product_func(self.url)

            # Обновляем данные в JSON файлах
            updated_data = self.json_parser.update_product_data(product_data)

            # Добавляем URL в данные
            updated_data['url'] = self.url
            updated_data['name'] = product_data['name']

            self.finished.emit(updated_data)
        except Exception as e:
            self.finished.emit({'error': str(e)})