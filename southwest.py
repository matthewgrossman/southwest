from enum import Enum, auto
from selenium import webdriver


class Fields(Enum):
    # input fields
    ConfirmationNum = auto()
    FirstName = auto()
    LastName = auto()

    # confirmation buttons
    RetrieveRes = auto()
    CheckIn = auto()


# defined xpaths for each different element we need to find in-page
TEXT_TPL = '//input[@name="{name}"]'
BUTTON_TPL = '//button[@role="submit" and contains(., "{inner_html}")]'
FIELD_XPATHS = {
    Fields.ConfirmationNum: TEXT_TPL.format(name="recordLocator"),
    Fields.FirstName: TEXT_TPL.format(name="firstName"),
    Fields.LastName: TEXT_TPL.format(name="lastName"),
    Fields.RetrieveRes: BUTTON_TPL.format(inner_html="Retrieve reservation"),
    Fields.CheckIn: BUTTON_TPL.format(inner_html="Check in"),
}


URL = "https://mobile.southwest.com/check-in"


class Southwest:

    def __init__(self, confirmation_num: str, first_name: str, last_name: str) -> None:
        self._config = {
            Fields.ConfirmationNum: confirmation_num,
            Fields.FirstName: first_name,
            Fields.LastName: last_name
        }
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('headless')
        self._driver = webdriver.Chrome(options=chrome_options)
        self._driver.implicitly_wait(5)

    def schedule(self):
        print("not yet implemented")
        pass

    def check_in(self) -> None:
        self._driver.get(URL)

        # insert all data required on the check-in page
        for field in [
            Fields.ConfirmationNum,
            Fields.FirstName,
            Fields.LastName,
        ]:
            xpath = FIELD_XPATHS[field]
            data = self._config[field]
            self._driver.find_element_by_xpath(xpath).send_keys(data)

        self._driver.find_element_by_xpath(FIELD_XPATHS[Fields.RetrieveRes]).click()

        # after clicking "Retrieve Reservation", implicitly wait for confirm button
        self._driver.find_element_by_xpath(FIELD_XPATHS[Fields.CheckIn]).click()
