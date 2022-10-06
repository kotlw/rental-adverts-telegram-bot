from datetime import datetime

from telegram import InputMediaPhoto
from telegram import InputMediaAudio
from telegram import InputMediaDocument
from telegram import InputMediaVideo
from telegram.constants import ParseMode

from bot import entity

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

POST_START = (
    "Для того щоб розмістити Ваше оголошення треба пройти декілька простих "
    "кроків. Не переймайтесь якщо щось вказали невірно, Ви зможете "
    "відредагувати оголошення після завершення всих кроків."
    "\n\nРекомендації: постарайтесь оформити Ваше оголошення гарно, "
    "використовуючи при можливості елементи інфографіки, згідно з "
    "вищезгаданими критеріями, тоді Ваша публікація буде розміщена в "
    "телеграм каналі і її зможуть знайти орендарі."
)

ASK_DISTINCT = "Оберіть район"
ASK_STREET = "Введіть назву вулиці"
ASK_BUILDING_TYPE = "Оберіть тип будинку"
ASK_FLOOR = "Введіть номер поверху (від 1 до 27)"
ASK_SQUARE = "Введіть загальну площу квартири в м²"
ASK_NUM_OF_ROOMS = "Введіть кількість кімнат (від 1 до 6)"
ASK_LAYOUT = (
    "Введіть особливості планування: "
    "спальня, кухня-студія, кабінет, роздільний санвузол, тощо"
)
ASK_DESCRIPTION = (
    "Введіть опис: меблі, побутова техніка, "
    "інфраструктура, інші особливості"
)
ASK_SETTLEMENT_DATE = "Введіть дату можливого заселення у форматі дд.мм.рр"
ASK_PRICE = (
    "Введіть ціну у USD (в оголошенні ціна буде вказана у долларах "
    "і гривні еквівалентно курсу на поточний день)"
)
ASK_CONTACT = (
    "Введіть контактну інформацію: ім’я, номер телефону/телеграм, "
    "власник чи рієлтор, приватно чи назва агенції, компанії."
)
ASK_PHOTO = "Завантажте фото, по завершеню введіть /done"

SUBMIT_ADVERT = (
    "🟢 Дякую, що подали заявку на публікацію житла. Ми розглянемо Ваше "
    "оголошення й у разі позитивного рішення опублікуємо його у каналі. "
    "Якщо в оголошенні не буде виявлено помилок, воно отримає статус "
    "перевірено. Якщо хочете подати більше публікацій, то потрібно ще раз "
    "натиснути “/post” і виконати раніше згадані умови."
)

CHOOSE_TO_EDIT = "Оберіть поле для редагування"
CANT_EDIT = "🔴 Нажаль, не можна редагувати опубліковані оголошення."
CANCEL = "🟢 Відмінено."
EDIT_DONE = "🟢 Відредаговано."
FLOOR_VALUE_ERROR = (
    "🔴 Будь-ласка введіть значення в межах від 1 до 27, "
    "або введіть /cancel для відміни."
)
NUM_OF_ROOMS_VALUE_ERROR = (
    "🔴 Будь-ласка введіть значення в межах від 1 до 6, "
    "або введіть /cancel для відміни."
)
DATE_VALUE_ERROR = (
    "🔴 Будь-ласка перевірте дату, можливо Ви ввели не в форматі дд.мм.рр. "
    "Наприклад: 24.08.22, "
    "або введіть /cancel для відміни."
)

TEXT_INPUT_ERROR = "🔴 Будь-ласка введіть текст"

PHOTO_VALUE_ERROR = (
    "🔴 Будь-ласка завантажте хочаб одне фото. "
    "Якщо Ви завершили введіть /done для підтвердження, "
    "або введіть /cancel для відміни."
)
PHOTO_MAX_LIMIT_ERROR = "😢 Нажаль телеграм дозволяє додати лише 10 фото."

EDIT_MARKUP = {
    "distinct": "Район",
    "street": "Вулиця",
    "building_type": "Тип будинку",
    "floor": "Поверх",
    "square": "Площа",
    "num_of_rooms": "Кількість кімнат",
    "layout": "Планування",
    "description": "Опис",
    "settlement_date": "Дата можливого заселення",
    "price": "Ціна",
    "contact": "Контактні дані",
    "photo": "Фото",
}


KEYBOARD_SELECT_VALUE_ERROR = (
    "🔴 Будь-ласка оберіть елемент зі списку або введіть /cancel для відміни."
)


def make_advert_post(
    data: entity.Advert,
    index: int = None,
    show_submit: bool = True,
    show_status=False,
) -> list[
    InputMediaAudio | InputMediaDocument | InputMediaPhoto | InputMediaVideo
]:
    media: list[
        InputMediaAudio
        | InputMediaDocument
        | InputMediaPhoto
        | InputMediaVideo
    ]

    status_map = {
        entity.StatusEnum.PENDING: "розглядається",
        entity.StatusEnum.APPROVED: "прийнято",
        entity.StatusEnum.HIDDEN: "приховано",
    }
    status = (
        f"\n<b>Статус:</b> {status_map[data.status]}" if show_status else ""
    )
    edit = f"\n/edit{index or ''} - редагувати"
    submit = "\n/submit - відправити" if show_submit else ""
    delete = f"\n/delete{index or ''} - видалити" if not show_submit else ""
    cancel = "\n/cancel - відміна" if show_submit else ""

    media = [InputMediaPhoto(p) for p in data.photo]
    media[-1].parse_mode = ParseMode.HTML
    media[-1].caption = (
        f"<b>Район:</b> {data.distinct}\n"
        f"<b>Вулиця:</b> {data.street}\n"
        f"<b>Тип будинку:</b> {data.building_type}\n"
        f"<b>Поверх:</b> {data.floor}\n"
        f"<b>Площа:</b> {data.square} м²\n"
        f"<b>Кількість кімнат:</b> {data.num_of_rooms}\n"
        f"<b>Планування:</b> {data.layout}\n"
        f"<b>Опис:</b> {data.description}\n"
        f"<b>Дата можливого заселення:</b> "
        f"{data.settlement_date.strftime('%d.%m.%y')}\n"
        f"<b>Ціна:</b> {data.price} $\n"
        f"<b>Контакти:</b> {data.contact}\n"
        f"{status}"
        f"{submit}"
        f"{edit}"
        f"{delete}"
        f"{cancel}"
    )

    return media


def make_filter_msg(data: dict) -> str:
    distinct = ", ".join(data["distinct"]) if data["distinct"] else "Всі"
    building_type = ", ".join(data["building_type"]) if data["building_type"] else "Всі"
    floor = data["floor"]
    price = data["price"]
    num_of_rooms = data["num_of_rooms"]

    msg = (
        f"<b>Район:</b> {distinct}\n"
        f"<b>Тип будинку:</b> {building_type}\n"
        f"<b>Поверх:</b> {floor}\n"
        f"<b>Ціна:</b> {price}\n"
        f"<b>Кількість кімнат:</b> {num_of_rooms}\n"
    )

    return msg
