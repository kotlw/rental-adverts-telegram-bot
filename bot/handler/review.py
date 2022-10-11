from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bot import app, entity, cfg, helpers
from bot.repository import repo

END = ConversationHandler.END
ADVERTS, REVIEW = range(2)



async def review_pending_adverts(update: Update, context) -> int | str:
    msg = update.message
    user_data = context.user_data

    user_data[ADVERTS] = await repo.advert.get_pending_adverts()

    if not user_data[ADVERTS]:
        await msg.reply_text(cfg.Txt.no_pending_adverts_found)
        return END

    for i, advert in enumerate(user_data[ADVERTS]):
        hints = {**cfg.Btn.approve, **cfg.Btn.delete}
        indexed_hints = {f"{k}{i+1}": v for k, v in hints.items()}

        media = helpers.create_advert_media_group(
            advert, command_hints=indexed_hints, show_status=True
        )

        await msg.reply_media_group(media)

    return REVIEW


async def choose_approve_advert(update: Update, context) -> int | str:
    msg = update.message
    user_data = context.user_data

    index = int(msg.text.replace(f"/{cfg.Cmd.approve}", "")) - 1
    advert = user_data[ADVERTS][index]
    advert.status = entity.AdvertStatusEnum.APPROVED
    await repo.advert.upsert(advert)

    await msg.reply_text(cfg.Txt.approved)

    return REVIEW


async def choose_delete_advert(update: Update, context) -> int:
    msg = update.message
    user_data = context.user_data

    index = int(msg.text.replace(f"/{cfg.Cmd.delete}", "")) - 1
    advert = user_data[ADVERTS][index]

    await repo.advert.remove(advert)
    await update.message.reply_text(cfg.Txt.deleted)

    return REVIEW


async def review_command_error(update: Update, _) -> None:
    rm = ReplyKeyboardRemove()
    await update.message.reply_text(
        cfg.Txt.review_command_eror, reply_markup=rm
    )


async def cancel(update: Update, _) -> int:
    rm = ReplyKeyboardRemove()
    await update.message.reply_text(cfg.Txt.canceled, reply_markup=rm)
    return END


review_adverts_conv = ConversationHandler(
    entry_points=[
        CommandHandler(cfg.Cmd.review, review_pending_adverts),
    ],
    states={
        REVIEW: [
            MessageHandler(
                filters.Regex(f"^\\/{cfg.Cmd.approve}[0-9]$"),
                choose_approve_advert,
            ),
            MessageHandler(
                filters.Regex(f"^\\/{cfg.Cmd.delete}[0-9]$"),
                choose_delete_advert,
            ),
            MessageHandler(~filters.COMMAND, review_command_error),
        ],
    },
    fallbacks=[CommandHandler(cfg.Cmd.cancel, cancel)],
)

app.add_handler(review_adverts_conv)
