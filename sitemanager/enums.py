
from enum import Enum


class SiteStatus(Enum):
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


class StatusLogType(Enum):
    HTTPS = "https"
    SMTP = "smtp"
