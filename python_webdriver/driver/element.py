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

    def get_all_elements(self) -> list[WebElement]:
        return self._driver.find_elements(by=self.locator[0], value=self.locator[1])


class WebDriverElementLocator:
    def __init__(self, driver: WebDriver, context: WebElement | None = None):
        self._driver = driver
        self.context = context

    def by_attribute(self, attr_name: str, attr_value: str) -> WebDriverElement:
        return WebDriverElement(
            locator=(By.XPATH, f'//*[@{attr_name}="{attr_value}"]'), driver=self._driver
        )

    def by_tag(self, tag_name: str) -> WebDriverElement:
        return WebDriverElement(
            locator=(By.TAG_NAME, tag_name), driver=self._driver
        )

    def by_id(self, element_id: str) -> WebDriverElement:
        return WebDriverElement(
            locator=(By.ID, element_id), driver=self._driver
        )

    def by_class(self, class_name: str):
        return WebDriverElement(
            locator=(By.CLASS_NAME, class_name), driver=self._driver
        )

    def by_name(self, name: str):
        return WebDriverElement(
            locator=(By.NAME, name), driver=self._driver
        )

    def by_xpath(self, xpath: str) -> WebDriverElement:
        return WebDriverElement(
            locator=(By.XPATH, xpath), driver=self._driver
        )

    def by_link_text(self, text: str) -> WebDriverElement:
        return WebDriverElement(
            locator=(By.LINK_TEXT, text), driver=self._driver
        )

    def by_css_selector(self, selector: str) -> WebDriverElement:
        return WebDriverElement(
            locator=(By.CSS_SELECTOR, selector), driver=self._driver
        )
