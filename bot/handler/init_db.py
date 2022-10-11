from telegram import Update
from telegram.ext import CommandHandler

from bot import app
from bot.repository import repo


async def init_db(update: Update, _):
    await repo.user.init_db()
    await update.message.reply_text("Initialized")


init_db_command = CommandHandler("init_db", init_db)

app.add_handler(init_db_command)
