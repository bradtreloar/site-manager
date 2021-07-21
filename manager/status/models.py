
from enum import Enum
from sqlalchemy import (
    Column, UniqueConstraint,
    Date, DateTime, Enum, ForeignKey, Numeric, Integer, String)
from sqlalchemy.orm import relationship
from manager.database import Model
from manager.sites import Site


class SiteStatusType(Enum):
    HTTPS = "https"
    SMTP = "smtp"


class StatusLogEntry(Model):
    __tablename__ = "status_log_entries"

    id = Column(Integer, primary_key=True)
    site_id = Column(Integer,
                     ForeignKey("sites.id"), nullable=False)
    type = Enum(SiteStatusType)

    site = relationship(Site, back_populates="status_log_entries")

    __table_args__ = (
        UniqueConstraint("type", "site_id"),
    )

    def __repr__(self):
        return "<StatusLogEntry(site='{}')>".format(
            self.site.host)


Site.status_log_entries = relationship(StatusLogEntry,
                                       back_populates="site",
                                       cascade="all, delete")
