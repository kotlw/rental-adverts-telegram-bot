import os
import sys
import logging

from telegram.ext import ApplicationBuilder

from .helper import db


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
if not BOT_TOKEN:
    logger.error("BOT_TOKEN variable is missing! Exiting now")
    sys.exit(1)

DB_URI = os.getenv("DB_URI") or ""
if not DB_URI:
    logger.error("DB_URI variable is missing! Exiting now")
    sys.exit(1)


app = ApplicationBuilder().token(BOT_TOKEN).build()
db_gateway = db.DBGateway(DB_URI)
