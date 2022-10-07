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

from bot import app, txt, entity, db_gateway
from bot.helper.telegram import splitted_inline_markup


(
    CHOOSE_FILTER,
    DISTINCT,
    BUILDING_TYPE,
    FLOOR,
    PRICE,
    NUM_OF_ROOMS,
    PRICE_FROM,
    PRICE_TO,
    FLOOR_FROM,
    FLOOR_TO,
    NUM_OF_ROOMS_FROM,
    NUM_OF_ROOMS_TO,
) = range(12)

(
    CB_DISTINCT,
    CB_BUILDING_TYPE,
    CB_FLOOR,
    CB_NUM_OF_ROOMS,
    CB_PRICE,
    CB_SEARCH,
    CB_FROM,
    CB_TO,
) = range(8)

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
    items: dict,
    cols: int,
    default_value_label: str,
    back_label: str,
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


def _create_price_callback(
    callback_id,
    markup_items: dict,
    markup_cols: int,
    return_value: int,
    data_key: str,
    is_price_from: bool,
):
    async def coroutine(update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply_markup = InlineKeyboardMarkup(
            [
                *splitted_inline_markup(markup_items, markup_cols),
                [InlineKeyboardButton("Повернутись", callback_data="BACK")],
            ]
        )

        filter_data = context.user_data["filter"]  # type: ignore
        if callback_id != "DEFAULT":
            p = filter_data[data_key]
            target = markup_items[callback_id]
            if is_price_from:
                if target == "<-":
                    if not p:
                        p = ["0", "0"]
                    elif len(p[0]) == 1:
                        p[0] = "0"
                    else:
                        p[0] = p[0][:-1]
                else:

                    if not p:
                        p = [target, "0"]
                    elif p[0] == "0":
                        p[0] = target
                    else:
                        p[0] += target
            else:

                if target == "<-":
                    if not p:
                        p = ["0", "0"]
                    elif len(p[1]) == 1:
                        p[1] = "0"
                    else:
                        p[1] = p[1][:-1]
                else:
                    if not p:
                        p = ["0", target]
                    elif p[1] == "0":
                        p[1] = target
                    else:
                        p[1] += target
            filter_data[data_key] = p

        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            text=txt.make_filter_msg(filter_data),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )

        return return_value

    return coroutine


def _create_price_callback_query_handler_group(
    markup_items: dict,
    markup_cols: int,
    return_value: int,
    data_key: str,
    is_price_from: bool,
    back_callback,
):
    return [
        *[
            CallbackQueryHandler(
                _create_price_callback(
                    i,
                    markup_items,
                    markup_cols,
                    return_value,
                    data_key,
                    is_price_from,
                ),
                pattern="^" + str(i) + "$",
            )
            for i in [*markup_items.keys()]
        ],
        CallbackQueryHandler(back_callback, pattern="^" + "BACK" + "$"),
    ]


async def cancel(update: Update, _) -> int:
    rm = ReplyKeyboardRemove()
    await update.message.reply_text(txt.CANCEL, reply_markup=rm)

    return ConversationHandler.END


distinct = _create_callback_query(
    "DEFAULT", DISTINCTS, 2, "Всі", "distinct", DISTINCT
)
building_type = _create_callback_query(
    "DEFAULT", BUILDING_TYPES, 1, "Всі", "building_type", BUILDING_TYPE
)

price = _create_callback_query(
    "DEFAULT",
    {CB_FROM: "Від", CB_TO: "До"},
    2,
    "Будь-яка",
    "price",
    PRICE,
)
price_all = _create_callback_query(
    "ALL",
    {CB_FROM: "Від", CB_TO: "До"},
    2,
    "Будь-яка",
    "price",
    PRICE,
)
price_from = _create_price_callback(
    "DEFAULT",
    dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
    3,
    PRICE_FROM,
    "price",
    True,
)
price_to = _create_price_callback(
    "DEFAULT",
    dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
    3,
    PRICE_TO,
    "price",
    False,
)


floor = _create_callback_query(
    "DEFAULT",
    {CB_FROM: "Від", CB_TO: "До"},
    2,
    "Будь-який",
    "floor",
    FLOOR,
)

floor_all = _create_callback_query(
    "ALL",
    {CB_FROM: "Від", CB_TO: "До"},
    2,
    "Будь-який",
    "floor",
    FLOOR,
)
floor_from = _create_price_callback(
    "DEFAULT",
    dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
    3,
    FLOOR_FROM,
    "floor",
    True,
)
floor_to = _create_price_callback(
    "DEFAULT",
    dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
    3,
    FLOOR_TO,
    "floor",
    False,
)

num_of_rooms = _create_callback_query(
    "DEFAULT",
    {CB_FROM: "Від", CB_TO: "До"},
    2,
    "Будь-яка",
    "num_of_rooms",
    NUM_OF_ROOMS,
)
num_of_rooms_all = _create_callback_query(
    "ALL",
    {CB_FROM: "Від", CB_TO: "До"},
    2,
    "Будь-яка",
    "num_of_rooms",
    NUM_OF_ROOMS,
)
num_of_rooms_from = _create_price_callback(
    "DEFAULT",
    dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
    3,
    NUM_OF_ROOMS_FROM,
    "num_of_rooms",
    True,
)
num_of_rooms_to = _create_price_callback(
    "DEFAULT",
    dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
    3,
    NUM_OF_ROOMS_TO,
    "num_of_rooms",
    False,
)


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

async def search_submit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    query = update.callback_query
    await query.answer()

    filter_data = context.user_data.get("filter", defaultdict(list))  # type: ignore
    filter_data["status"] = entity.StatusEnum.APPROVED
    print(filter_data)

    adverts = await db_gateway.get_posts_by_filter(filter_data)
    if adverts:
        for a in adverts:
            media = txt.make_advert_post(a)
            await query.message.reply_media_group(media)

    else:
        await query.message.reply_text(txt.NO_ADVERTS_FOUND)

    return ConversationHandler.END

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
            CallbackQueryHandler(price, pattern="^" + str(CB_PRICE) + "$"),
            CallbackQueryHandler(floor, pattern="^" + str(CB_FLOOR) + "$"),
            CallbackQueryHandler(
                num_of_rooms, pattern="^" + str(CB_NUM_OF_ROOMS) + "$"
            ),
            CallbackQueryHandler(
                search_submit, pattern="^" + str(CB_SEARCH) + "$"
            ),
        ],
        DISTINCT: _create_callback_query_handler_group(
            DISTINCTS, 2, "Всі", "distinct", DISTINCT
        ),
        BUILDING_TYPE: _create_callback_query_handler_group(
            BUILDING_TYPES, 1, "Всі", "building_type", BUILDING_TYPE
        ),
        PRICE: [
            CallbackQueryHandler(price_from, pattern="^" + str(CB_FROM) + "$"),
            CallbackQueryHandler(price_to, pattern="^" + str(CB_TO) + "$"),
            CallbackQueryHandler(price_all, pattern="^" + "ALL" + "$"),
            CallbackQueryHandler(search, pattern="^" + "BACK" + "$"),
        ],
        PRICE_FROM: _create_price_callback_query_handler_group(
            dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
            3,
            PRICE_FROM,
            "price",
            True,
            price,
        ),
        PRICE_TO: _create_price_callback_query_handler_group(
            dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
            3,
            PRICE_TO,
            "price",
            False,
            price,
        ),
        FLOOR: [
            CallbackQueryHandler(floor_from, pattern="^" + str(CB_FROM) + "$"),
            CallbackQueryHandler(floor_to, pattern="^" + str(CB_TO) + "$"),
            CallbackQueryHandler(floor_all, pattern="^" + "ALL" + "$"),
            CallbackQueryHandler(search, pattern="^" + "BACK" + "$"),
        ],
        FLOOR_FROM: _create_price_callback_query_handler_group(
            dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
            3,
            FLOOR_FROM,
            "floor",
            True,
            floor,
        ),
        FLOOR_TO: _create_price_callback_query_handler_group(
            dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
            3,
            FLOOR_TO,
            "floor",
            False,
            floor,
        ),
        NUM_OF_ROOMS: [
            CallbackQueryHandler(
                num_of_rooms_from, pattern="^" + str(CB_FROM) + "$"
            ),
            CallbackQueryHandler(
                num_of_rooms_to, pattern="^" + str(CB_TO) + "$"
            ),
            CallbackQueryHandler(num_of_rooms_all, pattern="^" + "ALL" + "$"),
            CallbackQueryHandler(search, pattern="^" + "BACK" + "$"),
        ],
        NUM_OF_ROOMS_FROM: _create_price_callback_query_handler_group(
            dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
            3,
            NUM_OF_ROOMS_FROM,
            "num_of_rooms",
            True,
            num_of_rooms,
        ),
        NUM_OF_ROOMS_TO: _create_price_callback_query_handler_group(
            dict(enumerate([*[str(i) for i in range(1, 10)], "0", "<-"])),
            3,
            NUM_OF_ROOMS_TO,
            "num_of_rooms",
            False,
            num_of_rooms,
        ),
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(search_conversation)
