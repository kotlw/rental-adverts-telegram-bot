import abc

from sqlalchemy import select, insert, update, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.declarative import declarative_base

from bot import entity


Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return {
            column: getattr(self, column)
            for column in self.__class__.__table__.columns.keys()
        }

class BaseRepository(abc.ABC):
    def __init__(self, engine: AsyncEngine, async_session: sessionmaker):
        self.engine = engine
        self.async_session = async_session
        self.model: BaseModel

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def upsert(self, entity_: entity.BaseEntity) -> None:
        sa_obj = self._from_entity(entity_)

        async with self.async_session() as session:
            stmt = select([self.model.id]).where(self.model.id == sa_obj.id)
            res = await session.execute(stmt)

            if res.fetchone():
                stmt = update(self.model).where(self.model.id == sa_obj.id)
                stmt = stmt.values(sa_obj.to_dict())
            else:
                stmt = insert(self.model).values(sa_obj.to_dict())

            await session.execute(stmt)
            await session.commit()

        await self.engine.dispose()

    async def remove(self, entity_: entity.BaseEntity) -> None:
        sa_obj = self._from_entity(entity_)

        async with self.async_session() as session:
            stmt = delete(self.model).where(self.model.id == sa_obj.id)
            await session.execute(stmt)
            await session.commit()

        await self.engine.dispose()

    @abc.abstractmethod
    def _from_entity(self, entity_: entity.BaseEntity) -> BaseModel:
        ...
