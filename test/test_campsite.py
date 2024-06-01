import unittest
from unittest.mock import patch, Mock
from datetime import datetime
import json
import sys
import os

# Add parent directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from campsite import Campsite


class TestCampsite(unittest.TestCase):

    def setUp(self):
        self.camp_grounds = {"june_lake": "232268"}
        self.dates = [("2024-06-13", "2024-06-16")]
        self.ntfy_url = "https://ntfy.sh"
        self.ntfy_topic = "campsite"
        self.infinite_run = False
        self.sleep_time = 1  # Reduced for faster tests
        self.campsite = Campsite(
            self.camp_grounds,
            self.dates,
            ntfy_url=self.ntfy_url,
            ntfy_topic=self.ntfy_topic,
            infinite_run=self.infinite_run,
            sleep_time=self.sleep_time,
        )
        self.test_file = "test example files/rec_response.json"
        with open(self.test_file, "r") as f:
            self.example_response = json.load(f)

    @patch("requests.get")
    @patch("requests.post")
    def test_parse_campgrounds(self, mock_post, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = self.example_response
        mock_get.return_value = mock_response

        parsed_campgrounds = self.campsite._parse_campgrounds()
        expected_campgrounds = {
            "june_lake": {
                "232268": {
                    "018": True,
                    "015": True,
                    "005": True,
                    "013": True,
                    "T004": True,
                    "009": True,
                    "004": True,
                    "T002": True,
                    "014": True,
                    "T005": True,
                    "007": True,
                    "001": True,
                    "010": True,
                    "019": True,
                    "012": True,
                    "022": True,
                    "017": True,
                    "002": True,
                    "020": True,
                    "011": True,
                    "008": True,
                    "006": True,
                    "T006": True,
                    "021": True,
                    "T003": True,
                    "T001": True,
                    "003": True,
                    "016": True,
                }
            }
        }

        self.assertEqual(parsed_campgrounds, expected_campgrounds)

    @patch("requests.get")
    @patch("requests.post")
    def test_check_sites(self, mock_post, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = self.example_response
        mock_get.return_value = mock_response

        with patch.object(self.campsite, "_send_ntfy_message") as mock_send_message:
            self.campsite._parsed_camp_grounds = {
                "june_lake": {
                    "232268": {
                        "018": True,
                        "015": True,
                        "005": True,
                        "013": True,
                        "T004": True,
                        "009": True,
                        "004": True,
                        "T002": True,
                        "014": True,
                        "T005": True,
                        "007": True,
                        "001": True,
                        "010": True,
                        "019": True,
                        "012": True,
                        "022": True,
                        "017": True,
                        "002": True,
                        "020": True,
                        "011": True,
                        "008": True,
                        "006": True,
                        "T006": True,
                        "021": True,
                        "T003": True,
                        "T001": True,
                        "003": True,
                        "016": True,
                    }
                }
            }
            self.campsite.check_sites()
            mock_send_message.assert_called_once_with(
                "2024-06-13", "2024-06-16", "june_lake", "018"
            )

    @patch("requests.get")
    def test_daterange(self, mock_get):
        start_date = "2024-06-01"
        end_date = "2024-06-05"
        expected_dates = [
            "2024-06-01T00:00:00Z",
            "2024-06-02T00:00:00Z",
            "2024-06-03T00:00:00Z",
            "2024-06-04T00:00:00Z",
            "2024-06-05T00:00:00Z",
        ]
        self.assertEqual(self.campsite._daterange(start_date, end_date), expected_dates)

    @patch("requests.post")
    def test_send_ntfy_message(self, mock_post):
        self.campsite._send_ntfy_message(
            "2024-06-01", "2024-06-05", "CampgroundA", "027"
        )
        mock_post.assert_called_once_with(
            f"{self.ntfy_url}/{self.ntfy_topic}",
            data="Site 027 is available for reservation from 2024-06-01 to 2024-06-05 at CampgroundA",
        )


if __name__ == "__main__":
    unittest.main()
