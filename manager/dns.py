
from datetime import datetime
import whois


def get_domain_expiration_datetime(site):
    domain = whois.query(site["host"])
    return domain.expiration_date


def get_domain_nameservers(site):
    domain = whois.query(site["host"])
    return domain.name_servers
