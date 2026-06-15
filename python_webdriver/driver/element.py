from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement


class WebDriverElementLocator:
    def __init__(self, driver: WebDriver):
        self.driver = driver

    def by_attribute(self, attr_name: str, attr_value: str) -> WebElement:
        return self.driver.find_element(by=By.XPATH, value=f'//*[@{attr_name}="{attr_value}"]')

    def by_tag(self, tag_name: str) -> WebElement:
        return self.driver.find_element(by=By.XPATH, value=f'//{tag_name}')

    def by_id(self, id: str):
        return self.by_attribute(attr_name="id", attr_value=id)


class WebDriverElementListLocator(WebDriverElementLocator):

    def by_attribute(self, attr_name: str, attr_value: str) -> list[WebElement]:
        return self.driver.find_elements(by=By.XPATH, value=f'//*[@{attr_name}="{attr_value}"]')

    def by_tag(self, tag_name: str) -> list[WebElement]:
        return self.driver.find_elements(by=By.XPATH, value=f'//{tag_name}')
