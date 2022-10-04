""" Application entry point. """
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram import InputMediaPhoto
from telegram.constants import ParseMode


import config
import handler.common
import handler.post


# async def han(update: Update, cnt):
#     await update.message.reply_text("<strong>hello world!</strong> nive to e", parse_mode=ParseMode.HTML)


app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_handler(handler.common.start_command)
app.add_handler(handler.post.conversation)
# app.add_handler(MessageHandler(filters.ALL, han))

app.run_polling()
