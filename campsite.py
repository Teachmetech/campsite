import time
import requests
from datetime import datetime, timedelta


class Campsite:
    def __init__(
        self,
        camp_grounds: dict,
        dates: list[tuple],
        recreation_api_url: str = None,
        request_headers: dict = None,
        ntfy_url: str = "https://ntfy.sh",
        ntfy_topic: str = "campsite",
        infinite_run: bool = True,
        sleep_time: int = 60,
        debug: bool = False,
    ):
        if not recreation_api_url:
            self.recreation_api_url = "https://www.recreation.gov/api/camps/availability/campground/{}/month?start_date={}T00%3A00%3A00.000Z"
        if not request_headers:
            self.request_headers = {
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache, no-store, must-revalidate",
                "pragma": "no-cache",
                "referer": "https://www.recreation.gov/camping/campgrounds/10039845?tab=campsites",
                "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            }
        self.camp_grounds = camp_grounds
        self._parsed_camp_grounds = self._parse_campgrounds()
        self.dates = dates
        self.ntfy_url = ntfy_url
        self.ntfy_topic = ntfy_topic
        self.infinite_run = infinite_run
        self.sleep_time = sleep_time
        self.debug = debug

    def _parse_campgrounds(self):
        current_month = datetime.now().month
        current_year = datetime.now().year
        parsed_campgrounds = {}
        for camp_ground in self.camp_grounds:
            campsites = []
            r = requests.get(
                self.recreation_api_url.format(
                    self.camp_grounds[camp_ground],
                    f"{current_year}-0{current_month}-01",
                ),
                headers=self.request_headers,
            )
            response_json = r.json()
            for site in response_json["campsites"]:
                campsites.append(response_json["campsites"][site]["site"])
            parsed_campgrounds[camp_ground] = {
                self.camp_grounds[camp_ground]: {site: True for site in campsites}
            }
        return parsed_campgrounds

    def check_sites(self):
        infinite_run = True
        while infinite_run:
            for camp_ground in self._parsed_camp_grounds:
                campground_id = list(self._parsed_camp_grounds[camp_ground].keys())[0]
                for date in self.dates:
                    starting_date = date[0]
                    ending_date = date[1]
                    starting_date_month = starting_date.split("-")[1]
                    starting_date_year = starting_date.split("-")[0]
                    campsite_response = requests.get(
                        self.recreation_api_url.format(
                            campground_id,
                            f"{starting_date_year}-{starting_date_month}-01",
                        ),
                        headers=self.request_headers,
                    )
                    response_data = campsite_response.json()
                    for site in response_data["campsites"]:
                        human_readable_campsite = response_data["campsites"][site][
                            "site"
                        ]
                        if not self._parsed_camp_grounds[camp_ground][
                            campground_id
                        ].get(human_readable_campsite, False):
                            continue
                        availabilities = response_data["campsites"][site][
                            "availabilities"
                        ]
                        all_days_available = True
                        for single_date in self._daterange(starting_date, ending_date):
                            if availabilities.get(single_date) != "Available":
                                all_days_available = False
                                if self.debug:
                                    print(
                                        "no availabilities for",
                                        starting_date,
                                        ending_date,
                                        camp_ground,
                                        human_readable_campsite,
                                    )
                                break
                        if all_days_available:
                            if self.debug:
                                print(
                                    "!Availabilities for",
                                    starting_date,
                                    ending_date,
                                    camp_ground,
                                    human_readable_campsite,
                                )
                            self._send_ntfy_message(
                                starting_date,
                                ending_date,
                                camp_ground,
                                response_data["campsites"][site]["site"],
                            )
                            self._parsed_camp_grounds[camp_ground][campground_id][
                                human_readable_campsite
                            ] = False
            if self.infinite_run:
                if self.debug:
                    print("sleeping...")
                time.sleep(self.sleep_time)
            else:
                infinite_run = False

    def _daterange(self, start_date, end_date):
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        delta = end - start  # timedelta

        days = [
            (start + timedelta(days=i)).strftime("%Y-%m-%dT00:00:00Z")
            for i in range(delta.days + 1)
        ]
        return days

    def _send_ntfy_message(self, start_date, end_date, campground, site):
        if self.debug:
            print(
                f"Site {site} is available for reservation from {start_date} to {end_date} at {campground}"
            )
        requests.post(
            f"{self.ntfy_url}/{self.ntfy_topic}",
            data=f"Site {site} is available for reservation from {start_date} to {end_date} at {campground}",
        )
