
from datetime import datetime
import requests


def test_https_response(site):
    start_at = datetime.now()
    response = requests.get("https://" + site["host"])
    end_at = datetime.now()
    duration = end_at - start_at
    return {
        "status_code": response.status_code,
        "duration": duration.total_seconds()
    }
