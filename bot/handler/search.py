from collections import defaultdict

from telegram import Update
from telegram import ReplyKeyboardRemove
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import CallbackQueryHandler
from telegram.constants import ParseMode

from bot import app, txt
from bot.helper.telegram import splitted_inline_markup


(CHOOSE_FILTER, DISTINCT, BUILDING_TYPE) = range(3)

(
    CB_DISTINCT,
    CB_BUILDING_TYPE,
    CB_FLOOR,
    CB_NUM_OF_ROOMS,
    CB_PRICE,
    CB_SEARCH,
) = range(6)

DISTINCTS = dict(enumerate(txt.DISTINCT_VALUES))
BUILDING_TYPES = dict(enumerate(txt.BUILDING_TYPE_VALUES))

DEFAULT_MARKUP = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Район", callback_data=str(CB_DISTINCT)),
            InlineKeyboardButton(
                "Тип будинку", callback_data=str(CB_BUILDING_TYPE)
            ),
        ],
        [
            InlineKeyboardButton("Поверх", callback_data=str(CB_FLOOR)),
            InlineKeyboardButton("Ціна", callback_data=str(CB_PRICE)),
        ],
        [
            InlineKeyboardButton(
                "Кількість кімнат", callback_data=str(CB_NUM_OF_ROOMS)
            ),
        ],
        [
            InlineKeyboardButton("Пошук", callback_data=str(CB_SEARCH)),
        ],
    ]
)



def _create_markup(
    items: dict, cols: int, default_value_label: str, back_label: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            *splitted_inline_markup(items, cols),
            [InlineKeyboardButton(default_value_label, callback_data="ALL")],
            [InlineKeyboardButton(back_label, callback_data="BACK")],
        ]
    )

def _create_callback_query(
    callback_id,
    markup_items: dict,
    markup_cols: int,
    default_label: str,
    data_key: str,
    return_value: int,
):
    async def coroutine(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        reply_markup = _create_markup(
            markup_items, markup_cols, default_label, "Повернутись"
        )

        filter_data = context.user_data["filter"]  # type: ignore

        if callback_id == "ALL":
            filter_data[data_key] = []

        elif callback_id != "DEFAULT":

            if markup_items[callback_id] not in filter_data[data_key]:
                filter_data[data_key].append(markup_items[callback_id])
            else:
                filter_data[data_key].remove(markup_items[callback_id])

        await query.edit_message_text(
            text=txt.make_filter_msg(filter_data),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )

        return return_value

    return coroutine


def _create_callback_query_handler_group(
    markup_items: dict,
    markup_cols: int,
    default_label: str,
    data_key: str,
    return_value: int,
):
    return [
        *[
            CallbackQueryHandler(
                _create_callback_query(
                    i,
                    markup_items,
                    markup_cols,
                    default_label,
                    data_key,
                    return_value,
                ),
                pattern="^" + str(i) + "$",
            )
            for i in [*markup_items.keys(), "ALL"]
        ],
        CallbackQueryHandler(search, pattern="^" + "BACK" + "$"),
    ]


async def cancel(update: Update, _) -> int:
    rm = ReplyKeyboardRemove()
    await update.message.reply_text(txt.CANCEL, reply_markup=rm)

    return ConversationHandler.END


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    filter_data = context.user_data.get("filter", defaultdict(list))  # type: ignore
    context.user_data["filter"] = filter_data  # type: ignore

    arguments = {
        "text": txt.make_filter_msg(filter_data),
        "reply_markup": DEFAULT_MARKUP,
        "parse_mode": ParseMode.HTML,
    }

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(**arguments)
        return CHOOSE_FILTER

    await update.message.reply_text(**arguments)

    return CHOOSE_FILTER


distinct = _create_callback_query(
    "DEFAULT", DISTINCTS, 1, "all", "distinct", DISTINCT
)
building_type = _create_callback_query(
    "DEFAULT", BUILDING_TYPES, 1, "all", "building_type", BUILDING_TYPE
)


search_conversation = ConversationHandler(
    entry_points=[CommandHandler("search", search)],  # type: ignore
    states={  # type: ignore
        CHOOSE_FILTER: [
            CallbackQueryHandler(
                distinct, pattern="^" + str(CB_DISTINCT) + "$"
            ),
            CallbackQueryHandler(
                building_type, pattern="^" + str(CB_BUILDING_TYPE) + "$"
            ),
        ],
        DISTINCT: _create_callback_query_handler_group(
            DISTINCTS, 2, "Всі", "distinct", DISTINCT
        ),
        BUILDING_TYPE: _create_callback_query_handler_group(
            BUILDING_TYPES, 1, "Всі", "building_type", BUILDING_TYPE
        ),
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(search_conversation)
