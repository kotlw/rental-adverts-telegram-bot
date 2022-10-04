"""Common messages."""
import db.model

KEYBOARD_SELECT_VALUE_ERROR = (
    "🔴 Будь-ласка оберіть елемент зі списку або введіть /cancel для відміни."
)

def advert_overview(data: db.model.Advert) -> str:
    return (
        f"*Район:* {data.distinct}\n"
        f"*Вулиця:* {data.street}\n"
        f"*Тип будинку:* {data.building_type}\n"
        f"*Поверх:* {data.floor}\n"
        f"*Площа:* {data.square} м²\n"
        f"*Кількість кімнат:* {data.num_of_rooms}\n"
        f"*Планування:* {data.layout}\n"
        f"*Опис:* {data.description}\n"
        f"*Дата можливого заселення:* {data.settlement_date}\n"
        f"*Ціна:* {data.price} $\n"
        f"*Контакти:* {data.contact}\n"
        "\n/edit \\- редагувати"
        "\n/submit \\- відправити"
    )
