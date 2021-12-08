
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
    filepath = config["path"]
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    db = create_engine(f"sqlite+pysqlite:///{filepath}")
    Model.metadata.create_all(db)
    session = sessionmaker(bind=db)()
    return session
