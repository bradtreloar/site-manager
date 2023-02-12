
import json
from typing import Dict
from sqlalchemy.orm.session import Session

from sitemanager.models import Site, SiteSSH
from sitemanager.config import SiteConfig


def import_sites(
        sites_config: Dict[str, SiteConfig],
        db_session: Session):

    # Add site host to site config.
    for site_host, site_config in sites_config.items():
        site_config["host"] = site_host

    # Imports sites.
    for site_config in sites_config.values():
        site = import_site(site_config, db_session)
        db_session.commit()

    # Set sites as active/inactive depending on whether or not they are in the
    # sites config.
    sites = db_session.query(Site).all()
    for site in sites:
        site.is_active = site.host in sites_config
    db_session.commit()


def import_site(site_config: SiteConfig, db_session: Session) -> Site:
    site_attributes = {
        "host": site_config["host"],
        "app": site_config.get("app"),
    }
    site = db_session.query(Site).filter(
        Site.host == site_config["host"]).scalar()
    if site is not None:
        for key, value in site_attributes.items():
            setattr(site, key, value)
    else:
        site = Site(**site_attributes)
        db_session.add(site)
    if "ssh" in site_config:
        import_site_ssh(site, site_config["ssh"], db_session)
    else:
        site_ssh = db_session.query(SiteSSH).filter(
            SiteSSH.site == site).scalar()
        if site_ssh:
            db_session.delete(site_ssh)
    return site


def import_site_ssh(
        site: Site,
        ssh_config: SiteSSH,
        db_session: Session):
    if "host" not in ssh_config:
        ssh_config["host"] = site.host
    ssh_host = ssh_config["host"]
    if site.ssh_config:
        for key, value in ssh_config.items():
            setattr(site.ssh_config, key, value)
    else:
        site.ssh_config = SiteSSH(**ssh_config)
