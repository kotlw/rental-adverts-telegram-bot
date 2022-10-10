import json
import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    select,
)
from sqlalchemy.dialects.postgresql import UUID

from bot import entity, cfg
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
    settlement_date = Column(DateTime)
    price = Column(Integer)
    contact = Column(String)
    photo = Column(String)
    create_date = Column(DateTime)


class AdvertRepository(base.BaseRepository):
    model = AdvertModel

    async def get_user_posts(self, user_id: int) -> list[entity.Advert]:

        async with self.async_session() as session:
            stmt = select(AdvertModel).where(AdvertModel.user_id == user_id)
            adverts = await session.execute(stmt)

            adverts = [self._to_entity(p[0]) for p in adverts.all()]
            await session.commit()

        await self.engine.dispose()

        return adverts

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
            settlement_date=datetime.strptime(
                entity_.settlement_date, cfg.date_format
            ),
            price=entity_.price,
            contact=entity_.contact,
            photo=json.dumps(entity_.photo),
            create_date=entity_.create_date,
        )

    def _to_entity(self, sa_obj: AdvertModel) -> entity.Advert:
        return entity.Advert(
            id=uuid.UUID(str(sa_obj.id)),
            status=entity.AdvertStatusEnum(sa_obj.status),
            user_id=sa_obj.user_id,
            distinct=sa_obj.distinct,
            street=sa_obj.street,
            building_type=sa_obj.building_type,
            floor=sa_obj.floor,
            square=sa_obj.square,
            num_of_rooms=sa_obj.num_of_rooms,
            layout=sa_obj.layout,
            description=sa_obj.description,
            settlement_date=sa_obj.settlement_date.strftime(cfg.date_format),
            price=sa_obj.price,
            contact=sa_obj.contact,
            photo=json.loads(sa_obj.photo),
            create_date=sa_obj.create_date,
        )
