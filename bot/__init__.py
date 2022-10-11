import os
import sys
import logging

from telegram.ext import ApplicationBuilder

PROD = False

logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO)
logger = logging.getLogger(__name__)


BOT_WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL") or ""
PORT = int(os.getenv("PORT", "8443"))
BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
DB_URI = os.getenv("DB_URI") or ""


for var_name in ["BOT_TOKEN", "DB_URI", "BOT_WEBHOOK_URL"]:
    if not locals()[var_name]:
        logger.error("%s variable is missing! Exiting now", var_name)
        sys.exit()


app = ApplicationBuilder().token(BOT_TOKEN).build()
