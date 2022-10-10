from datetime import datetime

from telegram import (
    Message,
    InputMediaPhoto,
    InputMediaAudio,
    InputMediaVideo,
    InputMediaDocument,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import filters
from telegram.constants import ParseMode
from telegram._utils.types import ReplyMarkup

from bot import entity, cfg


def create_advert_media_group(
    advert: entity.Advert,
    command_hints: dict | None = None,
    show_status: bool = False,
) -> list[
    InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo
]:

    media: list[
        InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo
    ]

    media = [InputMediaPhoto(p) for p in advert.photo]
    media[-1].parse_mode = ParseMode.HTML
    media[-1].caption = cfg.Txt.advert_caption_html(
        advert, command_hints=command_hints, show_status=show_status
    )

    return media


def create_reply_markup(
    items: list[str], cols: int = 1, is_inline: bool = False
) -> ReplyMarkup:

    result = []
    bucket = []

    for k, v in dict(enumerate(items)).items():
        if len(bucket) == cols:
            result.append(bucket)
            bucket = []

        b = InlineKeyboardButton(v, callback_data=str(k)) if is_inline else v
        bucket.append(b)

    if bucket:
        result.append(bucket)

    wrapper = InlineKeyboardMarkup if is_inline else ReplyKeyboardMarkup
    return wrapper(result)


class CustomFilters:
    class ValidDate(filters.MessageFilter):
        def filter(self, message: Message) -> bool:
            try:
                datetime.strptime(message.text, "%d.%m.%y")
            except ValueError:
                return False
            return True

    VALID_DATE = ValidDate()


filters = CustomFilters()
