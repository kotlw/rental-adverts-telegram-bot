from telegram import Update
from telegram import ReplyKeyboardRemove
from telegram import ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

from bot import app, txt, entity
from bot.helper.telegram import custom_filters


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
    rm = ReplyKeyboardMarkup([[b] for b in txt.DISTINCT_VALUES])

    await update.message.reply_text(txt.POST_START)
    await update.message.reply_text(txt.ASK_DISTINCT, reply_markup=rm)

    context.user_data["advert"] = {  # type: ignore
        "user_id": update.message.chat.id
    }

    return DISTINCT


async def distinct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["distinct"] = update.message.text

    rm = ReplyKeyboardRemove()
    await update.message.reply_text(txt.ASK_STREET, reply_markup=rm)

    return STREET


async def street(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["street"] = update.message.text

    rm = ReplyKeyboardMarkup([[b] for b in txt.BUILDING_TYPE_VALUES])

    await update.message.reply_text(txt.ASK_BUILDING_TYPE, reply_markup=rm)

    return BUILDING_TYPE


async def building_type(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["building_type"] = update.message.text

    rm = ReplyKeyboardRemove()
    await update.message.reply_text(txt.ASK_FLOOR, reply_markup=rm)

    return FLOOR


async def floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["floor"] = update.message.text

    await update.message.reply_text(txt.ASK_SQUARE)

    return SQUARE


async def square(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["square"] = update.message.text

    await update.message.reply_text(txt.ASK_NUM_OF_ROOMS)

    return NUM_OF_ROOMS


async def num_of_rooms(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["num_of_rooms"] = update.message.text

    await update.message.reply_text(txt.ASK_LAYOUT)

    return LAYOUT


async def layout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["layout"] = update.message.text

    await update.message.reply_text(txt.ASK_DESCRIPTION)

    return DESCRIPTION


async def description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["description"] = update.message.text

    await update.message.reply_text(txt.ASK_SETTLEMENT_DATE)

    return SETTLEMENT_DATE


async def settlement_date(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["settlement_date"] = update.message.text

    await update.message.reply_text(txt.ASK_PRICE)

    return PRICE


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["price"] = update.message.text

    await update.message.reply_text(txt.ASK_CONTACT)

    return CONTACT


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    data["contact"] = update.message.text

    await update.message.reply_text(txt.ASK_PHOTO)

    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    file_id = update.message.photo[0].file_id

    data["photo"] = data.get("photo", [file_id])
    data["photo"] = list({*data["photo"], file_id})

    if len(data["photo"]) == 10:
        await update.message.reply_text(txt.PHOTO_MAX_LIMIT_ERROR)

        media = txt.make_advert_post(entity.Advert.parse_obj(data))
        await update.message.reply_media_group(media)

        return OVERVIEW

    return PHOTO


async def overview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    data = context.user_data["advert"]  # type: ignore
    media = txt.make_advert_post(entity.Advert.parse_obj(data))
    await update.message.reply_media_group(media)

    return ConversationHandler.END


async def kb_select_error(update: Update, _) -> None:
    await update.message.reply_text(txt.KEYBOARD_SELECT_VALUE_ERROR)


async def floor_value_error(update: Update, _) -> None:
    await update.message.reply_text(txt.FLOOR_VALUE_ERROR)


async def date_value_error(update: Update, _) -> None:
    await update.message.reply_text(txt.DATE_VALUE_ERROR)


async def photo_value_error(update: Update, _) -> None:
    await update.message.reply_text(txt.PHOTO_VALUE_ERROR)


async def num_of_rooms_value_error(update: Update, _) -> None:
    await update.message.reply_text(txt.NUM_OF_ROOMS_VALUE_ERROR)


async def text_input_error(update: Update, _) -> None:
    await update.message.reply_text(txt.TEXT_INPUT_ERROR)


async def invalid_date(update: Update, _) -> None:
    await update.message.reply_text("invalid date")


async def cancel(update: Update, _) -> int:
    rm = ReplyKeyboardRemove()
    await update.message.reply_text(txt.CANCEL, reply_markup=rm)

    return ConversationHandler.END


post_conversation = ConversationHandler(
    entry_points=[CommandHandler("post", entry_point)],  # type: ignore
    states={  # type: ignore
        DISTINCT: [
            MessageHandler(filters.Text(txt.DISTINCT_VALUES), distinct),
            MessageHandler(~filters.COMMAND, kb_select_error),
        ],
        STREET: [
            MessageHandler(filters.Text(), street),
            MessageHandler(~filters.COMMAND, text_input_error),
        ],
        BUILDING_TYPE: [
            MessageHandler(
                filters.Text(txt.BUILDING_TYPE_VALUES),
                building_type,
            ),
            MessageHandler(~filters.COMMAND, kb_select_error),
        ],
        FLOOR: [
            MessageHandler(filters.Regex("^([1-9]|[12][0-7])$"), floor),
            MessageHandler(~filters.COMMAND, floor_value_error),
        ],
        SQUARE: [
            MessageHandler(filters.Text(), square),
            MessageHandler(~filters.COMMAND, text_input_error),
        ],
        NUM_OF_ROOMS: [
            MessageHandler(filters.Regex("^[1-6]$"), num_of_rooms),
            MessageHandler(~filters.COMMAND, num_of_rooms_value_error),
        ],
        LAYOUT: [
            MessageHandler(filters.Text(), layout),
            MessageHandler(~filters.COMMAND, text_input_error),
        ],
        DESCRIPTION: [
            MessageHandler(filters.Text(), description),
            MessageHandler(~filters.COMMAND, text_input_error),
        ],
        SETTLEMENT_DATE: [
            MessageHandler(custom_filters.VALID_DATE, settlement_date),
            MessageHandler(~filters.COMMAND, date_value_error),
        ],
        PRICE: [
            MessageHandler(filters.Text(), price),
            MessageHandler(~filters.COMMAND, text_input_error),
        ],
        CONTACT: [
            MessageHandler(filters.Text(), contact),
            MessageHandler(~filters.COMMAND, text_input_error),
        ],
        PHOTO: [
            MessageHandler(filters.PHOTO, photo),
            CommandHandler("done", overview),
            MessageHandler(filters.ALL & ~filters.COMMAND, photo_value_error),
        ],
        OVERVIEW: [
            MessageHandler(filters.PHOTO, overview),
            CommandHandler("done", overview),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(post_conversation)
