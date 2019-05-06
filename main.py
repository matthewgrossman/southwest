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


config = {
    Fields.ConfirmationNum: 'SCHIH5',
    Fields.FirstName: 'Matthew',
    Fields.LastName: 'Grossman'
}


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


def check_in(driver: webdriver) -> None:
    driver.get(URL)

    # insert all data required on the check-in page
    for field in [
        Fields.ConfirmationNum,
        Fields.FirstName,
        Fields.LastName,
    ]:
        xpath = FIELD_XPATHS[field]
        data = config[field]
        driver.find_element_by_xpath(xpath).send_keys(data)

    driver.find_element_by_xpath(FIELD_XPATHS[Fields.RetrieveRes]).click()

    # after clicking "Retrieve Reservation", implicitly wait for confirm button
    driver.find_element_by_xpath(FIELD_XPATHS[Fields.CheckIn]).click()


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    check_in(driver=driver)
