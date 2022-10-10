from collections import defaultdict

from telegram import Update
from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import CallbackQueryHandler
from telegram.constants import ParseMode

from bot import app, cfg, helpers, entity
from bot.repository import repo

FILTER = "filter"
SELECTED = "selected"
NUMBER_ENTER_STATE = "number_enter_state"

END = ConversationHandler.END
CHOOSE_FILTER = "choose_filter"
CATEGORY_FILTER = "category_filter"
NUMBER_FILTER = "number_filter"
NUMBER_ENTER = "number_enter"
DISTINCT = "distinct"
BUILDING_TYPE = "building_type"
FLOOR = "floor"
NUM_OF_ROOMS = "num_of_rooms"
PRICE = "price"


async def cancel(update: Update, _) -> int:
    await update.message.reply_text(cfg.Txt.canceled)
    return END


async def search(update: Update, context) -> str:
    user_data = context.user_data

    user_data[FILTER] = user_data.get(FILTER, defaultdict(list))
    kb = [
        *helpers.prepare_keyboard(cfg.Btn.filter_fields, 2, is_inline=True),
        *helpers.prepare_keyboard(cfg.Btn.filter_search, is_inline=True),
    ]
    rm = InlineKeyboardMarkup(kb)

    args = {
        "text": cfg.Txt.filter_msg(user_data[FILTER]),
        "reply_markup": rm,
        "parse_mode": ParseMode.HTML,
    }

    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(**args)
        return CHOOSE_FILTER

    await update.message.reply_text(**args)

    return CHOOSE_FILTER


async def choose_filter(update: Update, context) -> str | int:
    query = update.callback_query
    user_data = context.user_data

    await query.answer()

    if query.data == DISTINCT:
        user_data[SELECTED] = DISTINCT
        return await category_filter(update, context)
    elif query.data == BUILDING_TYPE:
        user_data[SELECTED] = BUILDING_TYPE
        return await category_filter(update, context)
    elif query.data == FLOOR:
        user_data[SELECTED] = FLOOR
        return await number_filter(update, context)
    elif query.data == NUM_OF_ROOMS:
        user_data[SELECTED] = NUM_OF_ROOMS
        return await number_filter(update, context)
    elif query.data == PRICE:
        user_data[SELECTED] = PRICE
        return await number_filter(update, context)
    elif query.data == cfg.Btn.cb_filter_search:
        user_data[SELECTED] = None
        return await filter_search(update, context)


    return CHOOSE_FILTER


async def filter_search(update: Update, context) -> str | int:
    query = update.callback_query
    msg = query.message
    user_data = context.user_data
    filter_data = user_data[FILTER]

    fltr = entity.AdvertFilter(**filter_data)
    adverts = await repo.advert.get_by_filter(fltr)

    if not adverts:
        await msg.reply_text(cfg.Txt.no_search_adverts_found)
        return END

    for advert in adverts:
        media = helpers.create_advert_media_group(advert)
        await msg.reply_media_group(media)

    return END


async def filter_all(update: Update, context) -> str:
    query = update.callback_query
    user_data = context.user_data
    filter_data = user_data[FILTER]
    selected_data = user_data[SELECTED]

    await query.answer()

    filter_data[selected_data] = []
    selected_data = None

    return await search(update, context)


async def category_filter(update: Update, context) -> str:
    query = update.callback_query
    user_data = context.user_data
    filter_data = user_data[FILTER]
    selected_data = user_data[SELECTED]

    await query.answer()

    categories = {
        DISTINCT: cfg.Btn.distinct_fields,
        BUILDING_TYPE: cfg.Btn.building_type_fields,
    }

    fields = categories[selected_data]

    if query.data in fields:
        if fields[query.data] in filter_data[selected_data]:
            filter_data[selected_data].remove(fields[query.data])
        else:
            filter_data[selected_data].append(fields[query.data])

    nav_buttons = {**cfg.Btn.filter_distinct_all, **cfg.Btn.filter_back}
    kb = [
        *helpers.prepare_keyboard(fields, 2, is_inline=True),
        *helpers.prepare_keyboard(nav_buttons, is_inline=True),
    ]
    rm = InlineKeyboardMarkup(kb)

    text = cfg.Txt.filter_msg(user_data[FILTER])
    await query.edit_message_text(
        text, reply_markup=rm, parse_mode=ParseMode.HTML
    )

    return CATEGORY_FILTER


async def number_filter(update: Update, context) -> str:
    query = update.callback_query
    user_data = context.user_data

    await query.answer()

    if query.data == cfg.Btn.cb_filter_num_from:
        user_data[NUMBER_ENTER_STATE] = cfg.Btn.cb_filter_num_from
        return await number_enter(update, context)
    elif query.data == cfg.Btn.cb_filter_num_to:
        user_data[NUMBER_ENTER_STATE] = cfg.Btn.cb_filter_num_to
        return await number_enter(update, context)

    from_to_buttons = {**cfg.Btn.filter_from, **cfg.Btn.filter_to}
    nav_buttons = {**cfg.Btn.filter_distinct_all, **cfg.Btn.filter_back}
    kb = [
        *helpers.prepare_keyboard(from_to_buttons, 2, is_inline=True),
        *helpers.prepare_keyboard(nav_buttons, is_inline=True),
    ]
    rm = InlineKeyboardMarkup(kb)

    text = cfg.Txt.filter_msg(user_data[FILTER])
    await query.edit_message_text(
        text, reply_markup=rm, parse_mode=ParseMode.HTML
    )

    return NUMBER_FILTER


async def number_enter(update: Update, context) -> str:
    query = update.callback_query
    user_data = context.user_data
    filter_data = user_data[FILTER]
    selected_data = user_data[SELECTED]
    state = user_data[NUMBER_ENTER_STATE]

    await query.answer()

    indicies = {cfg.Btn.cb_filter_num_from: 0, cfg.Btn.cb_filter_num_to: 1}
    index = indicies[state]

    if query.data in {**cfg.Btn.nums, **cfg.Btn.nums_nav}:
        filter_range = filter_data[selected_data]
        if query.data == cfg.Btn.cb_num_del:
            if not filter_range:
                filter_range = ["0", "0"]
            elif len(filter_range[index]) == 1:
                filter_range[index] = "0"
            else:
                filter_range[index] = filter_range[index][:-1]
        else:
            if not filter_range:
                filter_range = ["0", "0"]
                filter_range[index] = query.data
            elif filter_range[index] == "0":
                filter_range[index] = query.data
            else:
                filter_range[index] += query.data
        filter_data[selected_data] = filter_range

    kb = [
        *helpers.prepare_keyboard(cfg.Btn.nums, 3, is_inline=True),
        *helpers.prepare_keyboard(cfg.Btn.nums_nav, 2, is_inline=True),
        *helpers.prepare_keyboard(cfg.Btn.filter_back, is_inline=True),
    ]
    rm = InlineKeyboardMarkup(kb)

    text = cfg.Txt.filter_msg(user_data[FILTER])
    await query.edit_message_text(
        text, reply_markup=rm, parse_mode=ParseMode.HTML
    )

    return NUMBER_ENTER


search_conversation = ConversationHandler(
    entry_points=[CommandHandler("search", search)],  # type: ignore
    states={  # type: ignore
        CHOOSE_FILTER: [
            CallbackQueryHandler(choose_filter, pattern="^.*$"),
        ],
        CATEGORY_FILTER: [
            CallbackQueryHandler(
                filter_all, pattern=f"^{cfg.Btn.cb_filter_all}$"
            ),
            CallbackQueryHandler(search, pattern=f"^{cfg.Btn.cb_filter_back}$"),
            CallbackQueryHandler(category_filter, pattern="^.*$"),
        ],
        NUMBER_FILTER: [
            CallbackQueryHandler(
                filter_all, pattern=f"^{cfg.Btn.cb_filter_all}$"
            ),
            CallbackQueryHandler(search, pattern=f"^{cfg.Btn.cb_filter_back}$"),
            CallbackQueryHandler(number_filter, pattern="^.*$"),
        ],
        NUMBER_ENTER: [
            CallbackQueryHandler(
                number_filter, pattern=f"^{cfg.Btn.cb_filter_back}$"
            ),
            CallbackQueryHandler(number_enter, pattern="^.*$"),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

app.add_handler(search_conversation)
