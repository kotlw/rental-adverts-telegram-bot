"""This file contains handlers related to /post command."""
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

import config
import msg.post
import msg.common
import callback.common
import callback.post
import handler.common


async def cb_ph(update, context):
    print(update)

conversation = ConversationHandler(
    entry_points=[
        CommandHandler("post", callback.post.entry_point)  # type: ignore
    ],
    states={  # type: ignore
        callback.post.DISTINCT: [
            MessageHandler(
                filters.Text(config.DISTINCT_VALUES),
                callback.post.create_conversation_callback(
                    msg.post.ENTER_STREET,
                    return_value=callback.post.STREET,
                    data_key="advert",
                    data_attr="distinct",
                ),
            ),
            handler.common.kb_select_error,
        ],
        callback.post.STREET: [
            MessageHandler(
                filters.ALL,
                callback.post.create_conversation_callback(
                    msg.post.SELECT_BUILDING_TYPE,
                    reply_markup=ReplyKeyboardMarkup(
                        [[b] for b in config.BUILDING_TYPE_VALUES]
                    ),
                    return_value=callback.post.BUILDING_TYPE,
                    data_key="advert",
                    data_attr="street",
                ),
            )
        ],
        callback.post.BUILDING_TYPE: [
            MessageHandler(
                filters.Text(config.BUILDING_TYPE_VALUES),
                callback.post.create_conversation_callback(
                    msg.post.ENTER_FLOOR,
                    return_value=callback.post.FLOOR,
                    data_key="advert",
                    data_attr="building_type",
                ),
            ),
            handler.common.kb_select_error,
        ],
        callback.post.FLOOR: [
            MessageHandler(
                filters.Regex("^([1-9]|[12][0-7])$"),
                callback.post.create_conversation_callback(
                    msg.post.ENTER_SQUARE,
                    return_value=callback.post.SQUARE,
                    data_key="advert",
                    data_attr="floor",
                ),
            ),
            MessageHandler(
                filters.ALL & ~filters.COMMAND,
                callback.common.create_reply_text_callback(
                    msg.post.FLOOR_ENTER_ERROR
                ),
            ),
        ],
        callback.post.SQUARE: [
            MessageHandler(
                filters.ALL,
                callback.post.create_conversation_callback(
                    msg.post.ENTER_NUM_OF_ROOMS,
                    return_value=callback.post.NUM_OF_ROOMS,
                    data_key="advert",
                    data_attr="square",
                ),
            ),
        ],
        callback.post.NUM_OF_ROOMS: [
            MessageHandler(
                filters.ALL,
                callback.post.create_conversation_callback(
                    msg.post.ENTER_LAYOUT,
                    return_value=callback.post.LAYOUT,
                    data_key="advert",
                    data_attr="num_of_rooms",
                ),
            ),
        ],
        callback.post.LAYOUT: [
            MessageHandler(
                filters.ALL,
                callback.post.create_conversation_callback(
                    msg.post.ENTER_SETTLEMENT_DATE,
                    return_value=callback.post.SETTLEMENT_DATE,
                    data_key="advert",
                    data_attr="layout",
                ),
            ),
        ],
        callback.post.SETTLEMENT_DATE: [
            MessageHandler(
                filters.ALL,
                callback.post.create_conversation_callback(
                    msg.post.ENTER_PRICE,
                    return_value=callback.post.PRICE,
                    data_key="advert",
                    data_attr="settlement_date",
                ),
            ),
        ],
        callback.post.PRICE: [
            MessageHandler(
                filters.ALL,
                callback.post.create_conversation_callback(
                    msg.post.ENTER_CONTACT,
                    return_value=callback.post.CONTACT,
                    data_key="advert",
                    data_attr="price",
                ),
            ),
        ],
        callback.post.CONTACT: [
            MessageHandler(
                filters.ALL,
                callback.post.create_conversation_callback(
                    msg.post.UPLOAD_PHOTO,
                    return_value=callback.post.PHOTO,
                    data_key="advert",
                    data_attr="contact",
                ),
            ),
        ],
        callback.post.PHOTO: [
            MessageHandler(
                filters.ALL,
                cb_ph
            ),
        ],
    },
    fallbacks=[
        CommandHandler(  # type: ignore
            "cancel",
            callback.common.create_reply_text_callback(msg.post.CANCEL),
        ),
    ],
)
