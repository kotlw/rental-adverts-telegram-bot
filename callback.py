"""This file contains callback functions of the bot."""
from telegram import Update
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from sqlalchemy import select

import db
import model
import config


# Common callbacks
async def start(update: Update, _) -> None:
    """Stores user data, and sends welcome message."""

    chat = update.message.chat

    async with db.async_session() as session:
        result = await session.execute(
            select([model.User.id]).where(model.User.id == chat.id)
        )
        if not result.fetchone():
            async with session.begin():
                session.add(
                    model.User(
                        id=chat.id,
                        username=chat.username,
                        first_name=chat.first_name,
                    )
                )

        await session.commit()

    await db.engine.dispose()


async def search(update: Update, _) -> None:
    await update.message.reply_text("used search command")


async def keyboard_select_value_error(update: Update, _) -> None:
    """Shows error message."""
    await update.message.reply_text(config.KEYBOARD_SELECT_VALUE_ERROR_MSG)


async def cancel(update: Update, _) -> int:
    """Cancels and ends the conversation."""

    await update.message.reply_text(
        config.PA_CANCEL_MSG,
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


# Post advert conversation callbacks.
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


async def pa_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts posting advert conversation."""

    await update.message.reply_text(config.PA_START_MESSAGE)
    await update.message.reply_text(
        config.PA_SELECT_DISTINCT_MSG,
        reply_markup=ReplyKeyboardMarkup(
            [[b] for b in config.DISTINCT_VALUES]
        ),
    )

    advert = model.Advert(status="pending", user_id=update.message.chat_id)
    context.user_data["advert"] = advert  # type: ignore

    return DISTINCT


async def pa_distinct(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Saves distinct asks for street."""

    advert = context.user_data["advert"]  # type: ignore
    advert.distinct = update.message.text

    await update.message.reply_text(
        config.PA_ENTER_STREET_MSG, reply_markup=ReplyKeyboardRemove()
    )

    return STREET


async def pa_street(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves street asks for building type."""

    advert = context.user_data["advert"]  # type: ignore
    advert.street = update.message.text

    await update.message.reply_text(
        config.PA_SELECT_BUILDING_TYPE_MSG,
        reply_markup=ReplyKeyboardMarkup(
            [[b] for b in config.BUILDING_TYPE_VALUES]
        ),
    )

    return BUILDING_TYPE


async def pa_building_type(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Saves building type asks for floor."""

    advert = context.user_data["advert"]  # type: ignore
    advert.building_type = update.message.text

    await update.message.reply_text(config.PA_ENTER_FLOOR_MSG)

    return FLOOR


async def pa_floor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves floor asks for square."""

    advert = context.user_data["advert"]  # type: ignore
    advert.floor = update.message.text

    await update.message.reply_text(config.PA_ENTER_SQUARE)

    return SQUARE


async def pa_square(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves square asks for number of rooms."""

    advert = context.user_data["advert"]  # type: ignore
    advert.square = update.message.text

    await update.message.reply_text(config.PA_ENTER_NUM_OF_ROOMS)

    return NUM_OF_ROOMS


async def pa_num_of_rooms(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Saves floor asks for square."""

    advert = context.user_data["advert"]  # type: ignore
    advert.num_of_rooms = update.message.text

    await update.message.reply_text(config.PA_ENTER_LAYOUT)

    return LAYOUT


async def pa_layout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves layout asks for description."""

    advert = context.user_data["advert"]  # type: ignore
    advert.layout = update.message.text

    await update.message.reply_text(config.PA_ENTER_DESCRIPTION)

    return DESCRIPTION


async def pa_description(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Saves description asks for settlement date."""

    advert = context.user_data["advert"]  # type: ignore
    advert.description = update.message.text

    await update.message.reply_text(config.PA_ENTER_SETTLEMENT_DATE)

    return SETTLEMENT_DATE


async def pa_settlement_date(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Saves settlement date asks for price."""

    advert = context.user_data["advert"]  # type: ignore
    advert.floor = update.message.text
    print(advert.__dict__)

    await update.message.reply_text("thats it for now")

    return ConversationHandler.END
