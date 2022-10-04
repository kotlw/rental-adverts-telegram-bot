"""This file contains handlers related to /post command."""
from telegram import ReplyKeyboardRemove
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

import config
import msg.post
import msg.common
import callback.post
import callback.common
import handler.common


conversation = ConversationHandler(
    entry_points=[
        CommandHandler("post", callback.post.entry_point)  # type: ignore
    ],
    states={  # type: ignore
        callback.post.DISTINCT: [
            MessageHandler(
                filters.Text(config.DISTINCT_VALUES),
                callback.post.distinct,
            ),
            handler.common.error(msg.common.KEYBOARD_SELECT_VALUE_ERROR),
        ],
        callback.post.STREET: [
            MessageHandler(filters.Text(), callback.post.street)
        ],
        callback.post.BUILDING_TYPE: [
            MessageHandler(
                filters.Text(config.BUILDING_TYPE_VALUES),
                callback.post.building_type,
            ),
            handler.common.error(msg.common.KEYBOARD_SELECT_VALUE_ERROR),
        ],
        callback.post.FLOOR: [
            MessageHandler(
                filters.Regex("^([1-9]|[12][0-7])$"),
                callback.post.floor,
            ),
            handler.common.error(msg.post.FLOOR_VALUE_ERROR),
        ],
        callback.post.SQUARE: [
            MessageHandler(filters.Text(), callback.post.square),
        ],
        callback.post.NUM_OF_ROOMS: [
            MessageHandler(
                filters.Regex("^[1-6]$"), callback.post.num_of_rooms
            ),
            handler.common.error(msg.post.NUM_OF_ROOMS_VALUE_ERROR),
        ],
        callback.post.LAYOUT: [
            MessageHandler(filters.Text(), callback.post.layout),
        ],
        callback.post.DESCRIPTION: [
            MessageHandler(filters.Text(), callback.post.description),
        ],
        callback.post.SETTLEMENT_DATE: [
            MessageHandler(
                filters.Regex(
                    "^[0-9]{1,2}\\/[0-9]{1,2}\\/[0-9]{2}$"
                ),
                callback.post.settlement_date,
            ),
            handler.common.error(msg.post.DATE_VALUE_ERROR),
        ],
        callback.post.PRICE: [
            MessageHandler(filters.Text(), callback.post.price),
        ],
        callback.post.CONTACT: [
            MessageHandler(filters.Text(), callback.post.contact),
        ],
        callback.post.PHOTO: [
            MessageHandler(filters.PHOTO, callback.post.photo),
            CommandHandler("done", callback.post.done_photo),
            handler.common.error(msg.post.PHOTO_VALUE_ERROR),
        ],
    },
    fallbacks=[
        CommandHandler(  # type: ignore
            "cancel",
            callback.common.create_reply_text_callback(
                msg.post.CANCEL, reply_markup=ReplyKeyboardRemove()
            ),
        ),
    ],
)
