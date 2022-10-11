from bot import app, BOT_TOKEN, BOT_WEBHOOK_URL, BOT_PORT
from .handler import start, post_edit_show_advert, search, review


# this is to handle unused import warning
__all__ = ["start", "post_edit_show_advert", "search", "review"]


if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=BOT_PORT,
        url_path=BOT_TOKEN,
        webhook_url=BOT_WEBHOOK_URL + BOT_TOKEN,
    )
