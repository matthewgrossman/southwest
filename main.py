from enum import Enum
from selenium import webdriver


class Fields(Enum):
    # input fields
    ConfirmationNum = 'confirmation_num'
    FirstName = 'first_name'
    LastName = 'last_name'

    # confirmation buttons
    RetrieveRes = 'retrieve_res'
    CheckIn = 'check_in'


config = {
    Fields.ConfirmationNum: 'SCHIH5',
    Fields.FirstName: 'Matthew',
    Fields.LastName: 'Grossman'
}

TEXT_TPL = '//buton[@name="{name}"]'
BUTTON_TPL = '//button[@role="submit" and contains(., "{inner_html}")]'
FIELD_XPATHS = {
    Fields.ConfirmationNum: TEXT_TPL.format(name="recordLocator"),
    Fields.FirstName: TEXT_TPL.format(name="firstName"),
    Fields.LastName: TEXT_TPL.format(name="lastName"),
    Fields.RetrieveRes: BUTTON_TPL.format(inner_html="Retrieve reservation"),
    Fields.CheckIn: BUTTON_TPL.format(inner_html="Check in"),
}


def check_in(driver: webdriver) -> None:
    driver.get("https://mobile.southwest.com/check-in")

    # insert all data required on the check-in page
    for field in [
        Fields.ConfirmationNum,
        Fields.FirstName,
        Fields.LastName,
    ]:
        xpath = FIELD_XPATHS[field]
        data = config[field]
        driver.find_element_by_xpath(xpath).send_keys(data)

    retrieve_res_field = driver.find_element_by_xpath(FIELD_XPATHS[Fields.RetrieveRes])
    retrieve_res_field.click()

    # after clicking "Retrieve Reservation", implicitly wait for confirm button
    check_in_field = driver.find_element_by_xpath(FIELD_XPATHS[Fields.CheckIn])
    check_in_field.click()


if __name__ == '__main__':
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(5)
    check_in(driver=driver)
