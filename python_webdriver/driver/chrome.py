from python_webdriver.driver.element import WebDriverElementLocator, WebDriverElementListLocator
from python_webdriver.driver.exceptions import (
    WebDriverException,
    WebDriverNotStartedException,
    WebDriverNotInstantiatedException,
    InvalidFileExtensionException
)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebElement, WebDriver
from loguru import logger
import base64
from pathlib import Path
from enum import Enum
from typing import Any
from datetime import datetime


class ChromeDriver:
    def __init__(
        self,
        driver_path:  str | Path,
        implicit_wait_seconds: int,
        max_retry_attempts: int,
        driver_label: str | None = None,
    ):
        """
        Classe Wrapper que envelopa a classe WebDriver do selenium para automações utilizando o navegador Google Chrome

        Args:
            driver_path:
                Caminho para o executável do navegador
            implicit_wait_seconds
                Tempo (segundos) em que o Webdriver irá esperar implicitamente até elementos estarem acessíveis ao driver.
            max_retry_attempts:
                Quantidade máxima de vezes que o Webdriver retenta acessar um elemento indisponível ou inexistente.
            driver_label:
                Label para identificar driver quando rodando mais de uma instância. Utilizado apenas em logs. Padrão é sem label.
        """
        self.driver_path = Path(driver_path)
        self.implicit_wait_seconds = implicit_wait_seconds
        self.max_retry_attempts: int = max_retry_attempts
        self._driver: WebDriver | None = None
        self._is_driver_started = False
        self._label = DriverLabel(driver_label)

    # ------------------------------------------------------------------------------------
    #                                       API Pública
    # ------------------------------------------------------------------------------------

    def is_driver_started(self) -> bool:
        """Retorna True se o Webdriver tiver sido inicializado, False caso contrário."""
        return self._is_driver_started

    def get_driver(self) -> WebDriver:
        """Retorna instância do WebDriver"""
        if self._driver:
            return self._driver
        raise WebDriverNotInstantiatedException(
            "ChromeDriver ainda não foi instanciado."
        )

    def start_driver(self, options: tuple[str, ...] = tuple()) -> WebDriver:
        """
        Inicia o navegador localizado em **self.driver_path** e retorna uma instância de WebDriver.
        Args:
            options:
                Tupla de opções
        Returns:
            Instância de WebDriver.
        """
        if not self.is_driver_started():
            logger.debug(
                f"{self._label}Iniciando ChromeDriver..."
            )
            opt = webdriver.ChromeOptions()
            opt.binary_location = str(self.driver_path)
            for o in options:
                opt.add_argument(o)
            self._driver = webdriver.Chrome(opt)
            self._is_driver_started = True
            self.implicitly_wait_for(self.implicit_wait_seconds)
        return self.get_driver()

    def quit_driver(self):
        if self.is_driver_started():
            logger.debug(f"{self._label}Fechando ChromeDriver...")
            self.get_driver().quit()
            self._is_driver_started = False

    def goto(self, url: str):
        self._check_webdriver_started()
        logger.debug(f"{self._label}Navegando para {url}...")
        self.get_driver().get(url)

    def find_element(self) -> WebDriverElementLocator:
        return WebDriverElementLocator(self.get_driver())

    def find_elements(self) -> WebDriverElementListLocator:
        return WebDriverElementListLocator(self.get_driver())

    def type(
        self,
        element: WebElement,
        text: str,
    ) -> WebElement:
        self._check_webdriver_started()
        element.send_keys(text)
        return element

    def clear(
        self, element: WebElement
    ) -> WebElement:
        self._check_webdriver_started()
        logger.debug(f"{self._label}Limpando o elemento {element}...")
        element.clear()
        return element

    def type_and_enter(
        self,
        element: WebElement,
        text: str,
    ) -> WebElement:
        element = self.type(element, text)
        logger.debug(f"{self._label}Apertando botão Enter...")
        element.send_keys(Keys.ENTER)
        return element

    def click(
        self,
        element: WebElement,
    ) -> WebElement:
        self._check_webdriver_started()
        logger.debug(f"{self._label}Clicando no elemento {element}...")
        element.click()
        return element

    def scroll_element_into_view(self, element: WebElement) -> WebElement:
        self._check_webdriver_started()
        logger.debug(f"{self._label}Rolando até o elemento: {element}")
        self.get_driver().execute_script("arguments[0].scrollIntoView();", element)
        return element

    def implicitly_wait_for(self, seconds: float) -> None:
        logger.debug(
            f"{self._label}Configurando driver para aguardar implicitamente por {seconds} segundo(s)..."
        )
        self.get_driver().implicitly_wait(seconds)

    def page_to_pdf(
        self,
        file_path: str | Path,
        file_name: str | None = None,
        hide_elements: tuple[str, ...] = tuple(),
        options: dict[str, Any] = {}
    ) -> bytes:
        """
        Renderiza a página atual do navegador como PDF e salva no caminho especificado em *file_path*.

        Utiliza o comando *Page.printToPDF* do Chrome DevTools Protocol (CDP) para gerar o PDF, portanto é
        compatível apenas com o Chrome.

        Args:
            file_path (str): Caminho completo do diretório de destino (sem o nome do arquivo).
                O diretório é criado automaticamente, caso não exista.
            file_name:
                Nome do arquivo, caso queira dar um nome específico. O nome padrão é o timestamp atual (formato "%Y%m%d_%H%M%S.%f")
            hide_elements:
                Tupla com seletores CSS dos elementos a esconder na página, para que não saiam no PDF.
            options:
                Dicionário com opções passadas ao método Page.printToPDF.
                @see https://chromedevtools.github.io/devtools-protocol/tot/Page/#method-printToPDF para a lista de opções.

        Returns:
            Bytes do arquivo PDF escrito.

        Raises:
            WebDriverNotStartedException: Se o WebDriver não foi iniciado.
            OSError: Se não for possível criar o diretório ou gravar o arquivo.
            InvalidFileExtensionException caso a extensão do arquivo em *file_path* não for ".pdf".
            WebDriverException caso haja alguma falha na execução do comando Page.printToPDF.
        """
        self._check_webdriver_started()

        p = Path(file_path) if isinstance(file_path, str) else file_path

        if file_name:
            f = Path(file_name)
            expected = [".pdf", ".PDF"]
            if f.suffix not in expected:
                raise InvalidFileExtensionException(path=f, expected=expected, received=f.suffix)
        else:
            f = Path(f"{datetime.now().strftime("%Y%m%d_%H%M%S.%f")}.pdf")


        pdf_path = p / f

        logger.debug(f"Imprimindo PDF da página no caminho: {p}")

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

    def save_screenshot_page(self, file_dir: str) -> None:
        self._check_webdriver_started()
        path = Path(f"{file_dir}/{timestamp_as_file_name('png')}")
        path.parent.mkdir(parents=True, exist_ok=True)
        result = self.get_driver().save_screenshot(path)
        if result:
            logger.debug(f"Captura de tela sava no caminho: {path}")
        else:
            logger.error(f"Falha ao salvar captura de tela no caminho: {path}")

    def enable_network_throttling(
        self,
        throttling_profile: NetworkThrottlingProfile,
    ):
        logger.debug(
            f"Habilitando limitação de rede com perfil: {throttling_profile.name}"
        )
        self.get_driver().execute_cdp_cmd("Network.enable", {})
        self.get_driver().execute_cdp_cmd(
            "Network.emulateNetworkConditions", throttling_profile.value
        )

    # ------------------------------------------------------------------------------------
    #                                       API Interna
    # ------------------------------------------------------------------------------------
    

    def _check_webdriver_started(self) -> None:
        """Levanta WebDriverNotStartedException caso o Webdriver não tenha sido inicializado.
        :return:
        """
        if self.get_driver() is None or not self.is_driver_started():
            raise WebDriverNotStartedException("ChromeDriver ainda não foi iniciado.")


# ------------------------------------------------------------------------------------
#                                          Outras Classes
# ------------------------------------------------------------------------------------


class DriverLabel:
    """Label para identificação de drivers quando utilizando múltiplas instâncias. Usado apenas para logging."""
    def __init__(self, label: str | None = None):
        self.label = label

    def __repr__(self) -> str:
        return '' if not self.label else f'({self.label}) '


# ------------------------------------------------------------------------------------
#                                              Enums
# ------------------------------------------------------------------------------------


class NetworkThrottlingProfile(Enum):
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


# ------------------------------------------------------------------------------------
#                                         Exceptions
# ------------------------------------------------------------------------------------


class IncompatibleBrowserException(Exception):
    pass
