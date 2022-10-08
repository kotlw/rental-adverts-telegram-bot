from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from bot import DB_URI
from bot.repository import user, advert

engine = create_async_engine(DB_URI, echo=True)
session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

user = user.UserRepository(engine, session)
advert = advert.AdvertRepository(engine, session)
