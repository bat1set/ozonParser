from moduls.utils import *
from moduls.ParserJson import *
from moduls.Driver import SeleniumDriver
from moduls.Scraper import OzonPriceScraper
from selenium.webdriver.edge.options import Options
from moduls.VirtualEnvManager import VirtualEnvManager


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
    VirtualEnvManager(mod='default', libs=['selenium', 'webdriver-manager', 'fake-useragent', ])
    clear()

    # Получение данных о товаре
    url = "https://ozon.ru/t/MnM2Ekp"
    product_details = product(url)
    clear()

    # Вывод результата
    for key, value in product_details.items():
        print(f"{key}: {value}")

    # Обработка и запись данных
    main_data_path = 'data_Json/main_data.json'
    price_data_path = 'data_Json/price_for_all_dates.json'

    # Форматируем данные для записи
    formatted_data = {
        product_details['name']: {
            'image': product_details['image'],
            'price_card_ozon': product_details['price_card_ozon'].replace(' ', '').replace('₽', '').strip(),
            'price_discount': product_details['price_discount'].replace(' ', '').replace('₽', '').strip(),
            'price': product_details['price'].replace(' ', '').replace('₽', '').strip()
        }
    }

    # Обрабатываем изменения и записываем в файлы
    process_changes(formatted_data, main_data_path, price_data_path)

    input("Нажмите Enter, чтобы закрыть...")
    clear()


if __name__ == "__main__":
    main()
