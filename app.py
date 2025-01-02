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

    product_info = main_data[name]
    price_history = price_data.get(name, {})

    changes = {'card': 0, 'discount': 0, 'regular': 0}

    if price_history:
        dates = sorted(price_history.keys())
        if len(dates) >= 2:
            latest = price_history[dates[-1]]
            previous = price_history[dates[-2]]

            # Calculate changes for each price type
            changes = {
                'card': calculate_percentage_change(
                    previous['price_card_ozon'],
                    latest['price_card_ozon']
                ),
                'discount': calculate_percentage_change(
                    previous['price_discount'],
                    latest['price_discount']
                ),
                'regular': calculate_percentage_change(
                    previous['price'],
                    latest['price']
                )
            }

    return render_template('product.html',
                           name=name,
                           product=product_info,
                           changes=changes)




def calculate_percentage_change(old_value, new_value):
    try:

        old_value = float(str(old_value).replace('\u2009', '').replace(' ', '').replace('₽', ''))
        new_value = float(str(new_value).replace('\u2009', '').replace(' ', '').replace('₽', ''))
        if old_value == 0:
            return 0
        return ((new_value - old_value) / old_value) * 100
    except (ValueError, AttributeError) as e:
        print(f"Error converting price: {e}")  # Add logging
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
        'average_prices': calculate_average_prices(main_data),
        'price_history': aggregate_price_history(price_data),
        'price_trends': calculate_price_trends(price_data)
    }

    return jsonify(stats)


def calculate_average_prices(main_data):
    if not main_data:
        return {'card': 0, 'discount': 0, 'regular': 0}

    totals = {'card': 0, 'discount': 0, 'regular': 0}
    for product in main_data.values():
        totals['card'] += float(product['price_card_ozon'].replace('\u2009', '').replace(' ', '').replace('₽', ''))
        totals['discount'] += float(product['price_discount'].replace('\u2009', '').replace(' ', '').replace('₽', ''))
        totals['regular'] += float(product['price'].replace('\u2009', '').replace(' ', '').replace('₽', ''))

    count = len(main_data)
    return {k: v / count for k, v in totals.items()}


def aggregate_price_history(price_data):
    history = {}
    for product, dates in price_data.items():
        for date, prices in dates.items():
            if date not in history:
                history[date] = {
                    'card': [],
                    'discount': [],
                    'regular': []
                }
            history[date]['card'].append(
                float(prices['price_card_ozon'].replace('\u2009', '').replace(' ', '').replace('₽', '')))
            history[date]['discount'].append(
                float(prices['price_discount'].replace('\u2009', '').replace(' ', '').replace('₽', '')))
            history[date]['regular'].append(
                float(prices['price'].replace('\u2009', '').replace(' ', '').replace('₽', '')))

    return history


# File: app.py
def calculate_price_trends(price_data):
    trends = {}
    for product, dates in price_data.items():
        sorted_dates = sorted(dates.keys())
        if len(sorted_dates) >= 2:
            first_date = sorted_dates[0]
            last_date = sorted_dates[-1]

            first_prices = dates[first_date]
            last_prices = dates[last_date]

            trends[product] = {
                'card': calculate_percentage_change(
                    first_prices['price_card_ozon'],
                    last_prices['price_card_ozon']
                ),
                'discount': calculate_percentage_change(
                    first_prices['price_discount'],
                    last_prices['price_discount']
                ),
                'regular': calculate_percentage_change(
                    first_prices['price'],
                    last_prices['price']
                ),
                'period': {
                    'start': first_date,
                    'end': last_date
                }
            }

    return trends


@app.route('/get_stats_graph')
def get_stats_graph():
    price_data = read_json(PRICE_DATA_PATH)
    history = aggregate_price_history(price_data)

    plt.figure(figsize=(12, 6))
    dates = sorted(history.keys())

    # Рассчитываем средние цены для каждой даты
    avg_card = [sum(history[date]['card']) / len(history[date]['card']) if history[date]['card'] else 0 for date in
                dates]
    avg_discount = [sum(history[date]['discount']) / len(history[date]['discount']) if history[date]['discount'] else 0
                    for date in dates]
    avg_regular = [sum(history[date]['regular']) / len(history[date]['regular']) if history[date]['regular'] else 0 for
                   date in dates]

    plt.plot(dates, avg_card, label='Средняя цена с Ozon Card', marker='o')
    plt.plot(dates, avg_discount, label='Средняя цена со скидкой', marker='s')
    plt.plot(dates, avg_regular, label='Средняя обычная цена', marker='^')

    plt.xticks(rotation=45)
    plt.xlabel('Дата')
    plt.ylabel('Цена (₽)')
    plt.title('История средних цен всех товаров')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    plt.close()

    graph_url = base64.b64encode(img.getvalue()).decode()
    return jsonify({'success': True, 'graph': graph_url})

if __name__ == '__main__':
    app.run(debug=True)