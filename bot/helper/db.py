import json
import uuid
from datetime import datetime
from functools import singledispatchmethod

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Integer,
    Boolean,
    Enum,
    select,
    update,
    delete,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from bot import entity


Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    is_admin = Column(Boolean, default=False)
    create_date = Column(DateTime)


class Advert(Base):  # pylint: disable=missing-class-docstring
    __tablename__ = "advert"
    id = Column(UUID(as_uuid=True), primary_key=True)
    status = Column(Enum(entity.StatusEnum))
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


class DBGateway:
    def __init__(self, db_uri: str):
        self.engine = create_async_engine(db_uri, echo=True)

        # expire_on_commit=False will prevent attributes from being expired
        # after commit.
        self.async_session = sessionmaker(
            self.engine, expire_on_commit=False, class_=AsyncSession
        )

    async def recreate(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def insert_user_if_not_exist(self, user: entity.User) -> None:

        async with self.async_session() as session:
            result = await session.execute(
                select([User.id]).where(User.id == user.id)
            )

            if not result.fetchone():
                session.add(self._from_entity(user))

            await session.commit()

        await self.engine.dispose()

    async def upsert_advert(self, advert: entity.Advert) -> None:

        async with self.async_session() as session:
            result = await session.execute(
                select([Advert.id]).where(Advert.id == advert.id)
            )

            if result.fetchone():
                stmt = (
                    update(Advert)
                    .where(Advert.id == advert.id)
                    .values(
                        {
                            column: getattr(self._from_entity(advert), column)
                            for column in Advert.__table__.columns.keys()
                        }
                    )
                )
                await session.execute(stmt)
            else:
                session.add(self._from_entity(advert))

            await session.commit()

        await self.engine.dispose()

    async def get_user_posts(self, user_id: int) -> list[entity.Advert]:

        async with self.async_session() as session:
            posts = await session.execute(
                select(Advert).where(Advert.user_id == user_id)
            )
            posts = [self._to_entity(p[0]) for p in posts.all()]
            await session.commit()

        await self.engine.dispose()

        return posts

    async def delete_post(self, advert_id: uuid.UUID) -> None:

        async with self.async_session() as session:
            await session.execute(delete(Advert).where(Advert.id == advert_id))
            await session.commit()

        await self.engine.dispose()

    async def get_posts_by_filter(
        self, filter_data: dict
    ) -> list[entity.Advert]:

        async with self.async_session() as session:
            stmt = select(Advert).where(Advert.status == filter_data["status"])

            if filter_data["distinct"]:
                stmt = stmt.where(Advert.distinct.in_(filter_data["distinct"]))

            if filter_data["building_type"]:
                stmt = stmt.where(
                    Advert.building_type.in_(filter_data["building_type"])
                )

            if filter_data["floor"]:
                stmt = stmt.where(Advert.floor.between(*filter_data["floor"]))

            if filter_data["num_of_rooms"]:
                stmt = stmt.where(
                    Advert.num_of_rooms.between(*filter_data["floor"])
                )

            if filter_data["price"]:
                stmt = stmt.where(Advert.price.between(*filter_data["price"]))

            posts = await session.execute(stmt)
            posts = [self._to_entity(p[0]) for p in posts.all()]
            await session.commit()

        await self.engine.dispose()

        return posts

    @singledispatchmethod
    def _from_entity(self, arg):
        raise NotImplementedError(f"Cannot map value of type {type(arg)}")

    @_from_entity.register
    def _(self, usr_entity: entity.User) -> User:
        return User(
            id=usr_entity.id,
            username=usr_entity.username,
            first_name=usr_entity.first_name,
            is_admin=usr_entity.is_admin,
            create_date=usr_entity.create_date,
        )

    @_from_entity.register
    def _(self, ad_entity: entity.Advert) -> Advert:
        return Advert(
            id=ad_entity.id,
            status=ad_entity.status,
            user_id=ad_entity.user_id,
            distinct=ad_entity.distinct,
            street=ad_entity.street,
            building_type=ad_entity.building_type,
            floor=ad_entity.floor,
            square=ad_entity.square,
            num_of_rooms=ad_entity.num_of_rooms,
            layout=ad_entity.layout,
            description=ad_entity.description,
            settlement_date=ad_entity.settlement_date,
            price=ad_entity.price,
            contact=ad_entity.contact,
            photo=json.dumps(ad_entity.photo),
            create_date=ad_entity.create_date,
        )

    @singledispatchmethod
    def _to_entity(self, arg):
        raise NotImplementedError(f"Cannot map value of type {type(arg)}")

    @_to_entity.register
    def _(self, usr_model: User) -> entity.User:
        return entity.User(
            id=usr_model.id,
            username=usr_model.username,
            first_name=usr_model.first_name,
            is_admin=usr_model.is_admin,
            create_date=usr_model.create_date,
        )

    @_to_entity.register
    def _(self, ad_model: Advert) -> entity.Advert:
        return entity.Advert(
            id=uuid.UUID(ad_model.id.hex),
            status=ad_model.status,
            user_id=ad_model.user_id,
            distinct=ad_model.distinct,
            street=ad_model.street,
            building_type=ad_model.building_type,
            floor=ad_model.floor,
            square=ad_model.square,
            num_of_rooms=ad_model.num_of_rooms,
            layout=ad_model.layout,
            description=ad_model.description,
            settlement_date=datetime.strftime(
                ad_model.settlement_date, "%d.%m.%y"
            ),
            price=ad_model.price,
            contact=ad_model.contact,
            photo=json.loads(ad_model.photo),
            create_date=ad_model.create_date,
        )
