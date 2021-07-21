
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column, UniqueConstraint,
    Date, DateTime, Enum, ForeignKey, Numeric, Integer, String)
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Model = declarative_base()


def session(config):
    db = create_engine("sqlite+pysqlite:///{}".format(config["path"]))
    Model.metadata.create_all(db)
    session = sessionmaker(bind=db)()
    return session
