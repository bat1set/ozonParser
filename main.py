from moduls.utils import *
from moduls.ParserJson import *
from moduls.Driver import SeleniumDriver
from moduls.Scraper import OzonPriceScraper
from selenium.webdriver.edge.options import Options
from moduls.VirtualEnvManager import VirtualEnvManager
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QScrollArea, QFrame, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtCore import QUrl
import pyqtgraph as pg
import json
from datetime import datetime
import requests
from io import BytesIO


class PriceTrackerWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            result = product(self.url)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({'error': str(e)})


class ProductCard(QFrame):
    def __init__(self, product_data, url, parent=None):
        super().__init__(parent)
        self.url = url
        self.product_data = product_data
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)

        layout = QVBoxLayout(self)

        # Название товара
        self.name_label = QLabel(self.product_data.get('name', 'Название не найдено'))
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        # Изображение товара
        if self.product_data.get('image') != 'Не найдено':
            try:
                image_data = requests.get(self.product_data['image']).content
                pixmap = QPixmap()
                pixmap.loadFromData(BytesIO(image_data).read())
                pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
                image_label = QLabel()
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(image_label)
            except:
                pass

        # Цены
        price_layout = QVBoxLayout()
        price_layout.addWidget(QLabel(f"Цена: {self.product_data.get('price', 'Н/Д')}"))
        price_layout.addWidget(QLabel(f"Цена со скидкой: {self.product_data.get('price_discount', 'Н/Д')}"))
        price_layout.addWidget(QLabel(f"Цена с Ozon картой: {self.product_data.get('price_card_ozon', 'Н/Д')}"))
        layout.addLayout(price_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        stats_button = QPushButton("Статистика")
        stats_button.clicked.connect(self.show_stats)
        visit_button = QPushButton("Перейти к товару")
        visit_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.url)))
        button_layout.addWidget(stats_button)
        button_layout.addWidget(visit_button)
        layout.addLayout(button_layout)

        # Настройка порогов цен
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Мин. цена:"))
        self.min_price = QSpinBox()
        self.min_price.setRange(0, 1000000)
        threshold_layout.addWidget(self.min_price)

        threshold_layout.addWidget(QLabel("Макс. цена:"))
        self.max_price = QSpinBox()
        self.max_price.setRange(0, 1000000)
        threshold_layout.addWidget(self.max_price)

        layout.addLayout(threshold_layout)

        self.update_price_color()

    def update_price_color(self):
        try:
            current_price = int(self.product_data.get('price_card_ozon', '0').replace(' ', ''))
            if self.min_price.value() <= current_price <= self.max_price.value():
                self.name_label.setStyleSheet("color: green;")
            elif current_price > self.max_price.value():
                self.name_label.setStyleSheet("color: red;")
            else:
                self.name_label.setStyleSheet("color: black;")
        except ValueError:
            self.name_label.setStyleSheet("color: black;")

    def show_stats(self):
        with open('data_Json/price_for_all_dates.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        product_name = self.product_data['name']
        if product_name in data:
            stats_window = StatsWindow(data[product_name], product_name)
            stats_window.show()


class StatsWindow(QWidget):
    def __init__(self, price_data, product_name):
        super().__init__()
        self.setWindowTitle(f"Статистика цен - {product_name}")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Создаем график
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('white')
        plot_widget.showGrid(x=True, y=True)

        dates = list(price_data.keys())
        prices_card = [float(price_data[date]['price_card_ozon']) for date in dates]
        prices_discount = [float(price_data[date]['price_discount']) for date in dates]
        prices_regular = [float(price_data[date]['price']) for date in dates]

        # Добавляем линии на график
        plot_widget.plot(range(len(dates)), prices_card, pen='b', name='Цена с Ozon картой')
        plot_widget.plot(range(len(dates)), prices_discount, pen='g', name='Цена со скидкой')
        plot_widget.plot(range(len(dates)), prices_regular, pen='r', name='Обычная цена')

        # Добавляем легенду
        plot_widget.addLegend()

        layout.addWidget(plot_widget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ozon Price Tracker")
        self.resize(1000, 800)

        # Основной виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Панель добавления URL
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введите URL товара")
        add_button = QPushButton("Добавить")
        add_button.clicked.connect(self.add_product)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(add_button)
        main_layout.addLayout(url_layout)

        # Область прокрутки для карточек товаров
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.products_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Загружаем существующие товары
        self.load_existing_products()

    def load_existing_products(self):
        try:
            with open('data_Json/main_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                for product_name, product_data in data.items():
                    product_data['name'] = product_name
                    card = ProductCard(product_data, "")  # URL нужно будет где-то хранить
                    self.products_layout.addWidget(card)
        except FileNotFoundError:
            pass

    def add_product(self):
        url = self.url_input.text().strip()
        if not url:
            return

        # Показываем индикатор загрузки
        loading_label = QLabel("Загрузка...")
        self.products_layout.addWidget(loading_label)

        # Запускаем получение данных в отдельном потоке
        self.worker = PriceTrackerWorker(url)
        self.worker.finished.connect(lambda result: self.on_product_loaded(result, loading_label, url))
        self.worker.start()

    def on_product_loaded(self, product_data, loading_label, url):
        loading_label.deleteLater()
        if 'error' not in product_data:
            card = ProductCard(product_data, url)
            self.products_layout.addWidget(card)
            self.url_input.clear()


# Функция для получения информации о товаре с сайта
def product(url):
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
    VirtualEnvManager(mod='default',
                      libs=['selenium', 'webdriver-manager', 'fake-useragent', 'PyQt6', 'pyqtgraph', 'requests'])
    clear()

    # Запуск GUI приложения
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()