import json

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Enum,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID

from bot import entity
from bot.repository import base


class AdvertModel(base.BaseModel):
    __tablename__ = "advert"

    id = Column(UUID(as_uuid=True), primary_key=True)
    status = Column(Enum(entity.AdvertStatusEnum))
    user_id = Column(ForeignKey("user.id"))
    distinct = Column(String)
    street = Column(String)
    building_type = Column(String)
    floor = Column(Integer)
    square = Column(Integer)
    num_of_rooms = Column(Integer)
    layout = Column(String)
    description = Column(String)
    settlement_date = Column(Date)
    price = Column(Integer)
    contact = Column(String)
    photo = Column(String)
    create_date = Column(DateTime)


class AdvertRepository(base.BaseRepository):
    model = AdvertModel

    def _from_entity(self, entity_: entity.Advert) -> AdvertModel:
        return AdvertModel(
            id=entity_.id,
            status=entity_.status,
            user_id=entity_.user_id,
            distinct=entity_.distinct,
            street=entity_.street,
            building_type=entity_.building_type,
            floor=entity_.floor,
            square=entity_.square,
            num_of_rooms=entity_.num_of_rooms,
            layout=entity_.layout,
            description=entity_.description,
            settlement_date=entity_.settlement_date,
            price=entity_.price,
            contact=entity_.contact,
            photo=json.dumps(entity_.photo),
            create_date=entity_.create_date,
        )
