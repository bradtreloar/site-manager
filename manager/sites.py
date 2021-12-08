
import json
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, Integer, String

from manager.database import Model


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


class Site(Model):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    host = Column(String(255), unique=True, nullable=False)
    app = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<Site(site='{self.host}')>"


class SiteSSHConfig(Model):
    __tablename__ = "site_ssh_configs"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer,
                     ForeignKey("sites.id"), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=22, nullable=False)
    user = Column(String(255), nullable=False)
    key_filename = Column(String(1023))
    webauth = Column(String(4095))

    site = relationship(Site, back_populates="ssh_config")

    def __repr__(self):
        return f"<SiteSSHConfig(site='{self.site.host}')>"

    def to_dict(self):
        return {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "key_filename": self.key_filename,
            "webauth": json.loads(self.webauth) if self.webauth else None
        }


Site.ssh_config = relationship(SiteSSHConfig,
                               uselist=False,
                               back_populates="site",
                               cascade="all, delete")
