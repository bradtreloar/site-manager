
import json

from sitemanager.models import Site, SiteSSHConfig


def import_sites(sites_config, webauth_config, db_session):
    """Adds or updates each site from the config in the database."""
    for site_host, site_config in sites_config.items():
        site_config["host"] = site_host
        site_attributes = {
            "host": site_host,
        }
        if "app" in site_config.keys():
            site_attributes["app"] = site_config["app"]
        site = db_session.query(Site).filter(
            Site.host == site_host).scalar()
        if not site:
            site = Site(**site_attributes)
            db_session.add(site)
        else:
            for key, value in site_attributes.items():
                setattr(site, key, value)
        ssh_config_attributes = None
        if "ssh" in site_config.keys():
            ssh_config_attributes = site_config["ssh"]
            if "host" not in ssh_config_attributes.keys():
                ssh_config_attributes["host"] = site_host
            ssh_host = ssh_config_attributes["host"]
            if ssh_host in webauth_config.keys():
                ssh_config_attributes["webauth"] = json.dumps(
                    webauth_config[ssh_host])
            if not site.ssh_config:
                site.ssh_config = SiteSSHConfig(**ssh_config_attributes)
            else:
                for key, value in ssh_config_attributes.items():
                    setattr(site.ssh_config, key, value)
        db_session.commit()
    sites = db_session.query(Site).all()
    for site in sites:
        site.is_active = site.host in sites_config.keys()
    db_session.commit()
