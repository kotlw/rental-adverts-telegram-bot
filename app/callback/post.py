"""This file contains callbacks and callback factories related to /post
ConversationHandler.
"""
from typing import Any

from sqlalchemy import select
from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram._utils.types import ReplyMarkup
from telegram.ext._utils.types import CCT, HandlerCallback

import config
import db.model
import msg.post


(
    DISTINCT,
    STREET,
    BUILDING_TYPE,
    FLOOR,
    SQUARE,
    NUM_OF_ROOMS,
    LAYOUT,
    DESCRIPTION,
    SETTLEMENT_DATE,
    PRICE,
    CONTACT,
    PHOTO,
) = range(12)


async def entry_point(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Starts posting advert conversation."""

    await update.message.reply_text(msg.post.START)
    await update.message.reply_text(
        msg.post.SELECT_DISTINCT,
        reply_markup=ReplyKeyboardMarkup(
            [[b] for b in config.DISTINCT_VALUES]
        ),
    )

    advert = db.model.Advert(status="pending", user_id=update.message.chat_id)
    context.user_data["advert"] = advert  # type: ignore

    return DISTINCT


def create_conversation_callback(
    text: str,
    reply_markup: ReplyMarkup = ReplyKeyboardRemove(),
    return_value: int = ConversationHandler.END,
    data_key: str | None = None,
    data_attr: str | None = None,
) -> HandlerCallback[Update, CCT, Any]:

    async def callback(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> Any:

        if data_key and data_attr:
            data = context.user_data[data_key]  # type: ignore
            setattr(data, data_attr, update.message.text)

        await update.message.reply_text(text, reply_markup=reply_markup)

        return return_value

    return callback
