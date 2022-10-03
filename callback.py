"""This file contains callback functions of the bot."""
from telegram import Update
from telegram.ext import ContextTypes
from telegram.ext import ConversationHandler
from sqlalchemy import select

import db
import model


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("used search command")


# Post advert conversation
(
    DISTINCT,
    STREET,
    BUILDING_TYPE,
    FLOOR,
    SQUARE,
    LAYOUT,
    DESCRIPTION,
    SETTLEMENT_DATE,
    PRICE,
    CONTACT,
    PHOTO,
) = range(11)


async def pa_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "You are going to post advert set distinct"
    )

    return DISTINCT


async def pa_distinct(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        "this is distinct)"
    )
    context.user_data["saved"] = update.message

    return STREET


async def pa_street(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        f"thge data {context.user_data['saved']}"
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    """Cancels and ends the conversation."""

    user = update.message.from_user

    logger.info("User %s canceled the conversation.", user.first_name)

    await update.message.reply_text(

        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()

    )


    return ConversationHandler.END
