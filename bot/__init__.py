import os
import sys
import logging

from telegram.ext import ApplicationBuilder


logging_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO)
logger = logging.getLogger(__name__)


BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
DB_URI = os.getenv("DB_URI") or ""


for var_name in ["BOT_TOKEN", "DB_URI"]:
    if not locals()[var_name]:
        logger.error("%s variable is missing! Exiting now", var_name)
        sys.exit()


app = ApplicationBuilder().token(BOT_TOKEN).build()
