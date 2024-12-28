from gui import PriceTrackerWorker, ProductCard
from moduls.ParserJson import *
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QPushButton, QLineEdit, QLabel,
                           QScrollArea)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ozon Price Tracker")
        self.resize(1000, 800)
        self.json_parser = JsonParser()

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
        """Загрузка существующих товаров из JSON"""
        products = self.json_parser.get_all_products()
        for product_name, product_data in products.items():
            product_data['name'] = product_name
            card = ProductCard(product_data, "")  # URL можно хранить в JSON
            self.products_layout.addWidget(card)

    def add_product(self):
        url = self.url_input.text().strip()
        if not url:
            return

        # Показываем индикатор загрузки
        loading_label = QLabel("Загрузка...")
        self.products_layout.addWidget(loading_label)

        # Запускаем получение данных в отдельном потоке
        self.worker = PriceTrackerWorker(url, self.product_func)
        self.worker.finished.connect(
            lambda result: self.on_product_loaded(result, loading_label, url)
        )
        self.worker.start()

    def on_product_loaded(self, product_data, loading_label, url):
        loading_label.deleteLater()
        if 'error' not in product_data:
            card = ProductCard(product_data, url)
            self.products_layout.addWidget(card)
            self.url_input.clear()