import abc

from sqlalchemy import select, insert, update
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

    async def upsert(self, entity_: entity.BaseEntity) -> None:
        user = self._from_entity(entity_)

        async with self.async_session() as session:
            stmt = select([self.model.id]).where(self.model.id == user.id)
            res = await session.execute(stmt)

            if res.fetchone():
                stmt = update(self.model).where(self.model.id == user.id)
                stmt = stmt.values(user.to_dict())
            if not res.fetchone():
                stmt = insert(self.model).values(user.to_dict())

            await session.commit()

        await self.engine.dispose()

    @abc.abstractmethod
    def _from_entity(self, entity_: entity.BaseEntity) -> BaseModel:
        ...
