import abc
from enum import Enum
from typing import Dict
from uuid import UUID, uuid4
from datetime import date, datetime
from dataclasses import dataclass, asdict


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
    settlement_date: str
    price: int
    contact: str
    photo: list[str]
    id: UUID = uuid4()
    status: AdvertStatusEnum = AdvertStatusEnum.PENDING
    create_date: datetime = datetime.now()

    dict = asdict

    @staticmethod
    def from_dict(d: Dict):
        res = {
            "user_id": int(d["user_id"]),
            "distinct": str(d["distinct"]),
            "street": str(d["street"]),
            "building_type": str(d["building_type"]),
            "floor": int(d["floor"]),
            "square": int(d["square"]),
            "num_of_rooms": int(d["num_of_rooms"]),
            "layout": str(d["layout"]),
            "description": str(d["description"]),
            "settlement_date": str(d["settlement_date"]),
            "price": int(d["price"]),
            "contact": str(d["contact"]),
            "photo": list(d["photo"]),
        }
        if d.get("id"):
            res["id"] = d["id"]
            res["status"] = d["status"]
            res["create_date"] = d["create_date"]
        return Advert(**res)
