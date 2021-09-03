import time
from enum import auto
from enum import Enum

from selenium.webdriver.remote.webelement import WebElement
from seleniumwire import webdriver

from utils import UnableToGetBrowserHeaders


VIEW_RESERVATION_URL = "https://mobile.southwest.com/view-reservation"
CHECK_IN_URL = "https://mobile.southwest.com/check-in"
URL_PATH = "api/mobile-air-operations/v1/mobile-air-operations/page/check-in"
CHECK_IN_XHR_URL = "https://mobile.southwest.com/api/mobile-air-operations/v1/mobile-air-operations/page/check-in"


class Fields(Enum):
    # input fields
    ConfirmationNum = auto()
    FirstName = auto()
    LastName = auto()

    # confirmation buttons
    RetrieveRes = auto()
    CheckIn = auto()
    Success = auto()

    # date fields
    DepartingDate = auto()
    DepartingTime = auto()
    DepartingPeriod = auto()
    ReturningDate = auto()
    ReturningTime = auto()
    ReturningPeriod = auto()


TEXT_TPL = '//input[@name="{name}"]'
BUTTON_TPL = '//button[@role="submit" and contains(., "{inner_html}")]'

FIELD_XPATHS = {
    Fields.ConfirmationNum: TEXT_TPL.format(name="recordLocator"),
    Fields.FirstName: TEXT_TPL.format(name="firstName"),
    Fields.LastName: TEXT_TPL.format(name="lastName"),
    Fields.RetrieveRes: BUTTON_TPL.format(inner_html="Retrieve reservation"),
    Fields.CheckIn: BUTTON_TPL.format(inner_html="Check in"),
    Fields.Success: "//div[contains(@class, 'swa-message success')]",
}


class SouthwestBrowser:
    def __init__(self, confirmation_num: str, first_name: str, last_name: str) -> None:
        self._config = {
            Fields.ConfirmationNum: confirmation_num,
            Fields.FirstName: first_name,
            Fields.LastName: last_name,
        }
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('headless')
        chrome_options.add_argument("--ignore-ssl-errors=yes")
        chrome_options.add_argument("--ignore-certificate-errors")
        self._driver: webdriver = webdriver.Chrome(options=chrome_options)
        self._driver.implicitly_wait(5)

    def _get_element(self, field: Fields) -> WebElement:
        return self._driver.find_element_by_xpath(FIELD_XPATHS[field])

    def checkin(self) -> None:
        self._driver.get(CHECK_IN_URL)

        for field in [
            Fields.ConfirmationNum,
            Fields.FirstName,
            Fields.LastName,
        ]:
            element = self._get_element(field)
            element.send_keys(self._config[field])

        self._get_element(Fields.RetrieveRes).click()
        time.sleep(20)
        self._get_element(Fields.CheckIn).click()
        self._get_element(Fields.Success)
        check_in_req = next(
            (r for r in self._driver.requests if r.url == CHECK_IN_XHR_URL), None
        )
        if check_in_req is None:
            raise UnableToGetBrowserHeaders("error getting the headers")
        breakpoint()

    def get_browser_headers(self) -> dict[str, str]:
        self._driver.get(CHECK_IN_URL)

        for field in [
            Fields.ConfirmationNum,
            Fields.FirstName,
            Fields.LastName,
        ]:
            element = self._get_element(field)
            element.send_keys(self._config[field])

        self._get_element(Fields.RetrieveRes).click()

        # implicitly wait for checkin field
        self._get_element(Fields.CheckIn)
        check_in_req = next(
            (r for r in self._driver.requests if URL_PATH in r.url), None
        )
        if check_in_req is None:
            raise UnableToGetBrowserHeaders("error getting the headers")

        return dict(check_in_req.headers)
