
from datetime import datetime
from termcolor import colored
import requests
from requests.exceptions import ConnectionError

from manager.status.models import SiteStatus, latest_status


STATUS_COLORS = {
    SiteStatus.UP: ("grey", "on_green"),
    SiteStatus.DOWN: ("white", "on_red"),
    SiteStatus.UNKNOWN: ("grey", "on_yellow"),
}


def check_https_status(site_info):
    start_at = datetime.now()
    url = site_info["site_url"]
    latest_status = site_info["site_latest_status"]
    result = {
        **site_info,
        "request_time": start_at,
    }
    try:
        response = requests.get(url)
        end_at = datetime.now()
        result["duration"] = end_at - start_at
        result["status_code"] = response.status_code
        if response.status_code == 200:
            result["status"] = SiteStatus.UP
        else:
            result["status"] = SiteStatus.DOWN
            result["error"] = response.status_code
    except ConnectionError as ex:
        result["status"] = SiteStatus.DOWN
        result["error"] = "Connection error."
    result["status_changed"] = result["status"] != latest_status
    result["notify"] = [latest_status, result["status"]] != [
        SiteStatus.UNKNOWN, SiteStatus.UP]
    return result


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
