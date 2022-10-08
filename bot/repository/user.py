from sqlalchemy import Column, Integer, String, Boolean, DateTime

from bot import entity
from bot.repository import base


class UserModel(base.BaseModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    first_name = Column(String)
    is_admin = Column(Boolean, default=False)
    create_date = Column(DateTime)


class UserRepository(base.BaseRepository):
    model = UserModel

    def _from_entity(self, entity_: entity.User) -> UserModel:
        return UserModel(
            id=entity_.id,
            username=entity_.username,
            first_name=entity_.first_name,
            is_admin=entity_.is_admin,
            create_date=entity_.create_date,
        )
