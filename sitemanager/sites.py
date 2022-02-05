
import json
from typing import Dict
from sqlalchemy.orm.session import Session

from sitemanager.models import Site, SiteSSH
from sitemanager.config import SiteConfig, WebAuthItemConfig


def import_sites(sites_config, webauth_config, db_session):
    for site_host, site_config in sites_config.items():
        site = import_site(site_host, site_config, db_session)
        if "ssh" in site_config:
            import_site_ssh_config(
                site, site_config["ssh"], webauth_config, db_session)
        db_session.commit()
    sites = db_session.query(Site).all()
    for site in sites:
        site.is_active = site.host in sites_config
    db_session.commit()


def import_site(
        site_host: str,
        site_config: SiteConfig,
        db_session: Session) -> Site:
    site_attributes = {
        "host": site_host,
        "app": site_config.get("app"),
    }
    site = db_session.query(Site).filter(
        Site.host == site_host).scalar()
    if site is not None:
        for key, value in site_attributes.items():
            setattr(site, key, value)
    else:
        site = Site(**site_attributes)
        db_session.add(site)
    return site


def import_site_ssh_config(
        site: Site,
        ssh_config: SiteSSH,
        webauth_config: Dict[str, WebAuthItemConfig],
        db_session: Session):
    if "host" not in ssh_config:
        ssh_config["host"] = site.host
    ssh_host = ssh_config["host"]
    if ssh_host in webauth_config:
        ssh_config["webauth"] = json.dumps(webauth_config[ssh_host])
    if site.ssh_config:
        for key, value in ssh_config.items():
            setattr(site.ssh_config, key, value)
    else:
        site.ssh_config = SiteSSH(**ssh_config)
