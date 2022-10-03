"""This file contains configuration constants."""
import os

BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
DB_URI = os.getenv("DB_URI") or ""
ALEMBIC_DB_URI = os.getenv("DB_URI") or ""

DB_STATUS_VALUES = ["pending", "approved", "hidden"]
DB_DISTINCT_VALUES = ["район1", "район2", "район3"]
DB_BUILDING_TYPE_VALUES = ["новобудова", "хрущовка"]
