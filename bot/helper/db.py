from functools import singledispatch

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    Integer,
    Boolean,
    Enum,
    select,
)
from sqlalchemy.orm import sessionmaker
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
    id = Column(Integer, primary_key=True)
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

    async def upsert_user(self, user: entity.User):
        async with self.async_session() as session:
            result = await session.execute(
                select([User.id]).where(User.id == user.id)
            )

            if not result.fetchone():
                session.add(self._from_entity(user))

            await session.commit()

        await self.engine.dispose()

    @singledispatch
    def _from_entity(self, usr_entity: entity.User) -> User:
        return User(
            id=usr_entity.id,
            username=usr_entity.username,
            first_name=usr_entity.first_name,
            is_admin=usr_entity.is_admin,
            create_date=usr_entity.create_date,
        )

    @_from_entity.register(entity.Advert)
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
            photo=ad_entity.photo,
            create_date=ad_entity.create_date,
        )

