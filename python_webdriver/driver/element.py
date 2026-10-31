"""This file describes classes and objects meant for internal use only although they can be directly imported.
Use them at your own discretion."""

from selenium.webdriver.common.by import By, ByType
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebElement


class WebDriverElement:
    """A representation of a web page element."""

    def __init__(
        self,
        locator: tuple[ByType, str],
        driver: WebDriver,
        context: WebDriverElement | None = None,
    ):
        """
        Args:
            locator: Tuple containing the selector type (e.g., By.ID) and the seletor itself.
            driver: A Selenium WebDriver instance.
            context: Optional. Element search context. If provided, the element will be searched only inside the context of this parent element instead of the entire web page.
        """
        self.locator = locator
        self.context = context
        self._driver = driver

    def __repr__(self):
        return f"({self.locator[0]}) {self.locator[1]}"

    def get_element(self) -> WebElement:
        """Searches and returns the first corresponding element to `self.locator`.

        Returns:
            A Selenium WebElement object.
        """
        if self.context:
            return self.context.get_element().find_element(
                by=self.locator[0], value=self.locator[1]
            )
        return self._driver.find_element(by=self.locator[0], value=self.locator[1])

    def get_all_elements(self) -> list[WebElement]:
        """Searches and returns all corresponding elements to `self.locator`.

        Returns:
            A list of Selenium WebElement object.
        """
        if self.context:
            return self.context.get_element().find_elements(
                by=self.locator[0], value=self.locator[1]
            )
        return self._driver.find_elements(by=self.locator[0], value=self.locator[1])

    def get_coordinates(self) -> WebDriverElementCoordinates:
        """Returns the X and Y coordinates of the element.

        Returns:
            A WebDriverElementCoordinates object with both X and Y properties.
        """
        return WebDriverElementCoordinates(coords=self.get_element().location)


class WebDriverElementLocator:
    """An element locator"""

    # TODO: Remove the context param from method definitions; it's a leftover from a previous version of the class.

    def __init__(self, driver: WebDriver, context: WebDriverElement | None = None):
        """
        Args:
            driver: A Selenium WebDriver instance.
            context: Optional. Element search context. If provided, the element will be searched only inside the context of this parent element instead of the entire web page.
        """
        self._driver = driver
        self.context = context

    def by_attribute(
        self, attr_name: str, attr_value: str, context: WebDriverElement | None = None
    ) -> WebDriverElement:
        """Locates an element by HTML attribute.

        Examples:

            >WebDriverElementLocator.by_attribute("href", "my-anchor")

            >WebDriverElementLocator.by_attribute("title", "my-title")

        Args:
            attr_name: Attribute name.
            attr_value: Attribute value.

        Returns:
            A WebDriverElement representation of the element.
        """
        return WebDriverElement(
            locator=(By.XPATH, f'//*[@{attr_name}="{attr_value}"]'),
            driver=self._driver,
            context=self.context,
        )

    def by_tag(
        self, tag_name: str, context: WebDriverElement | None = None
    ) -> WebDriverElement:
        """Locates an element by HTML tag.

        Args:
            tag_name: HTML tag name, e.g. "input", "a".

        Returns:
            A WebDriverElement representation of the element.
        """
        return WebDriverElement(
            locator=(By.TAG_NAME, tag_name), driver=self._driver, context=self.context
        )

    def by_id(
        self, element_id: str, context: WebDriverElement | None = None
    ) -> WebDriverElement:
        """Locates an element by its HTML id attribute.

        Args:
            element_id: Element id.

        Returns:
            A WebDriverElement representation of the element.
        """
        return WebDriverElement(
            locator=(By.ID, element_id), driver=self._driver, context=self.context
        )

    def by_class(self, class_name: str, context: WebDriverElement | None = None):
        """Locates an element by its HTML class attribute.

        Args:
            class_name: Element class

        Returns:
            A WebDriverElement representation of the element.
        """
        return WebDriverElement(
            locator=(By.CLASS_NAME, class_name),
            driver=self._driver,
            context=self.context,
        )

    def by_name(self, name: str, context: WebDriverElement | None = None):
        """Locates an element by its HTML name attribute.

        Args:
            name: Element name.

        Returns:
            A WebDriverElement representation of the element.
        """
        return WebDriverElement(
            locator=(By.NAME, name), driver=self._driver, context=self.context
        )

    def by_xpath(
        self, xpath: str, context: WebDriverElement | None = None
    ) -> WebDriverElement:
        """Locates an element by XPath.

        Args:
            xpath: Expressão XPath utilizada para localizar o elemento.

        Returns:
            A WebDriverElement representation of the element.
        """
        return WebDriverElement(
            locator=(By.XPATH, xpath), driver=self._driver, context=self.context
        )

    def by_link_text(
        self, text: str, context: WebDriverElement | None = None
    ) -> WebDriverElement:
        """Locates an anchor HTML element (<a>) by its inner text.

        Args:
            text: The text to search.

        Returns:
            A WebDriverElement representation of the element.
        """
        return WebDriverElement(
            locator=(By.LINK_TEXT, text), driver=self._driver, context=self.context
        )

    def by_css_selector(
        self, selector: str, context: WebDriverElement | None = None
    ) -> WebDriverElement:
        """Locates an element by its CSS selector.

        Args:
            selector: The CSS selector.

        Returns:
            A WebDriverElement representation of the element.
        """
        return WebDriverElement(
            locator=(By.CSS_SELECTOR, selector),
            driver=self._driver,
            context=self.context,
        )


class WebDriverElementCoordinates:
    """Represents an element's X and Y coordinates inside the web page.

    Attributes:
        x: Horizontal coords of the element, in pixels.
        y: Vertical coords of the element, in pixels.
    """

    def __init__(self, coords: dict[str, int]):
        """
        Args:
            coords: A dictionary containing both "x" and "y" keys.

        Example:
            >WebDriverElementCoordinates({"x": 42, "y": 0})
        """
        self.x, self.y = coords.values()
