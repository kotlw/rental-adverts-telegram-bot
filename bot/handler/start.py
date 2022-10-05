from telegram.ext import CommandHandler
from telegram import Update

from bot import app
from bot import entity, db_gateway


async def start(update: Update, _):
    user = entity.User(
        id=update.message.chat.id,
        username=update.message.chat.username,
        first_name=update.message.chat.first_name,
    )

    await db_gateway.upsert_user(user)
    await update.message.reply_text("Hello user")


start_command = CommandHandler("start", start)

app.add_handler(start_command)
