from telegram import ReplyKeyboardRemove, Update
from telegram._utils.types import ReplyMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot import app, entity, cfg, helpers
from bot.repository import repo

BUCKET_KEY = "advert"
ADVERTS = "adverts"

END = ConversationHandler.END
DISTINCT = "distinct"
STREET = "street"
BUILDING_TYPE = "building_type"
FLOOR = "floor"
SQUARE = "square"
NUM_OF_ROOMS = "num_of_rooms"
LAYOUT = "layout"
DESCRIPTION = "description"
SETTLEMENT_DATE = "settlement_date"
PRICE = "price"
CONTACT = "contact"
PHOTO = "photo"
OVERVIEW = "overview"
EDIT = "edit"


async def post_advert(update: Update, context) -> str:
    msg = update.message
    context.user_data[EDIT] = False
    context.user_data[BUCKET_KEY] = {"user_id": msg.chat.id}

    rm = helpers.create_reply_markup(cfg.Btn.distincts, 2)
    await msg.reply_text(cfg.Txt.post_advert)
    await msg.reply_text(cfg.Txt.ask_distinct, reply_markup=rm)

    return DISTINCT


async def my_adverts(update: Update, context) -> str:
    msg = update.message

    adverts = await repo.advert.get_user_posts(update.message.chat.id)
    context.user_data[ADVERTS] = adverts

    for i, advert in enumerate(adverts):
        hints = {**cfg.Btn.edit}
        hints = {f"{k}{i}": v for k, v in hints.items()}
        media = helpers.create_advert_media_group(
            advert, command_hints=hints, show_status=True
        )
        await msg.reply_media_group(media)

    return EDIT


def _callback(
    state: str, text: str, reply_markup: ReplyMarkup, next_state: str
):
    async def callback(update: Update, context) -> str:
        msg = update.message
        context.user_data[BUCKET_KEY][state] = msg.text

        if context.user_data[EDIT]:
            return await overview(update, context)

        await msg.reply_text(text, reply_markup=reply_markup)

        return next_state

    return callback


_rm_remove = ReplyKeyboardRemove()
distinct = _callback(DISTINCT, cfg.Txt.ask_street, _rm_remove, STREET)
_rm = helpers.create_reply_markup(cfg.Btn.building_types)
street = _callback(STREET, cfg.Txt.ask_building_type, _rm, BUILDING_TYPE)
building_type = _callback(BUILDING_TYPE, cfg.Txt.ask_floor, _rm_remove, FLOOR)
floor = _callback(FLOOR, cfg.Txt.ask_square, _rm_remove, SQUARE)
square = _callback(SQUARE, cfg.Txt.ask_num_of_rooms, _rm_remove, NUM_OF_ROOMS)
num_of_rooms = _callback(NUM_OF_ROOMS, cfg.Txt.ask_layout, _rm_remove, LAYOUT)
layout = _callback(LAYOUT, cfg.Txt.ask_description, _rm_remove, DESCRIPTION)
description = _callback(
    DESCRIPTION, cfg.Txt.ask_settlement_date, _rm_remove, SETTLEMENT_DATE
)
settlement_date = _callback(
    SETTLEMENT_DATE, cfg.Txt.ask_price, _rm_remove, PRICE
)
price = _callback(PRICE, cfg.Txt.ask_contact, _rm_remove, CONTACT)
contact = _callback(CONTACT, cfg.Txt.ask_photo, _rm_remove, PHOTO)


async def photo(update: Update, context) -> str:
    msg = update.message
    file_id = msg.photo[0].file_id

    data = context.user_data[BUCKET_KEY]
    data["photo"] = data.get("photo", [])
    data["photo"].append(file_id)

    if len(data["photo"]) == 10:
        await msg.reply_text(cfg.Txt.photo_max_limit_error)
        return await overview(update, context)

    return PHOTO


async def overview(update: Update, context) -> str:
    msg = update.message
    data = context.user_data[BUCKET_KEY]

    if not data.get("photo"):
        await msg.reply_text(cfg.Txt.photo_value_error)
        return PHOTO

    advert = entity.Advert(**data)
    hints = {**cfg.Btn.edit, **cfg.Btn.submit}
    media = helpers.create_advert_media_group(advert, command_hints=hints)
    await msg.reply_media_group(media)

    return OVERVIEW


async def submit(update: Update, context) -> int:
    msg = update.message

    data = context.user_data[BUCKET_KEY]
    await repo.advert.upsert(entity.Advert(**data))
    await msg.reply_text(cfg.Txt.submit_advert)

    return END


async def choose_edit_field(update: Update, context) -> str:
    msg = update.message
    context.user_data[EDIT] = True

    rm = helpers.create_reply_markup(list(cfg.Btn.advert_fields.values()))
    await msg.reply_text(cfg.Txt.choose_edit_field, reply_markup=rm)

    return EDIT


async def edit(update: Update, context) -> str:
    msg = update.message

    rm = ReplyKeyboardRemove()
    if msg.text == cfg.Btn.advert_fields["distinct"]:
        rm = helpers.create_reply_markup(cfg.Btn.distincts)
        await msg.reply_text(cfg.Txt.ask_distinct, reply_markup=rm)
        return DISTINCT
    elif msg.text == cfg.Btn.advert_fields["street"]:
        await msg.reply_text(cfg.Txt.ask_street, reply_markup=rm)
        return STREET
    elif msg.text == cfg.Btn.advert_fields["building_type"]:
        rm = helpers.create_reply_markup(cfg.Btn.building_types)
        await msg.reply_text(cfg.Txt.ask_building_type, reply_markup=rm)
        return BUILDING_TYPE
    elif msg.text == cfg.Btn.advert_fields["floor"]:
        await msg.reply_text(cfg.Txt.ask_floor, reply_markup=rm)
        return FLOOR
    elif msg.text == cfg.Btn.advert_fields["square"]:
        await msg.reply_text(cfg.Txt.ask_square, reply_markup=rm)
        return SQUARE
    elif msg.text == cfg.Btn.advert_fields["num_of_rooms"]:
        await msg.reply_text(cfg.Txt.ask_num_of_rooms, reply_markup=rm)
        return NUM_OF_ROOMS
    elif msg.text == cfg.Btn.advert_fields["layout"]:
        await msg.reply_text(cfg.Txt.ask_layout, reply_markup=rm)
        return LAYOUT
    elif msg.text == cfg.Btn.advert_fields["description"]:
        await msg.reply_text(cfg.Txt.ask_description, reply_markup=rm)
        return DESCRIPTION
    elif msg.text == cfg.Btn.advert_fields["settlement_date"]:
        await msg.reply_text(cfg.Txt.ask_settlement_date, reply_markup=rm)
        return SETTLEMENT_DATE
    elif msg.text == cfg.Btn.advert_fields["price"]:
        await msg.reply_text(cfg.Txt.ask_price, reply_markup=rm)
        return PRICE
    elif msg.text == cfg.Btn.advert_fields["contact"]:
        await msg.reply_text(cfg.Txt.ask_contact, reply_markup=rm)
        return CONTACT
    elif msg.text == cfg.Btn.advert_fields["photo"]:
        context.user_data[BUCKET_KEY][PHOTO] = []
        await msg.reply_text(cfg.Txt.ask_photo, reply_markup=rm)
        return PHOTO

    return EDIT


async def cancel(update: Update, _) -> int:
    await update.message.reply_text(cfg.Txt.canceled)
    return END


def _error(msg: str):
    async def callback(update: Update, _) -> None:
        await update.message.reply_text(msg)

    return callback


select_value_error = _error(cfg.Txt.select_value_error)
text_value_error = _error(cfg.Txt.text_value_error)
floor_value_error = _error(cfg.Txt.floor_value_error)
num_of_rooms_value_error = _error(cfg.Txt.num_of_rooms_value_error)
date_value_error = _error(cfg.Txt.date_value_error)
photo_value_error = _error(cfg.Txt.photo_value_error)


post_advert_conv = ConversationHandler(
    entry_points=[  # type: ignore
        CommandHandler(cfg.Cmd.post_advert, post_advert),  # type: ignore
        CommandHandler(cfg.Cmd.my_adverts, my_adverts),  # type: ignore
    ],
    states={  # type: ignore
        DISTINCT: [
            MessageHandler(filters.Text(cfg.Btn.distincts), distinct),
            MessageHandler(~filters.COMMAND, select_value_error),
        ],
        STREET: [
            MessageHandler(filters.ALL, street),
            MessageHandler(~filters.COMMAND, text_value_error),
        ],
        BUILDING_TYPE: [
            MessageHandler(filters.Text(cfg.Btn.building_types), building_type),
            MessageHandler(~filters.COMMAND, select_value_error),
        ],
        FLOOR: [
            MessageHandler(filters.Regex("^([1-9]|[12][0-7])$"), floor),
            MessageHandler(~filters.COMMAND, floor_value_error),
        ],
        SQUARE: [
            MessageHandler(filters.ALL, square),
            MessageHandler(~filters.COMMAND, text_value_error),
        ],
        NUM_OF_ROOMS: [
            MessageHandler(filters.Regex("^[1-6]$"), num_of_rooms),
            MessageHandler(~filters.COMMAND, num_of_rooms_value_error),
        ],
        LAYOUT: [
            MessageHandler(filters.ALL, layout),
            MessageHandler(~filters.COMMAND, text_value_error),
        ],
        DESCRIPTION: [
            MessageHandler(filters.ALL, description),
            MessageHandler(~filters.COMMAND, text_value_error),
        ],
        SETTLEMENT_DATE: [
            MessageHandler(helpers.filters.VALID_DATE, settlement_date),
            MessageHandler(~filters.COMMAND, date_value_error),
        ],
        PRICE: [
            MessageHandler(filters.ALL, price),
            MessageHandler(~filters.COMMAND, text_value_error),
        ],
        CONTACT: [
            MessageHandler(filters.ALL, contact),
            MessageHandler(~filters.COMMAND, text_value_error),
        ],
        PHOTO: [
            MessageHandler(filters.PHOTO, photo),
            CommandHandler("done", overview),
            MessageHandler(~filters.COMMAND, photo_value_error),
        ],
        OVERVIEW: [
            CommandHandler("edit", choose_edit_field),
            CommandHandler("submit", submit),
        ],
        EDIT: [
            MessageHandler(
                filters.Text(list(cfg.Btn.advert_fields.values())),
                edit,
            ),
            MessageHandler(~filters.COMMAND, text_value_error),
        ],
    },
    fallbacks=[CommandHandler(cfg.Cmd.cancel, cancel)],
)

app.add_handler(post_advert_conv)
