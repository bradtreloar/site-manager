

from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String

from manager.database import Model


def import_sites(sites, db_session):
    for site_host, site_config in sites.items():
        site_config["host"] = site_host
        site_attributes = {
            "host": site_host,
            "ssh_hostname": site_host,
            "ssh_port": 22,
        }
        if "app" in site_config.keys():
            site_attributes["app"] = site_config["app"]
        if "ssh" in site_config.keys():
            site_ssh_config = site_config["ssh"]
            if "hostname" in site_ssh_config.keys():
                site_attributes["ssh_hostname"] = site_ssh_config["hostname"]
            if "port" in site_ssh_config.keys():
                site_attributes["ssh_port"] = site_ssh_config["port"]
            if "user" in site_ssh_config.keys():
                site_attributes["ssh_user"] = site_ssh_config["user"]
            if "key" in site_ssh_config.keys():
                site_attributes["ssh_key_filename"] = site_ssh_config["key"]
        site = db_session.query(Site).filter(
            Site.host == site_host).scalar()
        if not site:
            site = Site(**site_attributes)
            db_session.add(site)
            print("created", site)
        else:
            for key, value in site_attributes.items():
                setattr(site, key, value)
            print("updated", site)
        db_session.commit()


class Site(Model):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    host = Column(String(255), unique=True, nullable=False)
    ssh_hostname = Column(String(255))
    ssh_port = Column(Integer, default=22)
    ssh_user = Column(String(255))
    ssh_key_filename = Column(String(1023))
    app = Column(String(255))

    def __repr__(self):
        return "<Site(site='{}')>".format(
            self.host)
