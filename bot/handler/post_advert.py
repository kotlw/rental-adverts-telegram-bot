from datetime import datetime
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import ContextTypes
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram import InputMediaPhoto
from telegram import Message
from telegram.constants import ParseMode
from telegram import ReplyKeyboardMarkup
from telegram._utils.types import ReplyMarkup

from bot import app, entity, cfg
from bot.repository import repo


_BUCKET_KEY = "advert"

END = ConversationHandler.END
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


def _make_advert_msg(advert: entity.Advert):

    command_hint = {"submit": "pryniaty", "edit": "redaguvaty"}

    media = [InputMediaPhoto(p) for p in advert.photo]
    media[-1].parse_mode = ParseMode.HTML
    media[-1].caption = cfg.Txt.advert_caption_html(
        advert, command_hints=command_hint
    )

    return media


async def _reply_post(update: Update, advert: entity.Advert) -> None:
    media = _make_advert_msg(advert)
    await update.message.reply_media_group(media)  # type: ignore


class CustomFilters:
    class ValidDate(filters.MessageFilter):
        def filter(self, message: Message):
            try:
                datetime.strptime(message.text, "%d.%m.%y")
            except ValueError:
                return False
            return True

    VALID_DATE = ValidDate()


custom_filters = CustomFilters()


def _create_reply_markup(
    items: list[str], cols: int = 1, is_inline: bool = False
) -> ReplyMarkup:

    result = []
    bucket = []

    for k, v in dict(enumerate(items)).items():
        if len(bucket) == cols:
            result.append(bucket)
            bucket = []

        b = InlineKeyboardButton(v, callback_data=str(k)) if is_inline else v
        bucket.append(b)

    if bucket:
        result.append(bucket)

    wrapper = InlineKeyboardMarkup if is_inline else ReplyKeyboardMarkup
    return wrapper(result)


def _create_callback(
    text: str,
    reply_markup: ReplyMarkup | None = None,
    key: str | None = None,
    next_state: int | None = None,
):
    async def coroutine(
        update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> int | None:

        msg = update.message

        if key:
            data = context.user_data.get(_BUCKET_KEY, {})  # type: ignore
            data[key] = update.message.text
            context.user_data[_BUCKET_KEY] = data  # type: ignore

        await msg.reply_text(text, reply_markup=reply_markup)  # type: ignore

        return next_state

    return coroutine


def _create_handlers(
    key: str,
    handler_filters: filters.BaseFilter,
    error_msg: str,
    text: str,
    reply_markup: ReplyMarkup,
    next_state: int,
) -> list:

    return [
        MessageHandler(
            handler_filters,
            _create_callback(text, reply_markup, key, next_state),
        ),
        MessageHandler(~filters.COMMAND, _create_callback(error_msg)),
    ]


async def post_advert(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int | None:

    msg = update.message

    data = context.user_data.get(_BUCKET_KEY, {})  # type: ignore
    data["user_id"] = msg.chat.id

    rm = _create_reply_markup(cfg.Btn.distincts, 2)
    await msg.reply_text(cfg.Txt.post_advert)  # type: ignore
    await msg.reply_text(cfg.Txt.ask_distinct, reply_markup=rm)  # type: ignore

    return DISTINCT


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    msg = update.message
    file_id = msg.photo[0].file_id

    data = context.user_data.get(_BUCKET_KEY, {})  # type: ignore
    data["photo"] = data.get("photo", [])
    data["photo"].append(file_id)
    context.user_data[_BUCKET_KEY] = data  # type: ignore

    data["user_id"] = msg.chat.id

    if len(data["photo"]) == 10:
        await msg.reply_text(cfg.Txt.photo_max_limit_error)
        await _reply_post(update, entity.Advert(**data))
        return OVERVIEW

    return PHOTO


async def overview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data[_BUCKET_KEY]  # type: ignore
    if not data.get("photo"):
        await update.message.reply_text(cfg.Txt.photo_value_error)
        return PHOTO

    await _reply_post(update, data)

    return OVERVIEW


async def submit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data[_BUCKET_KEY]  # type: ignore
    await repo.advert.upsert(entity.Advert(**data))
    await update.message.reply_text(cfg.Txt.submit_advert)

    return END


post_advert_conversation = ConversationHandler(
    entry_points=[  # type: ignore
        CommandHandler(cfg.Cmd.post_advert, post_advert),  # type: ignore
    ],
    states={  # type: ignore
        DISTINCT: _create_handlers(
            key="distinct",
            handler_filters=filters.Text(cfg.Btn.distincts),
            error_msg=cfg.Txt.select_value_error,
            text=cfg.Txt.ask_street,
            reply_markup=ReplyKeyboardRemove(),
            next_state=STREET,
        ),
        STREET: _create_handlers(
            key="street",
            handler_filters=filters.ALL,
            error_msg=cfg.Txt.text_value_error,
            text=cfg.Txt.ask_building_type,
            reply_markup=_create_reply_markup(cfg.Btn.building_types, 1),
            next_state=BUILDING_TYPE,
        ),
        BUILDING_TYPE: _create_handlers(
            key="building_type",
            handler_filters=filters.Text(cfg.Btn.building_types),
            error_msg=cfg.Txt.select_value_error,
            text=cfg.Txt.ask_floor,
            reply_markup=ReplyKeyboardRemove(),
            next_state=FLOOR,
        ),
        FLOOR: _create_handlers(
            key="floor",
            handler_filters=filters.Regex("^([1-9]|[12][0-7])$"),
            error_msg=cfg.Txt.floor_value_error,
            text=cfg.Txt.ask_square,
            reply_markup=ReplyKeyboardRemove(),
            next_state=SQUARE,
        ),
        SQUARE: _create_handlers(
            key="square",
            handler_filters=filters.ALL,
            error_msg=cfg.Txt.text_value_error,
            text=cfg.Txt.ask_num_of_rooms,
            reply_markup=ReplyKeyboardRemove(),
            next_state=NUM_OF_ROOMS,
        ),
        NUM_OF_ROOMS: _create_handlers(
            key="num_of_rooms",
            handler_filters=filters.Regex("^[1-6]$"),
            error_msg=cfg.Txt.num_of_rooms_value_error,
            text=cfg.Txt.ask_layout,
            reply_markup=ReplyKeyboardRemove(),
            next_state=LAYOUT,
        ),
        LAYOUT: _create_handlers(
            key="layout",
            handler_filters=filters.ALL,
            error_msg=cfg.Txt.text_value_error,
            text=cfg.Txt.ask_description,
            reply_markup=ReplyKeyboardRemove(),
            next_state=DESCRIPTION,
        ),
        DESCRIPTION: _create_handlers(
            key="description",
            handler_filters=filters.ALL,
            error_msg=cfg.Txt.text_value_error,
            text=cfg.Txt.ask_settlement_date,
            reply_markup=ReplyKeyboardRemove(),
            next_state=SETTLEMENT_DATE,
        ),
        SETTLEMENT_DATE: _create_handlers(
            key="settlement_date",
            handler_filters=custom_filters.VALID_DATE,
            error_msg=cfg.Txt.date_value_error,
            text=cfg.Txt.ask_price,
            reply_markup=ReplyKeyboardRemove(),
            next_state=PRICE,
        ),
        PRICE: _create_handlers(
            key="price",
            handler_filters=filters.ALL,
            error_msg=cfg.Txt.text_value_error,
            text=cfg.Txt.ask_contact,
            reply_markup=ReplyKeyboardRemove(),
            next_state=CONTACT,
        ),
        CONTACT: _create_handlers(
            key="contact",
            handler_filters=filters.ALL,
            error_msg=cfg.Txt.text_value_error,
            text=cfg.Txt.ask_photo,
            reply_markup=ReplyKeyboardRemove(),
            next_state=PHOTO,
        ),
        PHOTO: [
            MessageHandler(filters.PHOTO, photo),
            CommandHandler("done", overview),
            MessageHandler(
                ~filters.COMMAND, _create_callback(cfg.Txt.photo_value_error)
            ),
        ],
        OVERVIEW: [
            CommandHandler("submit", submit),
            # CommandHandler("edit", edit_start),
        ],
    },
    fallbacks=[
        CommandHandler(  # type: ignore
            cfg.Cmd.cancel,
            _create_callback(text=cfg.Txt.canceled, next_state=END),
        ),
    ],
)

app.add_handler(post_advert_conversation)
