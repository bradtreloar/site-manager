

from sitemanager.remote.wordpress import WordpressClient
from sitemanager.remote.drupal import DrupalClient


REMOTE_CLIENTS = {
    "wordpress": WordpressClient,
    "drupal": DrupalClient,
}


def get_remote_client(app_name):
    return REMOTE_CLIENTS[app_name]
