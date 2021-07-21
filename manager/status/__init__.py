
from datetime import datetime
import requests


def check_https_status(site):
    start_at = datetime.now()
    url = "https://" + site.host
    response = requests.get(url)
    end_at = datetime.now()
    duration = end_at - start_at
    return {
        "site": site,
        "url": url,
        "request_time": start_at,
        "status_code": response.status_code,
        "duration": duration.total_seconds()
    }
