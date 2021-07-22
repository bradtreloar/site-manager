
import enum
from sqlalchemy import (
    Column, UniqueConstraint,
    Date, DateTime, Enum, ForeignKey, Numeric, Integer, String)
from sqlalchemy.orm import relationship
from manager.database import Model
from manager.sites import Site


class StatusLogType(enum.Enum):
    HTTPS = "https"
    SMTP = "smtp"


class SiteStatus(enum.Enum):
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


class StatusLogEntry(Model):
    __tablename__ = "status_log_entries"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer,
                     ForeignKey("sites.id"), nullable=False)
    type = Column(Enum(StatusLogType), nullable=False)
    status = Column(Enum(SiteStatus), nullable=False)
    created = Column(DateTime, nullable=False)

    site = relationship(Site, back_populates="status_log_entries")

    def __repr__(self):
        return "<StatusLogEntry(site='{}')>".format(
            self.site.host)


Site.status_log_entries = relationship(StatusLogEntry,
                                       back_populates="site",
                                       order_by="desc(StatusLogEntry.created)",
                                       cascade="all, delete")


@property
def latest_status_log_entry(site):
    entries = site.status_log_entries
    return entries[0] if len(entries) > 0 else None


Site.latest_status_log_entry = latest_status_log_entry


@property
def last_status(site):
    entry = site.latest_status_log_entry
    return entry.status if entry else SiteStatus.UNKNOWN


Site.last_status = last_status
