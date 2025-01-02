from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from typing import Protocol


class IWebDriver(Protocol):
    """Интерфейс для работы с веб-драйвером."""

    def get(self, url: str) -> None:
        pass

    def find_element(self, by: str, value: str) -> 'WebElement':
        pass

    def quit(self) -> None:
        pass

    def get_page_source(self) -> str:
        pass


class SeleniumDriver(IWebDriver):
    """Реализация IWebDriver с использованием Selenium."""

    def __init__(self, options: Options):
        self.driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            options=options,
        )

    def get(self, url: str) -> None:
        self.driver.get(url)

    def find_element(self, by: str, value: str) -> 'WebElement':
        return self.driver.find_element(by, value)

    def quit(self) -> None:
        self.driver.quit()

    def get_page_source(self) -> str:
        return self.driver.page_source
