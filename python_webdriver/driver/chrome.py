from python_webdriver.driver.element import (
    WebDriverElement,
    WebDriverElementLocator,
)
from python_webdriver.driver.exceptions import (
    WebDriverException,
    WebDriverNotStartedException,
    WebDriverNotInstantiatedException,
    InvalidFileExtensionException,
)
from python_webdriver.functions import retry_on_exception
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebElement, WebDriver
from selenium.webdriver import ActionChains
from loguru import logger
import base64
from pathlib import Path
from enum import Enum
from typing import Any
from datetime import datetime
from time import sleep


class ChromeDriver:
    def __init__(
        self,
        binary_path: (
            str | Path
        ) = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        label: str | None = None,
    ):
        """
        Thin wrapper class that provides some useful methods for creating automations using Selenium and Google Chrome.
        Other Chromium-based browsers may work but are not officially supported.

        Args:
            binary_path:
                Path to Google Chrome executable file (.exe). If not provided, the default installation directory of Chrome will be used.
            label:
                Driver label used only for logging. Useful when working with multiple drivers.
        """
        self.driver_path = Path(binary_path)
        self.options = ChromeDriverOptions()
        self._driver: WebDriver | None = None
        self._is_running = False
        self._label = DriverLabel(label)

    # ------------------------------------------------------------------------------------
    #                                       Public API
    # ------------------------------------------------------------------------------------

    def is_running(self) -> bool:
        """Returns True if the method *ChromeDriver::start* has been called, False otherwise."""
        return self._is_running

    def get_driver(self) -> WebDriver:
        """Returns instance of WebDriver. Useful for invoking Selenium methods directly.
        For the official reference, @see https://www.selenium.dev/documentation"""
        if self._driver:
            return self._driver
        raise WebDriverNotInstantiatedException(
            "ChromeDriver has not been instantiated yet."
        )

    def start(self) -> WebDriver:
        """
        Launches the browser located at **self.driver_path** and returns an instance of Selenium's WebDriver class.
        Consecutive calls of *ChromeDriver::start* only returns the existing instance of the WebDriver class until *ChromeDriver::quit* has been invoked.

        Returns:
            Instância de WebDriver.
        """
        if not self.is_running():
            logger.debug(f"{self._label}Iniciando ChromeDriver...")
            self.options.set_binary_location(self.driver_path)
            self._driver = webdriver.Chrome(self.options.get_options())
            self._is_running = True
        return self.get_driver()

    def quit(self):
        """Quits the browser along with any associated tabs

        Raises:
            WebDriverNotInstantiatedException: If ChromeDriver was never instantiated.
        """
        if self.is_running():
            logger.debug(f"{self._label}Fechando ChromeDriver...")
            self.get_driver().quit()
            self._is_running = False

    def get_options(self) -> webdriver.ChromeOptions:
        return self.options.get_options()

    def goto(self, url: str):
        """Navigates the browser to *url*

        Args:
            url: The URL address.

        Raises:
            WebDriverNotStartedException: If ChromeDriver::start was never invoked.
        """
        self._check_webdriver_started()
        logger.debug(f"{self._label}Navegando para {url}...")
        self.get_driver().get(url)

    def find_element(
        self, context: WebDriverElement | None = None
    ) -> WebDriverElementLocator:
        """Returns an element locator with several useful methods for finding elements in the current page.

        Args:
            context: Optional. An instance of WebDriverElement. If provided, the locator will look for elements only within the context, i.e. children, of this element instead of the whole web page.

        Returns:
            Instância de WebDriverElementLocator A locator class instance.

        Raises:
            WebDriverNotInstantiatedException: If ChromeDriver was never instantiated.
        """
        return WebDriverElementLocator(self.get_driver(), context)

    def type(
        self,
        element: WebDriverElement,
        text: str,
        max_retries: int = 10,
        timeout: float = 1,
    ):
        """Tries to type *text* into *element*.

        If for whatever reason an exception is raised during the process, retries up to *max_retries* times with a wait period of *timeout* seconds between retries.
        If the retries exceed *max_retries*, the exception will be re-raised.

        Args:
            element: Must be a tybeable element, else Selenium will raise ElementNotInteractableException (or equivalent).
            text: The text to type.
            max_retries: Maximum number of retries before re-raising the exception. Defaults to 10.
            timeout: Time interval (in seconds) between each retry. Defaults to 1.

        Raises:
            WebDriverNotStartedException: If *ChromeDriver::start* was never invoked.
        """
        self._check_webdriver_started()
        logger.debug(f"{self._label}Inserindo texto no elemento {element}...")

        def _action():
            el = element.get_element()
            el.send_keys(text)

        retry_on_exception(
            func=_action,
            max_attempts=max_retries,
            polling_seconds=timeout,
        )

    def clear(
        self, element: WebDriverElement, max_retries: int = 10, timeout: float = 1
    ):
        """Tries to clear any text from *element*.

        If for whatever reason an exception is raised during the process, retries up to *max_retries* times with a wait period of *timeout* seconds between retries.
        If the retries exceed *max_retries*, the exception will be re-raised.

        Args:
            element: Element to clear of text.
            max_retries: Maximum number of retries before re-raising the exception. Defaults to 10.
            timeout: Time interval (in seconds) between each retry. Defaults to 1.

        Raises:
            WebDriverNotStartedException: If *ChromeDriver::start* was never invoked.
        """
        self._check_webdriver_started()
        logger.debug(f"{self._label}Limpando o elemento {element}...")

        def _action():
            el = element.get_element()
            el.clear()

        retry_on_exception(
            func=_action,
            max_attempts=max_retries,
            polling_seconds=timeout,
        )

    def type_and_enter(
        self,
        element: WebDriverElement,
        text: str,
        max_retries: int = 10,
        timeout: float = 1,
    ):
        """Same as *ChromeDriver::type* but also presses the "Enter" key after the text is inserted.

        Args:
            element: Must be a tybeable element, else Selenium will raise ElementNotInteractableException (or equivalent).
            text: The text to type.
            max_retries: Maximum number of retries before re-raising the exception. Defaults to 10.
            timeout: Time interval (in seconds) between each retry. Defaults to 1.

        Raises:
            WebDriverNotStartedException: If *ChromeDriver::start* was never invoked.
        """
        self.type(element, text)
        logger.debug(f"{self._label}Apertando botão Enter...")

        def _action():
            element.get_element().send_keys(Keys.ENTER)

        retry_on_exception(
            func=_action,
            max_attempts=max_retries,
            polling_seconds=timeout,
        )

    def click(
        self, element: WebDriverElement, max_retries: int = 10, timeout: float = 1
    ):
        """Tries to click *element*.

        If for whatever reason an exception is raised during the process, retries up to *max_retries* times with a wait period of *timeout* seconds between retries.
        If the retries exceed *max_retries*, the exception will be re-raised.

        Args:
            element: The element to be clicked.
            max_retries: Maximum number of retries before re-raising the exception. Defaults to 10.
            timeout: Time interval (in seconds) between each retry. Defaults to 1.

        Raises:
            WebDriverNotStartedException: If *ChromeDriver::start* was never invoked.
        """
        self._check_webdriver_started()
        logger.debug(f"{self._label}Clicando no elemento {element}...")

        def _action():
            el: WebElement = element.get_element()
            el.click()

        retry_on_exception(
            func=_action,
            max_attempts=max_retries,
            polling_seconds=timeout,
        )

    def scroll_element_into_view(
        self, element: WebDriverElement, max_retries: int = 10, timeout: float = 1
    ):
        """Tries to scroll the web page until *element* is visible.

        If for whatever reason an exception is raised during the process, retries up to *max_retries* times with a wait period of *timeout* seconds between retries.
        If the retries exceed *max_retries*, the exception will be re-raised.

        Args:
            element: The element to be scrolled into view.
            max_retries: Maximum number of retries before re-raising the exception. Defaults to 10.
            timeout: Time interval (in seconds) between each retry. Defaults to 1.

        Raises:
            WebDriverNotStartedException: If *ChromeDriver::start* was never invoked.
        """
        self._check_webdriver_started()
        logger.debug(f"{self._label}Rolando até o elemento: {element}")

        def _action():
            self.get_driver().execute_script(
                "arguments[0].scrollIntoView();", element.get_element()
            )

        retry_on_exception(
            func=_action,
            max_attempts=max_retries,
            polling_seconds=timeout,
        )

    def drag_and_drop_by_offset(
        self,
        element: WebDriverElement,
        x_offset: int,
        y_offset: int,
        max_retries: int = 10,
        timeout: float = 1,
    ):
        """Tries to drag-and-drop an element by and X and Y offset.

        If for whatever reason an exception is raised during the process, retries up to *max_retries* times with a wait period of *timeout* seconds between retries.
        If the retries exceed *max_retries*, the exception will be re-raised.

        Args:
            element: Must be a draggable element, else Selenium will raise an exception.
            x_offset: Horizontal offset (in pixels) relative to the original position of *element*.
            y_offset: Vertical offset (in pixels) relative to the original position of *element*.
            max_retries: Maximum number of retries before re-raising the exception. Defaults to 10.
            timeout: Time interval (in seconds) between each retry. Defaults to 1.

        Raises:
            WebDriverNotStartedException: If *ChromeDriver::start* was never invoked.
        """
        self._check_webdriver_started()
        logger.debug(
            f"{self._label}Arrastando elemento {element} até os offsets X: {x_offset}, Y: {y_offset}..."
        )

        def _action():
            el: WebElement = element.get_element()
            action_chains = ActionChains(self.get_driver())
            (
                action_chains.drag_and_drop_by_offset(
                    el, xoffset=x_offset, yoffset=y_offset
                ).perform()
            )

        retry_on_exception(
            func=_action,
            max_attempts=max_retries,
            polling_seconds=timeout,
        )

    def explicit_wait(self, seconds: float):
        """Waits for *seconds*. Equivalent to *time.sleep* but with a layer of logging.

        Args:
            seconds: Time to wait for, in seconds.
        """
        logger.debug(
            f"{self._label}Aguardando explicitamente por {seconds} segundo(s)..."
        )
        sleep(seconds)

    def hide_elements(self, elements: tuple[str, ...]):
        """Synchronously hides elements in the current web page.

        Uses Javascript (`document.querySelectorAll`) to change the `display` attribute to *none*.
        Note that due to the nature of running Javascript code through Selenium, this method can fail silently, so make sure the element(s) are all loaded and visible before calling *ChromeDriver::hide_elements*.

        Args:
            elements: Tuple with the CSS selectors of the elements to hide.
        """
        for el in elements:
            self.get_driver().execute_script(
                f"document.querySelectorAll('{el}').forEach((el) => el.style.display = 'none')"
            )

    def page_to_pdf(
        self,
        file_path: str | Path,
        file_name: str | None = None,
        hide_elements: tuple[str, ...] = tuple(),
        options: dict[str, Any] = {},
    ) -> bytes:
        """
        Creates a PDF file from the current web page.

        Note: This method uses Google Chrome's `Page.printToPDF` to create the PDF file and may not work on other Chromium-based browsers.

        Args:
            file_path (str): Path (without the file name) to save the PDF file.
                The directory will be created if it does not exist.
            file_name:
                Optional. Name of the PDF file (with the `.pdf` extension). If not provided, the file name will be a timestamp of the creation time.
            hide_elements:
                Optional. A tuple of CSS selectors. Elements matching these selectors will be hidden from the web page before creating the PDF file.
            options:
                Dictionary with options to be passed to `Page.printToPDF`.
                For a full list of options, @see https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-printToPDF.

        Returns:
            Bytes object of the created file.

        Raises:
            WebDriverNotStartedException: If *ChromeDriver::start* was never invoked.
            OSError: If an error occurred during the creation of the directory or file.
            InvalidFileExtensionException If *file_name* does not have a *.pdf* extension.
            WebDriverException If an error occurred during the execution of the `Page.printToPDF` command.
        """
        self._check_webdriver_started()

        p = Path(file_path) if isinstance(file_path, str) else file_path

        if file_name:
            f = Path(file_name)
            expected = [".pdf", ".PDF"]
            if f.suffix not in expected:
                raise InvalidFileExtensionException(
                    path=f, expected=expected, received=f.suffix
                )
        else:
            f = Path(f"{datetime.now().strftime("%Y%m%d_%H%M%S.%f")}.pdf")

        pdf_path = p / f

        logger.debug(f"{self._label}Imprimindo PDF da página no caminho: {p}")

        # Create directory, if it does not exist
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # Inject CSS to hide elements so they don't appear in the PDF
        for selector in hide_elements:
            self.get_driver().execute_script(
                f"document.querySelectorAll('{selector}').forEach((el) => el.style.display = 'none')"
            )

        # Use CDP to render page as PDF
        pdf_data = self.get_driver().execute_cdp_cmd(
            cmd="Page.printToPDF",
            cmd_args=options,
        )

        if not pdf_data:
            raise WebDriverException("Failed to print page to PDF.")

        # Decode and save
        with open(pdf_path, "wb") as f:
            decoded_data = base64.b64decode(pdf_data["data"])
            f.write(decoded_data)

        return decoded_data

    def save_screenshot_page(self, file_dir: str) -> Path | None:
        """
        Takes a screenshot of the entire page and saves it to `file_dir`.

        Note: Make sure the web page is fully loaded before invoking this method, else some page elements may be missing from the screenshot.

        Args:
            file_dir (str): Directory (without the file name) to save the screenshot.
                The directory will be created if it does not exist.

        Returns:
            Path object of the screenshot (.png), or None if an *IOError* occurred during the creation of the screenshot.

        Raises:
            WebDriverNotStartedException: If *ChromeDriver::start* was never invoked.
            OSError: If an error occurred during the creation of `file_dir`.
        """
        self._check_webdriver_started()
        path = Path(f"{file_dir}/{datetime.now().strftime("%Y%m%d_%H%M%S.%f")}.png")
        path.parent.mkdir(parents=True, exist_ok=True)
        result = self.get_driver().save_screenshot(path)
        if result:
            logger.debug(f"{self._label}Captura de tela sava no caminho: {path}")
            return path
        else:
            logger.error(
                f"{self._label}Falha ao salvar captura de tela no caminho: {path}"
            )
            return None

    def enable_network_throttling(
        self,
        throttling_profile: ChromeNetworkThrottlingProfile,
    ):
        """Enables network throttling. Useful for emulating slower internet connections.

        Args:
            throttling_profile: A network throttlign profile.

        Raises:
            WebDriverNotInstantiatedException: If ChromeDriver was never instantiated.
        """
        logger.debug(
            f"{self._label}Habilitando limitação de rede com perfil: {throttling_profile.name}"
        )
        self.get_driver().execute_cdp_cmd("Network.enable", {})
        self.get_driver().execute_cdp_cmd(
            "Network.emulateNetworkConditions", throttling_profile.value
        )

    # ------------------------------------------------------------------------------------
    #                                       Internal API
    # ------------------------------------------------------------------------------------

    def _check_webdriver_started(self) -> None:
        """Raises WebDriverNotStartedException if the method `ChromeDriver::start` was not invoked at least once.
        :return:
        """
        if self.get_driver() is None or not self.is_running():
            raise WebDriverNotStartedException("ChromeDriver ainda não foi iniciado.")


# ------------------------------------------------------------------------------------
#                                          Helper Classes
# ------------------------------------------------------------------------------------


class DriverLabel:
    """Webdriver label used to differentiate multiple driver instances. Only used in logging."""

    def __init__(self, label: str | None = None):
        self.label = label

    def __repr__(self) -> str:
        return "" if not self.label else f"({self.label}) "


class ChromeDriverOptions:
    """Interface for easily setting options with webdriver.ChromeOptions"""

    def __init__(self) -> None:
        self.options = webdriver.ChromeOptions()

    def get_options(self) -> webdriver.ChromeOptions:
        return self.options

    def set_option(self, arg: str) -> None:
        """Sets an arbitrary Chromium option.
        For a full list of supported arguments, @see https://peter.sh/experiments/chromium-command-line-switches/

        Args:
            arg (str): Name of the argument. Example: --start-maximized
        """
        logger.debug(f"Setting Chrome option '{arg}'...")
        self.options.add_argument(arg)

    def set_experimental_option(
        self, name: str, value: str | int | dict[str, Any] | list[str]
    ) -> None:
        """Sets an arbitrary Chromium experimental option.

        Args:
            name (str): Name of the option. Example: "prefs"
            value (str | int | dict[str, Any] | list[str]): Option value
        """
        logger.debug(
            f"Setting experimental Chrome option '{name}' with the value(s) '{value}'"
        )
        self.options.add_experimental_option(name, value)

    def set_binary_location(self, path: str | Path) -> None:
        """Sets path to Chrome binary.

        Args:
            path (str | Path): Absolute path to Chrome executable.
        """
        p = Path(path) if isinstance(path, str) else path
        self.options.binary_location = str(p)

    def set_start_maximized(self) -> None:
        """Starts browser window maximized."""
        self.set_option("--start-maximized")

    def set_headless_mode(self) -> None:
        """Starts browser in headless mode, i.e., without a UI or display server dependencies."""
        self.set_option("--headless")

    def set_download_path(self, path: str | Path) -> None:
        """Sets the file download path to *path* and disables the "Save as" dialog.

        Args:
            path (str | Path): Absolute path to file download location. The directory will be created if it does not exist.
        """
        p = Path(path) if isinstance(path, str) else path
        p.mkdir(exist_ok=True)
        self.set_experimental_option(
            "prefs",
            {
                "download.default_directory": str(p),
                "download.prompt_for_download": False,  # no "Save as" dialog
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,  # avoids blocks on some file types
            },
        )


# ------------------------------------------------------------------------------------
#                                              Enums
# ------------------------------------------------------------------------------------


class ChromeNetworkThrottlingProfile(Enum):
    """Network throttling profiles to be used with `ChromeDriver::enable_network_throttling`"""

    OFFLINE = {
        "offline": True,
        "downloadThroughput": 0,
        "uploadThroughput": 0,
        "latency": 0,
    }
    SLOW_2G = {
        "offline": False,
        "downloadThroughput": 250 * 1024 / 8,
        "uploadThroughput": 50 * 1024 / 8,
        "latency": 2000,
    }
    CELLULAR_2G = {
        "offline": False,
        "downloadThroughput": 450 * 1024 / 8,
        "uploadThroughput": 150 * 1024 / 8,
        "latency": 300,
    }
    CELLULAR_3G = {
        "offline": False,
        "downloadThroughput": 750 * 1024 / 8,
        "uploadThroughput": 250 * 1024 / 8,
        "latency": 100,
    }
    CELLULAR_4G = {
        "offline": False,
        "downloadThroughput": 4 * 1024 * 1024 / 8,
        "uploadThroughput": 3 * 1024 * 1024 / 8,
        "latency": 20,
    }
