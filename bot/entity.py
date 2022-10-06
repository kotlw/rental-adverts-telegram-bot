import enum
from uuid import UUID, uuid4
from datetime import datetime, date

from pydantic import BaseModel, validator

class StatusEnum(enum.Enum):
    PENDING = 1
    APPROVED = 2
    HIDDEN = 3


class User(BaseModel):
    id: int
    username: str
    first_name: str
    is_admin: bool = False
    create_date: datetime = datetime.now()


class Advert(BaseModel):
    id: UUID = uuid4()
    status: StatusEnum = StatusEnum.PENDING
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
    create_date: datetime = datetime.now()

    @validator("settlement_date", pre=True)
    def parse_birthdate(cls, value):  # pylint: disable
        return datetime.strptime(value, "%d.%m.%y").date()

    class Config:
        json_encoders = {
            date: lambda x: x.strftime("%d.%m.%y"),
        }
