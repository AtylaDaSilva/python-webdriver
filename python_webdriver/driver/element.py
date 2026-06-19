from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as conditions


class WebDriverElementLocator:
    def __init__(self, driver: WebDriver, context: WebElement | None = None):
        self.driver = driver
        self.context = context

    def by_attribute(self, attr_name: str, attr_value: str) -> WebElement:
        if self.context:
            return self.context.find_element(by=By.XPATH, value=f'//*[@{attr_name}="{attr_value}"]')
        return self.driver.find_element(by=By.XPATH, value=f'//*[@{attr_name}="{attr_value}"]')

    def by_tag(self, tag_name: str) -> WebElement:
        if self.context:
            return self.context.find_element(by=By.XPATH, value=f'//{tag_name}')
        return self.driver.find_element(by=By.XPATH, value=f'//{tag_name}')

    def by_id(self, id: str):
        if self.context:
            return self.context.find_element(by=By.ID, value=id)
        return self.by_attribute(attr_name="id", attr_value=id)

    def by_class(self, class_name: str):
        if self.context:
            return self.context.find_element(by=By.CLASS_NAME, value=class_name)
        return self.by_attribute(attr_name="class", attr_value=class_name)

    def by_xpath(self, xpath: str):
        return self.driver.find_element(by=By.XPATH, value=xpath)


class WebDriverElementListLocator(WebDriverElementLocator):

    def by_attribute(self, attr_name: str, attr_value: str) -> list[WebElement]:
        if self.context:
            return self.context.find_elements(by=By.XPATH, value=f'//*[@{attr_name}="{attr_value}"]')
        return self.driver.find_elements(by=By.XPATH, value=f'//*[@{attr_name}="{attr_value}"]')

    def by_tag(self, tag_name: str) -> list[WebElement]:
        if self.context:
            return self.context.find_elements(by=By.XPATH, value=f'//{tag_name}')
        return self.driver.find_elements(by=By.XPATH, value=f'//{tag_name}')

class WebElementWait:
    def __init__(self, driver: WebDriver, element: WebElement, seconds_to_wait: int = 10):
        self._element = element
        self._driver = driver
        self._seconds_to_wait = seconds_to_wait

    def to_be_clickable(self) -> bool:
        wait = WebDriverWait(self._driver, self._seconds_to_wait)
        element = wait.until(conditions.element_to_be_clickable(self._element))
        return True if element else False

    def to_be_visible(self) -> bool:
        wait = WebDriverWait(self._driver, self._seconds_to_wait)
        element = wait.until(conditions.visibility_of(self._element))
        return True if element else False
