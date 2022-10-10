from dataclasses import dataclass

from bot import entity


@dataclass(slots=True)
class BotCommand:
    start = "start"
    post_advert = "post_advert"
    my_adverts = "my_adverts"

    done = "done"
    cancel = "cancel"
    submit = "submit"
    edit = "edit"


@dataclass(slots=True)
class BotButton:
    distincts = [
        "Галицький",
        "Залізничний",
        "Личаківський",
        "Франківський",
        "Шевченківський",
        "Сихівський",
    ]
    building_types = ["новобудова", "не новобудова (чешка, хрущовка, тощо)"]
    advert_fields = {
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
    submit = {BotCommand.submit: "відправити"}
    edit = {BotCommand.edit: "редагувати"}


@dataclass(slots=True)
class BotText:
    post_advert = (
        "Для того щоб розмістити Ваше оголошення треба пройти декілька простих "
        "кроків. Не переймайтесь якщо щось вказали невірно, Ви зможете "
        "відредагувати оголошення після завершення всих кроків."
        "\n\nРекомендації: постарайтесь оформити Ваше оголошення гарно, "
        "використовуючи при можливості елементи інфографіки, згідно з "
        "вищезгаданими критеріями, тоді Ваша публікація буде розміщена в "
        "телеграм каналі і її зможуть знайти орендарі."
    )
    ask_distinct = "Оберіть район"
    ask_street = "Введіть назву вулиці"
    ask_building_type = "Оберіть тип будинку"
    ask_floor = "Введіть номер поверху (від 1 до 27)"
    ask_square = "Введіть загальну площу квартири в м²"
    ask_num_of_rooms = "Введіть кількість кімнат (від 1 до 6)"
    ask_layout = (
        "Введіть особливості планування: "
        "спальня, кухня-студія, кабінет, роздільний санвузол, тощо"
    )
    ask_description = (
        "Введіть опис: меблі, побутова техніка, "
        "інфраструктура, інші особливості"
    )
    ask_settlement_date = "Введіть дату можливого заселення у форматі дд.мм.рр"
    ask_price = (
        "Введіть ціну у USD (в оголошенні ціна буде вказана у долларах "
        "і гривні еквівалентно курсу на поточний день)"
    )
    ask_contact = (
        "Введіть контактну інформацію: ім’я, номер телефону/телеграм, "
        "власник чи рієлтор, приватно чи назва агенції, компанії."
    )
    ask_photo = f"Завантажте фото, по завершеню введіть /{BotCommand.done}"

    canceled = "🟢 Відмінено."

    choose_edit_field = "Оберіть поле для редагування"

    text_value_error = "🔴 Будь-ласка введіть текст"
    select_value_error = (
        "🔴 Будь-ласка оберіть елемент зі списку або введіть "
        f"/{BotCommand.cancel} для відміни."
    )
    floor_value_error = (
        "🔴 Будь-ласка введіть значення в межах від 1 до 27, "
        f"або введіть /{BotCommand.cancel} для відміни."
    )
    num_of_rooms_value_error = (
        "🔴 Будь-ласка введіть значення в межах від 1 до 6, "
        f"або введіть /{BotCommand.cancel} для відміни."
    )
    date_value_error = (
        "🔴 Будь-ласка перевірте дату, можливо Ви ввели не в форматі дд.мм.рр. "
        "Наприклад: 24.08.22, "
        f"або введіть /{BotCommand.cancel} для відміни."
    )
    photo_value_error = (
        "🔴 Будь-ласка завантажте хочаб одне фото. "
        f"Якщо Ви завершили введіть /{BotCommand.done} для підтвердження, "
        f"або введіть /{BotCommand.cancel} для відміни."
    )
    photo_max_limit_error = "😢 Нажаль телеграм дозволяє додати лише 10 фото."

    submit_advert = (
        "🟢 Дякую, що подали заявку на публікацію житла. Ми розглянемо Ваше "
        "оголошення й у разі позитивного рішення опублікуємо його у каналі. "
        "Якщо в оголошенні не буде виявлено помилок, воно отримає статус "
        "перевірено. Якщо хочете подати більше публікацій, то потрібно ще раз "
        "натиснути “/post” і виконати раніше згадані умови."
    )

    @staticmethod
    def advert_caption_html(
        advert: entity.Advert,
        command_hints: dict | None = None,
        show_status: bool = False,
    ) -> str:

        status = (
            f"<b>Статус:</b> {advert.status.value}\n\n" if show_status else ""
        )

        commands = ""
        if command_hints:
            commands = [f"/{k} - {v}" for k, v in command_hints.items()]
            commands = "\n".join(commands)

        caption = (
            f"<b>Район:</b> {advert.distinct}\n"
            f"<b>Вулиця:</b> {advert.street}\n"
            f"<b>Тип будинку:</b> {advert.building_type}\n"
            f"<b>Поверх:</b> {advert.floor}\n"
            f"<b>Площа:</b> {advert.square} м²\n"
            f"<b>Кількість кімнат:</b> {advert.num_of_rooms}\n"
            f"<b>Планування:</b> {advert.layout}\n"
            f"<b>Опис:</b> {advert.description}\n"
            f"<b>Дата можливого заселення:</b> {advert.settlement_date}\n"
            f"<b>Ціна:</b> {advert.price} $\n"
            f"<b>Контакти:</b> {advert.contact}\n\n"
            f"{status}"
            f"{commands}"
        )

        return caption


# aliases
Cmd = BotCommand
Btn = BotButton
Txt = BotText
