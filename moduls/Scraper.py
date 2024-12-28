from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from typing import Dict

from moduls.Driver import IWebDriver

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class OzonPriceScraper:
    def __init__(self, url: str, driver: 'IWebDriver'):
        self.url = url
        self.driver = driver

    def _wait_for_element(self, by: By, value: str, timeout: int = 3) -> 'WebElement':
        """Ожидает элемент на странице."""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((by, value)))

    def get_product_details(self) -> Dict[str, str]:
        """Извлекает название товара, цены: основную, без Ozon Карты и без скидки."""
        details = {
            "name": "Не найден",
            "image": "Не найдено",
            "price_card_ozon": "Не найден",
            "price_discount": "Не найден",
            "price": "Не найден",
        }
        try:
            logger.info(f"Открытие страницы: {self.url}")
            self.driver.get(self.url)

            # Извлечение названия товара
            try:
                product_name_element = self._wait_for_element(By.CSS_SELECTOR, "div[data-widget='webProductHeading'] h1.l4u_27")
                details["name"] = product_name_element.text.strip()
                logger.info(f"Название товара: {details['name']}")
            except Exception:
                logger.warning("Название товара не найдено.")

            # Извлечение картинки товара
            try:
                gallery_elements = self._wait_for_element(By.CSS_SELECTOR, "div[data-index] img", timeout=10)
                for element in gallery_elements:
                    src = element.get_attribute("src")
                    if "video" not in src:
                        details["image"] = src
                        logger.info(f"Ссылка на изображение товара: {details['product_image']}")
                        break
                if details["image"] == "Не найдено":
                    logger.warning("Изображение товара не найдено.")
            except Exception:
                logger.warning("Галерея изображений не найдена.")

            # Основная цена
            try:
                main_price_element = self._wait_for_element(By.CSS_SELECTOR, "span.tl3_27")
                details["price_card_ozon"] = main_price_element.text.strip()
                logger.info(f"Основная цена: {details['price_card_ozon']}")
            except Exception:
                logger.warning("Основная цена не найдена.")

            # Цена без Ozon Карты
            try:
                without_card_element = self.driver.find_element(By.CSS_SELECTOR, "span.l8t_27.tl8_27.u1l_27")
                details["price_discount"] = without_card_element.text.strip()
                logger.info(f"Цена без Ozon Карты: {details['price_discount']}")
            except Exception:
                logger.warning("Цена без Ozon Карты не найдена.")

            # Цена без скидки
            try:
                without_discount_element = self.driver.find_element(By.CSS_SELECTOR, "span.t7l_27.t8l_27.t6l_27.lt8_27")
                details["price"] = without_discount_element.text.strip()
                logger.info(f"Цена без скидки: {details['price']}")
            except Exception:
                logger.warning("Цена без скидки не найдена.")

        except Exception as e:
            logger.error(f"Ошибка при обработке страницы: {e}")

            # Сохранение HTML для отладки
            html = self.driver.get_page_source()
            with open("page_source.html", "w", encoding="utf-8") as file:
                file.write(html)
            logger.info("HTML страницы сохранён в файл page_source.html")
            raise
        finally:
            self.driver.quit()

        return details
