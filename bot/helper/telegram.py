from datetime import datetime

from telegram.ext.filters import MessageFilter
from telegram import Message

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
