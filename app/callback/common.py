"""This file contains common callbacks and callback factories."""
from typing import Any

from sqlalchemy import select
from telegram import Update
from telegram._utils.types import ReplyMarkup
from telegram.ext._utils.types import CCT, HandlerCallback
from telegram import ReplyKeyboardRemove

import db.common
import db.model


async def start(update: Update, _) -> None:
    """Stores user data, and sends welcome message."""

    chat = update.message.chat

    async with db.common.async_session() as session:
        result = await session.execute(
            select([db.model.User.id]).where(db.model.User.id == chat.id)
        )
        if not result.fetchone():
            async with session.begin():
                session.add(
                    db.model.User(
                        id=chat.id,
                        username=chat.username,
                        first_name=chat.first_name,
                    )
                )

        await session.commit()

    await db.common.engine.dispose()


def create_reply_text_callback(
    text: str,
    reply_markup: ReplyMarkup = None,  # type: ignore
    return_value: Any = None,
) -> HandlerCallback[Update, CCT, Any]:
    """Returns callback with defined replying text, reply_markup and
    return_value.
    """

    async def callback(update: Update, _) -> Any:

        await update.message.reply_text(text, reply_markup=reply_markup)

        return return_value

    return callback
