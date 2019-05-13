import datetime
import time
from datetime import timezone
from typing import Any
from typing import Dict
from typing import List
from typing import NamedTuple

import requests

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


class SouthwestAPI:
    CHECK_IN_TIMEDELTA = datetime.timedelta(days=1)
    ROOT_URL = "https://mobile.southwest.com/api/mobile-air-{verb}/v1/mobile-air-{verb}/page/{path}"
    CHECK_IN_URL = ROOT_URL.format(verb="operations", path='check-in')
    VIEW_RESERVATION_URL = ROOT_URL.format(verb="booking", path='view-reservation')
    SW_API_KEY = "l7xx0a43088fe6254712b10787646d1b298e"

    def __init__(self, confirmation_num: str, first_name: str, last_name: str) -> None:

        self._url_args = "/{confirmation_num}?first-name={first_name}&last-name={last_name}".format(
            confirmation_num=confirmation_num,
            first_name=first_name,
            last_name=last_name
        )
        self._view_reservation_url = self.VIEW_RESERVATION_URL + self._url_args
        self._check_in_url = self.CHECK_IN_URL + self._url_args

    def _request(self, url: str) -> Dict[str, Any]:
        return requests.get(url, headers={'x-api-key': self.SW_API_KEY}).json()

    def get_reservation_info(self) -> List[FlightInfo]:
        data = self._request(self._view_reservation_url)
        flight_info_dicts = data['viewReservationViewPage']['shareDetails']['flightInfo']
        return [FlightInfo.from_flight_info_dict(fid) for fid in flight_info_dicts]

    def schedule(self) -> None:
        flight_infos = self.get_reservation_info()
        now = datetime.datetime.now(timezone.utc)
        next_flight = next(f for f in flight_infos if f.departure_dt > now)
        check_in_dt = next_flight.departure_dt - self.CHECK_IN_TIMEDELTA
        print(next_flight)
        print(f"Scheduling check-in for: {check_in_dt}")
        time.sleep((check_in_dt - now).total_seconds())
        self.check_in()

    @utils.retry(Exception)
    def check_in(self) -> None:
        self._request(self._check_in_url)
        pass


if __name__ == '__main__':
    config = {
        'confirmation_num': 'KXLIFL',
        'first_name': 'Leah',
        'last_name': 'Schatz'
    }

    sw_api = SouthwestAPI(**config)
    sw_api.schedule()
