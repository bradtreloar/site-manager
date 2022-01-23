
import enum
import json
from sqlalchemy import (
    Column, Date, DateTime, Enum, ForeignKey, Numeric, Integer, String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Boolean, Integer, String

from sitemanager.database import BaseModel
from sitemanager.enums import SiteStatus, StatusLogType


class Site(BaseModel):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    host = Column(String(255), unique=True, nullable=False)
    app = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)

    @property
    def latest_status_log_entry(site):
        entries = site.status_log_entries
        return entries[0] if len(entries) > 0 else None

    @property
    def latest_status(site):
        entry = site.latest_status_log_entry
        return entry.status if entry else SiteStatus.UNKNOWN

    def __repr__(self):
        return f"<Site(site='{self.host}')>"


class SiteSSHConfig(BaseModel):
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


class StatusLogEntry(BaseModel):
    __tablename__ = "status_log_entries"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer,
                     ForeignKey("sites.id"), nullable=False)
    type = Column(Enum(StatusLogType), nullable=False)
    status = Column(Enum(SiteStatus), nullable=False)
    created = Column(DateTime, nullable=False)

    site = relationship(Site, back_populates="status_log_entries")

    def __repr__(self):
        return f"<StatusLogEntry(site='{self.site.host}')>"


Site.status_log_entries = relationship(StatusLogEntry,
                                       back_populates="site",
                                       order_by="desc(StatusLogEntry.created)",
                                       cascade="all, delete")
