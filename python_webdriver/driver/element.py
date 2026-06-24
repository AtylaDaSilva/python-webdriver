from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebElement


class WebDriverElement:
    def __init__(self, locator: tuple[ByType, str], driver: WebDriver):
        self.locator = locator
        self._driver = driver

    def __repr__(self):
        return f"({self.locator[0]}) {self.locator[1]}"

    def get_element(self) -> WebElement:
        return self._driver.find_element(by=self.locator[0], value=self.locator[1])


class WebDriverElementLocator:
    def __init__(self, driver: WebDriver, context: WebElement | None = None):
        self._driver = driver
        self.context = context

    def by_attribute(self, attr_name: str, attr_value: str) -> WebDriverElement:
        return WebDriverElement(
            locator=(By.XPATH, f'//*[@{attr_name}="{attr_value}"]'), driver=self._driver
        )

    def by_tag(self, tag_name: str) -> WebElement:
        raise NotImplementedError
        if self.context:
            return self.context.find_element(by=By.XPATH, value=f'//{tag_name}')
        return self.driver.find_element(by=By.XPATH, value=f'//{tag_name}')

    def by_id(self, element_id: str) -> WebDriverElement:
        return WebDriverElement(
            locator=(By.ID, element_id), driver=self._driver
        )

    def by_class(self, class_name: str):
        raise NotImplementedError
        if self.context:
            return self.context.find_element(by=By.CLASS_NAME, value=class_name)
        return self.by_attribute(attr_name="class", attr_value=class_name)

    def by_xpath(self, xpath: str) -> WebDriverElement:
        return WebDriverElement(
            locator=(By.XPATH, xpath), driver=self._driver
        )


class WebDriverElementListLocator(WebDriverElementLocator):

    def by_attribute(self, attr_name: str, attr_value: str) -> list[WebElement]:
        raise NotImplementedError
        if self.context:
            return self.context.find_elements(by=By.XPATH, value=f'//*[@{attr_name}="{attr_value}"]')
        return self.driver.find_elements(by=By.XPATH, value=f'//*[@{attr_name}="{attr_value}"]')

    def by_tag(self, tag_name: str) -> list[WebElement]:
        raise NotImplementedError
        if self.context:
            return self.context.find_elements(by=By.XPATH, value=f'//{tag_name}')
        return self.driver.find_elements(by=By.XPATH, value=f'//{tag_name}')
