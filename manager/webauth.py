
from requests.sessions import Session
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'


class LoginError(BaseException):
    pass


class WebauthError(BaseException):
    pass


def start_webauth_session(config):
    session = Session()
    response = session.post(config["login_url"], {
        "login": "login",
        "username": config["username"],
        "password": config["password"],
    }, params={
        "target": "",
        "auth_id": "",
        "ap_name": "",
    }, verify=False)
    if response.status_code != 200:
        raise LoginError
    response = session.post(config["webauth_url"], {
        "rs": "is_lsys_image_exist",
        "rsargs[]": "root",
        "csrf_token": "",
    }, verify=False)
    if response.status_code != 200:
        raise WebauthError
