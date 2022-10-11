import sys
import logging

from telegram.ext import ApplicationBuilder

import cfg
from handler import start, post_edit_show_advert, search, review

logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    for var_name in ["BOT_TOKEN", "DB_URI", "BOT_WEBHOOK_URL"]:
        if not getattr(cfg, var_name):
            logger.error("%s variable is missing! Exiting now", var_name)
            sys.exit()

    app = ApplicationBuilder().token(cfg.BOT_TOKEN).build()

    app.add_handler(start.start_command)
    app.add_handler(post_edit_show_advert.post_edit_show_advert_conv)
    app.add_handler(search.search_conv)
    app.add_handler(review.review_adverts_conv)

    app.run_webhook(
        listen="0.0.0.0",
        port=cfg.PORT,
        url_path=cfg.BOT_TOKEN,
        webhook_url=cfg.BOT_WEBHOOK_URL + cfg.BOT_TOKEN,
    )

