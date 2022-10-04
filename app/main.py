""" Application entry point. """
from telegram.ext import ApplicationBuilder, MessageHandler, filters

import config
import handler.common
import handler.post

app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_handler(handler.common.start_command)
app.add_handler(handler.post.conversation)

async def ph(update, _):
    print(update)

app.add_handler(MessageHandler(filters.ALL, ph))

app.run_polling()
