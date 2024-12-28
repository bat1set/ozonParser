from gui import StatsWindow
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtCore import QUrl

import json

import requests
from io import BytesIO


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
