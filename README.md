
# Campsite Availability Checker

This Python script checks for campsite availability on recreation.gov and sends notifications when a site is available for specified dates.

## Features

- Checks campsite availability for specified campgrounds and dates.
- Sends notifications via ntfy when a site is available.
- Configurable request headers and API URL.

## Requirements

- Python 3.x
- `requests` library

## Installation

1. Clone the repository:
```bash
    git clone https://github.com/Teachmetech/campsite.git
    cd campsite
```
2. Install the required packages:
```bash
    pip install -r requirements.txt
```
## Usage

1. Define your campgrounds and dates in the script.

```python
    camp_grounds = {
        "Campground A": "123456",
        "Campground B": "789012"
    }

    dates = [
        ("2024-06-01", "2024-06-05"),
        ("2024-07-10", "2024-07-15")
    ]
```

2. Create an instance of the `Campsite` class and call the `check_sites` method.

```python
    campsite_checker = Campsite(camp_grounds, dates)
    campsite_checker.check_sites()
```

## Configuration

- `recreation_api_url`: URL to fetch campsite availability (default provided).
- `request_headers`: Headers for the HTTP requests (default provided).
- `ntfy_url`: URL for the ntfy notification service (default: `https://ntfy.sh`).
- `ntfy_topic`: Topic for ntfy notifications (default: `campsite`).
- `sleep_time`: Time in seconds to wait between checks (default: 60).

## Example

```python
import time
import requests
from datetime import datetime, timedelta

# camp_grounds keys can be anything, this is what NTFY will use in its message
# For example, you could use Camp Cook Campsite or camp_cook_campsite for the key
# The value matters, however, as this is the ID of the campsite which you can find
# in the URL when clicking on the campsite.

camp_grounds = {
    "Campground A": "123456",
    "Campground B": "789012"
}

dates = [
    ("2024-06-01", "2024-06-05"),
    ("2024-07-10", "2024-07-15")
]

campsite_checker = Campsite(camp_grounds, dates)
campsite_checker.check_sites()
```

## License

This project is licensed under the MIT License.
