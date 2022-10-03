""" Application entry point. """
from telegram import Update
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

import config
import callback


app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_handler(CommandHandler("start", callback.start))
app.add_handler(CommandHandler("search", callback.search))

conv = ConversationHandler(
    entry_points=[CommandHandler("post_advert", callback.pa_start)],
    states={
        callback.DISTINCT: [MessageHandler(filters.ALL, callback.pa_distinct)],
        callback.STREET: [MessageHandler(filters.ALL, callback.pa_street)],
    },
    fallbacks=[CommandHandler("cancel", callback.cancel)],
)


app.add_handler(conv)


app.run_polling()
