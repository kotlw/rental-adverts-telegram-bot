from datetime import datetime

from telegram.ext.filters import MessageFilter
from telegram import Message
from telegram import InlineKeyboardButton


class CustomFilters:
    class ValidDate(MessageFilter):
        def filter(self, message: Message):
            try:
                datetime.strptime(message.text, "%d.%m.%y")
            except ValueError:
                return False
            return True

    VALID_DATE = ValidDate()


custom_filters = CustomFilters()


def splitted_inline_markup(
    items: dict, cols: int
) -> list[list[InlineKeyboardButton]]:

    result = []
    bucket = []

    for k, v in items.items():
        if len(bucket) == cols:
            result.append(bucket)
            bucket = []
        bucket.append(InlineKeyboardButton(v, callback_data=str(k)))

    if bucket:
        result.append(bucket)

    return result

