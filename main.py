import os

from selenium.webdriver.edge.options import Options
from moduls.Driver import SeleniumDriver
from moduls.Scraper import OzonPriceScraper
from moduls.VirtualEnvManager import VirtualEnvManager

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    VirtualEnvManager(mod='default', libs=['selenium', 'webdriver-manager', 'fake-useragent',])
    clear()
    url = "https://ozon.ru/t/MnM2Ekp"

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

    # Получение данных о товаре
    product_details = scraper.get_product_details()
    clear()
    # Вывод результата
    for key, value in product_details.items():
        print(f"{key}: {value}")

    input("Нажмите Enter, чтобы закрыть...")
    clear()

if __name__ == "__main__":
    main()
