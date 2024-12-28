import datetime
import json
import os


# Функция для чтения данных из файла с обработкой ошибок
def read_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Ошибка: Невозможно декодировать JSON в файле {file_path}. Файл пуст или поврежден.")
            return {}
    return {}


# Функция для записи данных в файл
def write_json(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


# Функция для обработки изменений и записи их в оба файла
def process_changes(new_data, main_data_path, price_data_path):
    # Чтение текущих данных
    main_data = read_json(main_data_path)
    price_data = read_json(price_data_path)

    # Получаем текущую дату и время
    today_datetime = datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')

    # Обрабатываем данные и ищем изменения
    for key, new_values in new_data.items():
        if key in main_data:
            # Если данные изменились, добавляем новые данные в price_for_all_dates
            old_values = main_data[key]
            if new_values != old_values:
                # Добавляем новую запись с временем
                price_data.setdefault(key, {})
                price_data[key][today_datetime] = {
                    "price_card_ozon": old_values['price_card_ozon'],
                    "price_discount": old_values['price_discount'],
                    "price": old_values['price']
                }
                # Обновляем main_data новым значением
                main_data[key] = new_values
        else:
            # Если данных еще нет в main_data, добавляем новые данные
            main_data[key] = new_values
            price_data.setdefault(key, {})
            price_data[key][today_datetime] = {
                "price_card_ozon": new_values['price_card_ozon'],
                "price_discount": new_values['price_discount'],
                "price": new_values['price']
            }

    # Записываем обновленные данные в файлы
    write_json(main_data_path, main_data)
    write_json(price_data_path, price_data)