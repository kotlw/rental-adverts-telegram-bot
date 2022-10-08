import abc

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID, uuid4
from enum import Enum


class AdvertStatusEnum(Enum):
    PENDING = "розглядається"
    APPROVED = "опубліковано"


@dataclass(slots=True)
class BaseEntity(abc.ABC):
    ...

@dataclass(slots=True, kw_only=True)
class User(BaseEntity):
    id: int
    username: str
    first_name: str
    is_admin: bool = False
    create_date: datetime = datetime.now()


@dataclass(slots=True, kw_only=True)
class Advert(BaseEntity):
    user_id: int
    distinct: str
    street: str
    building_type: str
    floor: int
    square: int
    num_of_rooms: int
    layout: str
    description: str
    settlement_date: date
    price: int
    contact: str
    photo: list[str]
    id: UUID = uuid4()
    status: AdvertStatusEnum = AdvertStatusEnum.PENDING
    create_date: datetime = datetime.now()

