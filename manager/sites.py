

from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String

from manager.database import Model


def import_sites(sites, db_session):
    for site_host, site_config in sites.items():
        site_config["host"] = site_host
        if "ssh_hostname" not in site_config.keys():
            site_config["ssh_hostname"] = site_host
        if "ssh_port" not in site_config.keys():
            site_config["ssh_port"] = 22
        site = db_session.query(Site).filter(
            Site.host == site_host).scalar()
        if not site:
            site = Site(**site_config)
            db_session.add(site)
            print("created", site)
        else:
            for key, value in site_config.items():
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
