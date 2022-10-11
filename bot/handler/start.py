from telegram.ext import CommandHandler
from telegram import Update

import cfg
import entity
from repository import repo


async def start(update: Update, _):
    chat = update.message.chat
    user = entity.User(
        id=chat.id, username=chat.username, first_name=chat.first_name
    )

    await repo.user.upsert(user)
    await update.message.reply_text("Hello user")


start_command = CommandHandler(cfg.Cmd.start, start)
