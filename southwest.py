import sys
import subprocess
import datetime
from enum import Enum, auto
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement


class Fields(Enum):
    # input fields
    ConfirmationNum = auto()
    FirstName = auto()
    LastName = auto()

    # confirmation buttons
    RetrieveRes = auto()
    CheckIn = auto()

    # date fields
    DepartingDate = auto()
    DepartingTime = auto()
    DepartingPeriod = auto()
    ReturningDate = auto()
    ReturningTime = auto()
    ReturningPeriod = auto()


# defined xpaths for each different element we need to find in-page
TEXT_TPL = '//input[@name="{name}"]'
BUTTON_TPL = '//button[@role="submit" and contains(., "{inner_html}")]'
DATETIME_TPL = "//div[contains(@class, 'trip-details--flight-status')]/*[{idx}]"
DATE_TPL = "//div[contains(@class, 'trip-details--flight-status')]/*[{idx}]//span[contains(@class,'flight-day')]"
TIME_TPL = "//div[contains(@class, 'trip-details--flight-status')]/*[{idx}]//div[contains(@class, 'flight-time--time')]/span[1]"
PERIOD_TPL = "//div[contains(@class, 'trip-details--flight-status')]/*[{idx}]//div[contains(@class, 'flight-time--time')]/span[2]"
FIELD_XPATHS = {
    Fields.ConfirmationNum: TEXT_TPL.format(name="recordLocator"),
    Fields.FirstName: TEXT_TPL.format(name="firstName"),
    Fields.LastName: TEXT_TPL.format(name="lastName"),
    Fields.RetrieveRes: BUTTON_TPL.format(inner_html="Retrieve reservation"),
    Fields.CheckIn: BUTTON_TPL.format(inner_html="Check in"),
    Fields.DepartingDate: DATE_TPL.format(idx=1),
    Fields.DepartingTime: TIME_TPL.format(idx=1),
    Fields.DepartingPeriod: TIME_TPL.format(idx=1),
    Fields.ReturningDate: DATE_TPL.format(idx=2),
    Fields.ReturningTime: TIME_TPL.format(idx=2),
    Fields.ReturningPeriod: PERIOD_TPL.format(idx=2),
}


CHECK_IN_URL = "https://mobile.southwest.com/check-in"
VIEW_RESERVATION_URL = "https://mobile.southwest.com/view-reservation"


class Southwest:

    def __init__(self, confirmation_num: str, first_name: str, last_name: str) -> None:
        self._config = {
            Fields.ConfirmationNum: confirmation_num,
            Fields.FirstName: first_name,
            Fields.LastName: last_name
        }
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('headless')
        self._driver: webdriver = webdriver.Chrome(options=chrome_options)
        self._driver.implicitly_wait(5)

    def _enter_configuration(self) -> None:
        # insert all data required on the check-in page
        for field in [
            Fields.ConfirmationNum,
            Fields.FirstName,
            Fields.LastName,
        ]:
            element = self._get_element(field)
            element.send_keys(self._config[field])

        self._get_element(Fields.RetrieveRes).click()

    def _get_element(self, field: Fields) -> WebElement:
        return self._driver.find_element_by_xpath(FIELD_XPATHS[field])

    def _parse_date_strings(self, date: str, time: str, period: str) -> datetime.datetime:
        """
        @date: "Thu, May 16, 2019"
        @time: "6:15"
        @period: "PM"
        """
        _, month_day, year = date.split(', ')
        return datetime.datetime.strptime(f"{month_day},{year},{time}{period}", "%b %d,%Y,%I:%M%p")

    def _schedule_check_in(self, flight_dt: datetime.datetime) -> None:
        check_in_cmd = " ".join([
            sys.argv[0],
            '--action',
            'check-in',
            '--confirmation-num',
            self._config[Fields.ConfirmationNum],
            '--first-name',
            self._config[Fields.FirstName],
            '--last-name',
            self._config[Fields.LastName]
        ])
        dt_str = flight_dt.strftime('%Y%m%d%H%M')
        import ipdb
        ipdb.set_trace()

        subprocess.run(['at', '-t', dt_str], input=check_in_cmd)

    def schedule(self) -> None:
        self._driver.get(VIEW_RESERVATION_URL)
        self._enter_configuration()

        departing_date = self._get_element(Fields.DepartingDate).text
        departing_time = self._get_element(Fields.DepartingTime).text
        departing_period = self._get_element(Fields.ReturningPeriod).text
        departing_dt = self._parse_date_strings(departing_date, departing_time, departing_period)

        self._schedule_check_in(flight_dt=departing_dt)

    def check_in(self) -> None:
        self._driver.get(CHECK_IN_URL)
        self._enter_configuration()

        # after clicking "Retrieve Reservation", implicitly wait for confirm button
        self._get_element(Fields.CheckIn).click()
