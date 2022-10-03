""" Application entry point. """
from telegram.ext import ApplicationBuilder
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import filters

import config
import callback


app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_handler(CommandHandler("start", callback.start))
# app.add_handler(CommandHandler("search", callback.search))

conv = ConversationHandler(
    entry_points=[CommandHandler("post", callback.pa_start)],  # type: ignore
    states={  # type: ignore
        callback.DISTINCT: [
            MessageHandler(
                filters.Text(config.DISTINCT_VALUES), callback.pa_distinct
            )
        ],
        callback.STREET: [MessageHandler(filters.ALL, callback.pa_street)],
        callback.BUILDING_TYPE: [
            MessageHandler(
                filters.Text(config.BUILDING_TYPE_VALUES),
                callback.pa_building_type,
            )
        ],
        callback.FLOOR: [
            MessageHandler(
                filters.Regex("^([1-9]|[12][0-7])$"),
                callback.pa_floor,
            )
        ],
        callback.SQUARE: [
            MessageHandler(
                filters.ALL,
                callback.pa_square,
            )
        ],
        callback.NUM_OF_ROOMS: [
            MessageHandler(
                filters.ALL,
                callback.pa_num_of_rooms,
            )
        ],
        callback.LAYOUT: [
            MessageHandler(
                filters.ALL,
                callback.pa_layout,
            )
        ],
        callback.DESCRIPTION: [
            MessageHandler(
                filters.ALL,
                callback.pa_description,
            )
        ],
        callback.SETTLEMENT_DATE: [
            MessageHandler(
                filters.ALL,
                callback.pa_settlement_date,
            )
        ],
    },
    fallbacks=[
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            callback.keyboard_select_value_error,
        ),
        CommandHandler("cancel", callback.cancel),
    ],  # type: ignore
)


app.add_handler(conv)


app.run_polling()
