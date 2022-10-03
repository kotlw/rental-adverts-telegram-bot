"""This module contains sqlalchemy models."""
import enum

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import func
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import Boolean
from sqlalchemy import Enum
from sqlalchemy.ext.declarative import declarative_base

import config


Base = declarative_base()


class User(Base):  # pylint: disable=C0115
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    create_date = Column(DateTime, server_default=func.now())
    is_admin = Column(Boolean, default=False)

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}


class Advert(Base):  # pylint: disable=C0115
    __tablename__ = "advert"
    id = Column(Integer, primary_key=True)
    create_date = Column(DateTime, server_default=func.now())
    status = Column(Enum(enum.Enum("status", config.DB_STATUS_VALUES)))
    user_id = Column(ForeignKey("user.id"))
    distinct = Column(Enum(enum.Enum("distinct", config.DB_DISTINCT_VALUES)))
    street = Column(String(50))
    building_type = Column(
        Enum(enum.Enum("building_type", config.DB_BUILDING_TYPE_VALUES))
    )
    floor = Column(Integer)
    square = Column(Integer)
    num_of_rooms = Column(Integer)
    layout = Column(String)
    description = Column(String)
    settlement_date = Column(DateTime)
    price_uah = Column(Integer)
    price_usd = Column(Integer)
    contact = Column(String)

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}
