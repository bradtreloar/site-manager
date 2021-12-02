
from datetime import datetime
from termcolor import colored
import requests
from requests.exceptions import ConnectionError

from manager.status.models import SiteStatus


STATUS_COLORS = {
    SiteStatus.UP: ("grey", "on_green"),
    SiteStatus.DOWN: ("white", "on_red"),
    SiteStatus.UNKNOWN: ("grey", "on_yellow"),
}


class UnexpectedResponseException(BaseException):
    pass


def check_https_status(site_info):
    prev_status = site_info["site_latest_status"]

    def do_request():
        url = site_info["site_url"]
        response = requests.get(url)
        status_code = response.status_code
        if status_code != 200:
            raise UnexpectedResponseException(response.status_code)

    attempts = 0
    status = SiteStatus.UNKNOWN
    duration = None
    request_time = datetime.now()
    while attempts < 2 and status != SiteStatus.UP:
        try:
            start_at = datetime.now()
            do_request()
            end_at = datetime.now()
            duration = end_at - start_at
            request_time = start_at
            status = SiteStatus.UP
        except ConnectionError:
            status = SiteStatus.DOWN
        except UnexpectedResponseException:
            status = SiteStatus.DOWN
        attempts += 1
    status_changed = status != prev_status
    ignore_status_change = prev_status == SiteStatus.UNKNOWN and status == SiteStatus.UP
    return {
        **site_info,
        "duration": duration,
        "request_time": request_time,
        "status": status,
        "status_changed": status != prev_status,
        "notify": status_changed and not ignore_status_change,
    }


def print_https_status_list(sites):
    print()
    for site in sites:
        status = site.latest_status
        try:
            status_age = (datetime.now() -
                          site.latest_status_log_entry.created)
        except AttributeError:
            status_age = ""
        print("{0:.<40} {1} for {2} days".format(
            site.host,
            colored(" {} ".format(
                status.value.upper()), *STATUS_COLORS[status]),
            status_age.days))
    print()
