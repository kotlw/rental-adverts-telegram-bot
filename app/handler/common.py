"""This file contains common handlers."""
from telegram.ext import filters
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler

import msg.common
import callback.common

start_command = CommandHandler("start", callback.common.start)

kb_select_error = (
    MessageHandler(
        filters.ALL & ~filters.COMMAND,
        callback.common.create_reply_text_callback(
            msg.common.KEYBOARD_SELECT_VALUE_ERROR
        ),
    ),
)

