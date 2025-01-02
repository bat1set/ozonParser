from flask import Flask, render_template, request, jsonify, redirect, url_for

import os
from main import product as fetch_product
from moduls.ParserJson import read_json, write_json, process_changes
import matplotlib.pyplot as plt
import io
import base64


app = Flask(__name__)

# Настройка matplotlib для поддержки русского языка
plt.rcParams['font.family'] = 'DejaVu Sans'

# Пути к файлам данных
MAIN_DATA_PATH = 'data_Json/main_data.json'
PRICE_DATA_PATH = 'data_Json/price_for_all_dates.json'


def ensure_data_directory():
    """Проверка наличия директории для данных"""
    os.makedirs('data_Json', exist_ok=True)
    for file_path in [MAIN_DATA_PATH, PRICE_DATA_PATH]:
        if not os.path.exists(file_path):
            write_json(file_path, {})


@app.route('/')
def index():
    ensure_data_directory()
    main_data = read_json(MAIN_DATA_PATH)
    return render_template('index.html', products=main_data)


@app.route('/add_product', methods=['POST'])
def add_product():
    url = request.json.get('url')
    try:
        product_details = fetch_product(url)
        formatted_data = {
            product_details['name']: {
                'url': url,  # Сохраняем URL для будущих обновлений
                'image': product_details['image'],
                'price_card_ozon': product_details['price_card_ozon'].replace(' ', '').replace('₽', '').strip(),
                'price_discount': product_details['price_discount'].replace(' ', '').replace('₽', '').strip(),
                'price': product_details['price'].replace(' ', '').replace('₽', '').strip()
            }
        }
        process_changes(formatted_data, MAIN_DATA_PATH, PRICE_DATA_PATH)
        return jsonify({'success': True, 'data': formatted_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/product/<name>')
def product_page(name):
    main_data = read_json(MAIN_DATA_PATH)
    price_data = read_json(PRICE_DATA_PATH)

    if name not in main_data:
        return redirect(url_for('index'))

    if name in main_data:
        product_info = main_data[name]
        price_history = price_data.get(name, {})

        # Расчёт изменения цен
        if price_history:
            dates = sorted(price_history.keys())
            if len(dates) >= 2:
                latest = price_history[dates[-1]]
                previous = price_history[dates[-2]]

                # Расчёт процентных изменений
                changes = {
                    'card': calculate_percentage_change(
                        float(previous['price_card_ozon']),
                        float(latest['price_card_ozon'])
                    ),
                    'discount': calculate_percentage_change(
                        float(previous['price_discount']),
                        float(latest['price_discount'])
                    ),
                    'regular': calculate_percentage_change(
                        float(previous['price']),
                        float(latest['price'])
                    )
                }
            else:
                changes = {'card': 0, 'discount': 0, 'regular': 0}
        else:
            changes = {'card': 0, 'discount': 0, 'regular': 0}

        return render_template('product.html',
                               name=name,
                               product=product_info,
                               changes=changes)
    return "Товар не найден", 404



def calculate_percentage_change(old_value, new_value):
    try:
        # Удаляем все не числовые символы и конвертируем в float
        old_value = float(old_value.replace('\u2009', '').replace(' ', ''))
        new_value = float(new_value.replace('\u2009', '').replace(' ', ''))
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100
    except (ValueError, AttributeError):
        return 0


@app.route('/update_product/<name>')
def update_product(name):
    main_data = read_json(MAIN_DATA_PATH)
    if name in main_data:
        url = main_data[name].get('url', "https://ozon.ru/t/MnM2Ekp")
        product_details = fetch_product(url)
        formatted_data = {
            name: {
                'url': url,
                'image': product_details['image'],
                'price_card_ozon': product_details['price_card_ozon'].replace(' ', '').replace('₽', '').strip(),
                'price_discount': product_details['price_discount'].replace(' ', '').replace('₽', '').strip(),
                'price': product_details['price'].replace(' ', '').replace('₽', '').strip()
            }
        }
        process_changes(formatted_data, MAIN_DATA_PATH, PRICE_DATA_PATH)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Товар не найден'})


@app.route('/get_price_history/<name>')
def get_price_history(name):
    price_data = read_json(PRICE_DATA_PATH)
    if name in price_data:
        plt.figure(figsize=(10, 6))
        dates = sorted(price_data[name].keys())

        card_prices = [float(price_data[name][date]['price_card_ozon']) for date in dates]
        discount_prices = [float(price_data[name][date]['price_discount']) for date in dates]
        regular_prices = [float(price_data[name][date]['price']) for date in dates]

        plt.plot(dates, card_prices, label='Цена с Ozon Card', marker='o')
        plt.plot(dates, discount_prices, label='Цена со скидкой', marker='s')
        plt.plot(dates, regular_prices, label='Обычная цена', marker='^')

        plt.xticks(rotation=45)
        plt.xlabel('Дата')
        plt.ylabel('Цена (₽)')
        plt.title(f'История цен - {name}')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()

        graph_url = base64.b64encode(img.getvalue()).decode()
        return jsonify({'success': True, 'graph': graph_url})

    return jsonify({'success': False, 'error': 'Товар не найден'})


@app.route('/delete_products', methods=['POST'])
def delete_products():
    products_to_delete = request.json.get('products', [])
    main_data = read_json(MAIN_DATA_PATH)
    price_data = read_json(PRICE_DATA_PATH)

    for product in products_to_delete:
        if product in main_data:
            del main_data[product]
        if product in price_data:
            del price_data[product]

    write_json(MAIN_DATA_PATH, main_data)
    write_json(PRICE_DATA_PATH, price_data)

    return jsonify({'success': True})


@app.route('/update_all_products')
def update_all_products():
    main_data = read_json(MAIN_DATA_PATH)
    for name, product_info in main_data.items():
        url = product_info.get('url', "https://ozon.ru/t/MnM2Ekp")
        product_details = fetch_product(url)
        formatted_data = {
            name: {
                'url': url,
                'image': product_details['image'],
                'price_card_ozon': product_details['price_card_ozon'].replace(' ', '').replace('₽', '').strip(),
                'price_discount': product_details['price_discount'].replace(' ', '').replace('₽', '').strip(),
                'price': product_details['price'].replace(' ', '').replace('₽', '').strip()
            }
        }
        process_changes(formatted_data, MAIN_DATA_PATH, PRICE_DATA_PATH)
    return jsonify({'success': True})


@app.route('/statistics')
def get_statistics():
    main_data = read_json(MAIN_DATA_PATH)
    price_data = read_json(PRICE_DATA_PATH)

    stats = {
        'total_products': len(main_data),
        'price_changes': {},
        'average_prices': {
            'card': 0,
            'discount': 0,
            'regular': 0
        }
    }

    # Вычисляем статистику
    for name, product in main_data.items():
        stats['average_prices']['card'] += float(product['price_card_ozon'].replace('\u2009', '').replace(' ', ''))
        stats['average_prices']['discount'] += float(product['price_discount'].replace('\u2009', '').replace(' ', ''))
        stats['average_prices']['regular'] += float(product['price'].replace('\u2009', '').replace(' ', ''))

    if stats['total_products'] > 0:
        for key in stats['average_prices']:
            stats['average_prices'][key] /= stats['total_products']

    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True)