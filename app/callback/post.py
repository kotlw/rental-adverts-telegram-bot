"""This file contains callbacks and callback factories related to /post
ConversationHandler.
"""
from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from telegram.constants import ParseMode

import config
import db.model
import msg.post
import msg.common


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
    OVERVIEW,
) = range(13)


async def entry_point(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Starts posting advert conversation."""

    rm = ReplyKeyboardMarkup([[b] for b in config.DISTINCT_VALUES])

    await update.message.reply_text(msg.post.START)
    await update.message.reply_text(msg.post.ASK_DISTINCT, reply_markup=rm)

    advert = db.model.Advert(status="pending", user_id=update.message.chat_id)
    context.user_data["advert"] = advert  # type: ignore

    return DISTINCT


async def distinct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.distinct = update.message.text

    rm = ReplyKeyboardRemove()
    await update.message.reply_text(msg.post.ASK_STREET, reply_markup=rm)

    return STREET


async def street(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.street = update.message.text

    rm = ReplyKeyboardMarkup([[b] for b in config.BUILDING_TYPE_VALUES])

    await update.message.reply_text(
        msg.post.ASK_BUILDING_TYPE, reply_markup=rm
    )

    return BUILDING_TYPE


async def building_type(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.building_type = update.message.text

    rm = ReplyKeyboardRemove()
    await update.message.reply_text(msg.post.ASK_FLOOR, reply_markup=rm)

    return FLOOR


async def floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.floor = update.message.text

    await update.message.reply_text(msg.post.ASK_SQUARE)

    return SQUARE


async def square(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.square = update.message.text

    await update.message.reply_text(msg.post.ASK_NUM_OF_ROOMS)

    return NUM_OF_ROOMS


async def num_of_rooms(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.num_of_rooms = update.message.text

    await update.message.reply_text(msg.post.ASK_LAYOUT)

    return LAYOUT


async def layout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.layout = update.message.text

    await update.message.reply_text(msg.post.ASK_DESCRIPTION)

    return DESCRIPTION


async def description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.description = update.message.text

    await update.message.reply_text(msg.post.ASK_SETTLEMENT_DATE)

    return SETTLEMENT_DATE


async def settlement_date(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.settlement_date = update.message.text

    await update.message.reply_text(msg.post.ASK_PRICE)

    return PRICE


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.price = update.message.text

    await update.message.reply_text(msg.post.ASK_CONTACT)

    return CONTACT


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data.contact = update.message.text

    await update.message.reply_text(msg.post.ASK_PHOTO)

    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    file_id = update.message.photo[0].file_id

    data.photo = list({*data.photo, file_id}) if data.photo else [file_id]

    if len(data.photo) < 10:
        return PHOTO

    return OVERVIEW


async def done_photo(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    data = context.user_data["advert"]  # type: ignore
    media = [InputMediaPhoto(p) for p in data.photo]
    media[-1].caption = msg.common.advert_overview(data)
    media[-1].parse_mode = ParseMode.MARKDOWN_V2

    await update.message.reply_media_group(media)  # type: ignore

    return ConversationHandler.END
