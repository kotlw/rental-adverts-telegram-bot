"""This file contains configuration constants."""
import os

BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
DB_URI = os.getenv("DB_URI") or ""
ALEMBIC_DB_URI = os.getenv("DB_URI") or ""

STATUS_VALUES = ["pending", "approved", "hidden"]
DISTINCT_VALUES = [
    "Галицький",
    "Залізничний",
    "Личаківський",
    "Франківський",
    "Шевченківський",
    "Сихівський",
]
BUILDING_TYPE_VALUES = ["новобудова", "не новобудова (чешка, хрущовка, тощо)"]

# Messages
KEYBOARD_SELECT_VALUE_ERROR_MSG = (
    "🔴 Будь-ласка оберіть елемент зі списку або введіть /cancel для відміни."
)

# Post advert messages
PA_CANCEL_MSG = "🟢 Створення оголошення відмінено."

PA_START_MESSAGE = (
    "Для того щоб розмістити Ваше оголошення треба пройти декілька простих "
    "кроків. Не переймайтесь якщо щось вказали невірно, Ви зможете "
    "відредагувати оголошення після завершення всих кроків."
)
PA_SELECT_DISTINCT_MSG = "Оберіть район"
PA_ENTER_STREET_MSG = "Введіть назву вулиці"
PA_SELECT_BUILDING_TYPE_MSG = "Оберіть тип будинку"
PA_ENTER_FLOOR_MSG = "Введіть номер поверху (від 1 до 27)"
PA_ENTER_SQUARE = "Введіть площу квартири"
PA_ENTER_NUM_OF_ROOMS = "Введіть кількість кімнат"
PA_ENTER_LAYOUT = "Введіть планування квартири"
PA_ENTER_DESCRIPTION = "Введіть опис"
PA_ENTER_SETTLEMENT_DATE = "Введіть дату можливого заселення"
