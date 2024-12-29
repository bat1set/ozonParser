import json
from datetime import datetime


class JsonParser:
    def __init__(self):
        self.main_data_path = 'data_Json/main_data.json'
        self.price_history_path = 'data_Json/price_for_all_dates.json'

    def read_json(self, file_path):
        """Чтение JSON файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def write_json(self, data, file_path):
        """Запись в JSON файл"""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def update_product_data(self, product_data):
        """Обновление данных о товаре"""
        # Чтение существующих данных
        main_data = self.read_json(self.main_data_path)
        price_history = self.read_json(self.price_history_path)

        product_name = product_data['name']

        # Обновление основных данных
        main_data[product_name] = {
            'image': product_data['image'],
            'price_card_ozon': product_data['price_card_ozon'].replace(' ', '').replace('₽', '').strip(),
            'price_discount': product_data['price_discount'].replace(' ', '').replace('₽', '').strip(),
            'price': product_data['price'].replace(' ', '').replace('₽', '').strip()
        }

        # Обновление истории цен
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        if product_name not in price_history:
            price_history[product_name] = {}

        price_history[product_name][current_time] = {
            'price_card_ozon': main_data[product_name]['price_card_ozon'],
            'price_discount': main_data[product_name]['price_discount'],
            'price': main_data[product_name]['price']
        }

        # Сохранение обновленных данных
        self.write_json(main_data, self.main_data_path)
        self.write_json(price_history, self.price_history_path)

        return main_data[product_name]

    def get_product_history(self, product_name):
        """Получение истории цен товара"""
        price_history = self.read_json(self.price_history_path)
        return price_history.get(product_name, {})

    def get_all_products(self):
        """Получение всех отслеживаемых товаров"""
        return self.read_json(self.main_data_path)