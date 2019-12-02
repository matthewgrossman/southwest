import sched
import datetime
import time
from datetime import timezone
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple

import requests
from requests import Session

import utils


class FlightInfo(NamedTuple):
    title: str
    departure_dt: datetime.datetime
    arrival_dt: datetime.datetime

    @classmethod
    def from_flight_info_dict(cls, flight_info_dict: Dict[str, Any]) -> 'FlightInfo':
        departure_dt = datetime.datetime.fromisoformat(flight_info_dict['departureDateTime'])
        arrival_dt = datetime.datetime.fromisoformat(flight_info_dict['arrivalDateTime'])
        return cls(
            title=flight_info_dict['title'],
            departure_dt=departure_dt,
            arrival_dt=arrival_dt,
        )

    def __str__(self) -> str:
        return f"{self.title}, {self.departure_dt}, {self.arrival_dt}"


class CheckedInFlightInfo(NamedTuple):
    seat: str
    has_precheck: bool

    @classmethod
    def from_checked_in_flight_dict(cls, checked_in_flight_dict: Dict[str, Any]) -> 'CheckedInFlightInfo':
        flight = next(iter(checked_in_flight_dict['checkInConfirmationPage']['flights']))
        passenger = next(iter(flight['passengers']))
        seat = passenger["boardingGroup"] + passenger["boardingPosition"]
        return cls(
            seat=seat,
            has_precheck=passenger['hasPrecheck']
        )

    def __str__(self) -> str:
        precheck_str = 'with' if self.has_precheck else 'without'
        return f"Seat {self.seat}, {precheck_str} precheck"


class IneligibleToCheckinError(Exception):
    pass


class Errors:
    BEFORE_CHECKIN = 'ERROR__AIR_TRAVEL__BEFORE_CHECKIN_WINDOW'
    AIR_TRAVEL_NOT_OPEN = 'ERROR__AIR_TRAVEL__NOT_OPEN'
    RECORD_NOT_FOUND = 'ERROR__AIR_RESERVATION__RECORD_LOCATOR_NOT_FOUND'


class SouthwestAPI:
    CHECKIN_TIMEDELTA = datetime.timedelta(days=1)
    ROOT_URL = "https://mobile.southwest.com/api/mobile-air-{verb}/v1/mobile-air-{verb}/page/{path}"
    CHECKIN_URL = ROOT_URL.format(verb="operations", path='check-in')
    VIEW_RESERVATION_URL = ROOT_URL.format(verb="booking", path='view-reservation')
    SW_API_KEY = "l7xx0a43088fe6254712b10787646d1b298e"

    def __init__(self, confirmation_num: str, first_name: str, last_name: str) -> None:

        self._confirmation_num = confirmation_num
        self._first_name = first_name
        self._last_name = last_name

        self._url_args = f"/{confirmation_num}?first-name={first_name}&last-name={last_name}"
        self._checkin_post_url = self.CHECKIN_URL
        self._view_reservation_url = self.VIEW_RESERVATION_URL + self._url_args
        self._checkin_get_url = self.CHECKIN_URL + self._url_args

        self._req_session = Session()
        self._req_session.headers['x-api-key'] = self.SW_API_KEY

        self._scheduler = sched.scheduler(time.time)

    def get_reservation_info(self) -> List[FlightInfo]:
        resp = self._req_session.get(url=self._view_reservation_url)
        data = resp.json()
        if not resp.ok:
            if data.get('messageKey') in (Errors.RECORD_NOT_FOUND):
                raise Exception('Could not find flight information, please confirm name and confirmation number')
            raise Exception(f"Unknown error: {data}")

        flight_info_dicts = data['viewReservationViewPage']['shareDetails']['flightInfo']
        return [FlightInfo.from_flight_info_dict(fid) for fid in flight_info_dicts]

    def schedule(self) -> None:
        flight_infos = self.get_reservation_info()
        now = datetime.datetime.now(timezone.utc)
        next_flight = next(f for f in flight_infos if f.departure_dt > now)
        checkin_dt = next_flight.departure_dt - self.CHECKIN_TIMEDELTA
        print(next_flight)

        print(f"Scheduling check-in for: {checkin_dt}")
        self._scheduler.enterabs(checkin_dt.timestamp(), 1, self.checkin)
        self._scheduler.run()

    @utils.retry([IneligibleToCheckinError])
    def checkin(self) -> None:
        resp = self._checkin_get()
        data = resp.json()
        if not resp.ok:
            if data.get('messageKey') in (Errors.BEFORE_CHECKIN, Errors.AIR_TRAVEL_NOT_OPEN):
                raise IneligibleToCheckinError("Attempted checkin too early")
            raise Exception(f"Unknown error: {data}")

        check_in_token = data['checkInSessionToken']
        resp = self._checkin_post(check_in_token=check_in_token)
        if not resp.ok:
            raise Exception(f"Unknown error: {resp.json()}")
        print("\nSuccess!")

        checked_in_flight_info = CheckedInFlightInfo.from_checked_in_flight_dict(resp.json())
        print(checked_in_flight_info)

    def _checkin_get(self) -> requests.Response:
        return self._req_session.get(url=self._checkin_get_url)

    def _checkin_post(self, check_in_token: str) -> requests.Response:
        data = {
            'checkInSessionToken': check_in_token,
            'firstName': self._first_name,
            'lastName': self._last_name,
            'recordLocator': self._confirmation_num,
        }
        return self._req_session.post(url=self._checkin_post_url, json=data)


if __name__ == '__main__':
    config = {
        'confirmation_num': 'TKVCKG',
        'first_name': 'Matthew',
        'last_name': 'Grossman'
    }

    sw_api = SouthwestAPI(**config)
    sw_api.schedule()
