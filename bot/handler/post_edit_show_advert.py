from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram._utils.types import ReplyMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot import app, entity, cfg, helpers
from bot.repository import repo
from bot.cfg import (
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
)

END = ConversationHandler.END
BUCKET_KEY, ADVERTS, OVERVIEW, EDIT, MY_ADVERTS_OVERVIEW = range(5)


async def post_advert(update: Update, context) -> str:
    msg = update.message
    user_data = context.user_data

    user_data[EDIT] = False
    user_data[BUCKET_KEY] = {"user_id": msg.chat.id}

    kb = helpers.prepare_keyboard(cfg.Btn.distinct_fields, 2)
    rm = ReplyKeyboardMarkup(kb)
    await msg.reply_text(cfg.Txt.post_advert)
    await msg.reply_text(cfg.Txt.ask_distinct, reply_markup=rm)

    return DISTINCT


async def my_adverts(update: Update, context) -> int | str:
    msg = update.message
    user_data = context.user_data

    user_data[ADVERTS] = await repo.advert.get_user_adverts(msg.chat.id)

    if not user_data[ADVERTS]:
        await msg.reply_text(cfg.Txt.no_user_adverts_found)
        return END

    for i, advert in enumerate(user_data[ADVERTS]):
        hints = {**cfg.Btn.edit, **cfg.Btn.delete}
        indexed_hints = {f"{k}{i+1}": v for k, v in hints.items()}

        media = helpers.create_advert_media_group(
            advert, command_hints=indexed_hints, show_status=True
        )

        await msg.reply_media_group(media)

    return MY_ADVERTS_OVERVIEW


def _callback(
    state: str, text: str, reply_markup: ReplyMarkup, next_state: str
):
    async def callback(update: Update, context) -> int | str:
        msg = update.message
        user_data = context.user_data

        user_data[BUCKET_KEY][state] = msg.text

        if user_data[EDIT]:
            return await overview(update, context)

        await msg.reply_text(text, reply_markup=reply_markup)

        return next_state

    return callback


_rm_remove = ReplyKeyboardRemove()
distinct = _callback(DISTINCT, cfg.Txt.ask_street, _rm_remove, STREET)
_kb = helpers.prepare_keyboard(cfg.Btn.building_type_fields)
_rm = ReplyKeyboardMarkup(_kb)
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


async def photo(update: Update, context) -> int | str:
    msg = update.message
    user_data = context.user_data

    file_id = msg.photo[0].file_id
    data = user_data[BUCKET_KEY]
    data[PHOTO] = data.get(PHOTO, [])
    data[PHOTO].append(file_id)

    if len(data[PHOTO]) == 10:
        await msg.reply_text(cfg.Txt.photo_max_limit_error)
        return await overview(update, context)

    return PHOTO


async def overview(update: Update, context) -> int | str:
    msg = update.message
    user_data = context.user_data

    data = user_data[BUCKET_KEY]

    # if no photoes were added and /done command is pressed
    if not data.get(PHOTO):
        await msg.reply_text(cfg.Txt.photo_value_error)
        return PHOTO

    rm = ReplyKeyboardRemove()
    await msg.reply_text(cfg.Txt.advert_overview, reply_markup=rm)

    advert = entity.Advert.from_dict(data)
    hints = {**cfg.Btn.edit, **cfg.Btn.submit, **cfg.Btn.cancel}
    media = helpers.create_advert_media_group(advert, command_hints=hints)
    await msg.reply_media_group(media)

    return OVERVIEW


async def submit(update: Update, context) -> int:
    msg = update.message
    user_data = context.user_data

    data = user_data[BUCKET_KEY]
    await repo.advert.upsert(entity.Advert.from_dict(data))
    await msg.reply_text(cfg.Txt.submit_advert)

    return END


async def choose_edit_field(update: Update, context) -> int | str:
    msg = update.message
    user_data = context.user_data

    user_data[EDIT] = True

    kb = helpers.prepare_keyboard(cfg.Btn.advert_fields)
    rm = ReplyKeyboardMarkup(kb)
    await msg.reply_text(cfg.Txt.choose_edit_field, reply_markup=rm)

    return EDIT


async def choose_edit_advert(update: Update, context) -> int | str:
    msg = update.message
    user_data = context.user_data

    index = int(msg.text.replace(f"/{cfg.Cmd.edit}", "")) - 1
    data = user_data[BUCKET_KEY] = user_data[ADVERTS][index].dict()

    if data["status"] == entity.AdvertStatusEnum.APPROVED:
        await msg.reply_text(cfg.Txt.cant_edit)
        return END

    await overview(update, context)
    return await choose_edit_field(update, context)


async def choose_delete_advert(update: Update, context) -> int:
    msg = update.message
    user_data = context.user_data

    index = int(msg.text.replace(f"/{cfg.Cmd.delete}", "")) - 1
    advert = user_data[ADVERTS][index]

    await repo.advert.remove(advert)
    await update.message.reply_text(cfg.Txt.deleted)

    return END


async def edit(update: Update, context) -> int | str:
    msg = update.message
    user_data = context.user_data

    rm = ReplyKeyboardRemove()

    if msg.text == cfg.Btn.advert_fields[DISTINCT]:
        kb = helpers.prepare_keyboard(cfg.Btn.distinct_fields)
        rm = ReplyKeyboardMarkup(kb)
        await msg.reply_text(cfg.Txt.ask_distinct, reply_markup=rm)
        return DISTINCT
    elif msg.text == cfg.Btn.advert_fields[STREET]:
        await msg.reply_text(cfg.Txt.ask_street, reply_markup=rm)
        return STREET
    elif msg.text == cfg.Btn.advert_fields[BUILDING_TYPE]:
        kb = helpers.prepare_keyboard(cfg.Btn.building_type_fields)
        rm = ReplyKeyboardMarkup(kb)
        await msg.reply_text(cfg.Txt.ask_building_type, reply_markup=rm)
        return BUILDING_TYPE
    elif msg.text == cfg.Btn.advert_fields[FLOOR]:
        await msg.reply_text(cfg.Txt.ask_floor, reply_markup=rm)
        return FLOOR
    elif msg.text == cfg.Btn.advert_fields[SQUARE]:
        await msg.reply_text(cfg.Txt.ask_square, reply_markup=rm)
        return SQUARE
    elif msg.text == cfg.Btn.advert_fields[NUM_OF_ROOMS]:
        await msg.reply_text(cfg.Txt.ask_num_of_rooms, reply_markup=rm)
        return NUM_OF_ROOMS
    elif msg.text == cfg.Btn.advert_fields[LAYOUT]:
        await msg.reply_text(cfg.Txt.ask_layout, reply_markup=rm)
        return LAYOUT
    elif msg.text == cfg.Btn.advert_fields[DESCRIPTION]:
        await msg.reply_text(cfg.Txt.ask_description, reply_markup=rm)
        return DESCRIPTION
    elif msg.text == cfg.Btn.advert_fields[SETTLEMENT_DATE]:
        await msg.reply_text(cfg.Txt.ask_settlement_date, reply_markup=rm)
        return SETTLEMENT_DATE
    elif msg.text == cfg.Btn.advert_fields[PRICE]:
        await msg.reply_text(cfg.Txt.ask_price, reply_markup=rm)
        return PRICE
    elif msg.text == cfg.Btn.advert_fields[CONTACT]:
        await msg.reply_text(cfg.Txt.ask_contact, reply_markup=rm)
        return CONTACT
    elif msg.text == cfg.Btn.advert_fields[PHOTO]:
        user_data[BUCKET_KEY][PHOTO] = []
        await msg.reply_text(cfg.Txt.ask_photo, reply_markup=rm)
        return PHOTO

    return EDIT


async def cancel(update: Update, _) -> int:
    rm = ReplyKeyboardRemove()
    await update.message.reply_text(cfg.Txt.canceled, reply_markup=rm)
    return END


def _error(msg: str):
    async def callback(update: Update, _) -> None:
        await update.message.reply_text(msg)

    return callback


select_value_error = _error(cfg.Txt.select_value_error)
text_value_error = _error(cfg.Txt.text_value_error)
number_value_error = _error(cfg.Txt.number_value_error)
floor_value_error = _error(cfg.Txt.floor_value_error)
num_of_rooms_value_error = _error(cfg.Txt.num_of_rooms_value_error)
date_value_error = _error(cfg.Txt.date_value_error)
photo_value_error = _error(cfg.Txt.photo_value_error)


post_edit_show_advert_conv = ConversationHandler(
    entry_points=[
        CommandHandler(cfg.Cmd.post_advert, post_advert),
        CommandHandler(cfg.Cmd.my_adverts, my_adverts),
    ],
    states={
        DISTINCT: [
            MessageHandler(
                filters.Text(list(cfg.Btn.distinct_fields.values())), distinct
            ),
            MessageHandler(~filters.COMMAND, select_value_error),
        ],
        STREET: [
            MessageHandler(filters.ALL, street),
            MessageHandler(~filters.COMMAND, text_value_error),
        ],
        BUILDING_TYPE: [
            MessageHandler(
                filters.Text(list(cfg.Btn.building_type_fields.values())),
                building_type,
            ),
            MessageHandler(~filters.COMMAND, select_value_error),
        ],
        FLOOR: [
            MessageHandler(filters.Regex("^([1-9]|[12][0-7])$"), floor),
            MessageHandler(~filters.COMMAND, floor_value_error),
        ],
        SQUARE: [
            MessageHandler(filters.Regex("^[1-9][0-9]*$"), square),
            MessageHandler(~filters.COMMAND, number_value_error),
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
            MessageHandler(filters.Regex("^[1-9][0-9]*$"), price),
            MessageHandler(~filters.COMMAND, number_value_error),
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
        MY_ADVERTS_OVERVIEW: [
            MessageHandler(
                filters.Regex(f"^\\/{cfg.Cmd.edit}[0-9]$"), choose_edit_advert
            ),
            MessageHandler(
                filters.Regex(f"^\\/{cfg.Cmd.delete}[0-9]$"),
                choose_delete_advert,
            ),
        ],
    },
    fallbacks=[CommandHandler(cfg.Cmd.cancel, cancel)],
)

app.add_handler(post_edit_show_advert_conv)
