from dataclasses import dataclass

from bot import entity


DISTINCT = "distinct"
STREET = "street"
BUILDING_TYPE = "building_type"
FLOOR = "floor"
SQUARE = "square"
NUM_OF_ROOMS = "num_of_rooms"
LAYOUT = "layout"
DESCRIPTION = "description"
SETTLEMENT_DATE = "settlement_date"
PRICE = "price"
CONTACT = "contact"
PHOTO = "photo"


@dataclass(slots=True)
class BotCommand:
    start = "start"
    post_advert = "post_advert"
    my_adverts = "my_adverts"
    search = "search"
    review = "review"

    done = "done"
    cancel = "cancel"
    submit = "submit"
    edit = "edit"
    delete = "delete"
    approve = "approve"


@dataclass(slots=True)
class BotButton:
    distinct_fields = {
        "galyckyi": "Галицький",
        "zaliznychnyi": "Залізничний",
        "lychakivskyi": "Личаківський",
        "frankivskyi": "Франківський",
        "shevchenkivskyi": "Шевченківський",
        "syhivskyi": "Сихівський",
    }
    building_type_fields = {
        "novobudova": "новобудова",
        "ne_novobudova": "не новобудова (чешка, хрущовка, тощо)",
    }
    advert_fields = {
        DISTINCT: "Район",
        STREET: "Вулиця",
        BUILDING_TYPE: "Тип будинку",
        FLOOR: "Поверх",
        SQUARE: "Площа",
        NUM_OF_ROOMS: "Кількість кімнат",
        LAYOUT: "Планування",
        DESCRIPTION: "Опис",
        SETTLEMENT_DATE: "Дата можливого заселення",
        PRICE: "Ціна",
        CONTACT: "Контактні дані",
        PHOTO: "Фото",
    }
    filter_fields = {
        DISTINCT: advert_fields[DISTINCT],
        BUILDING_TYPE: advert_fields[BUILDING_TYPE],
        FLOOR: advert_fields[FLOOR],
        NUM_OF_ROOMS: advert_fields[NUM_OF_ROOMS],
        PRICE: advert_fields[PRICE],
    }
    filter_num_from = {"filter_num_from": "Від"}
    filter_num_to = {"filter_num_to": "До"}
    filter_back = {"filter_back": "Повернутись"}
    filter_search = {"filter_search": "Пошук"}
    filter_all = {"filter_all": "Всі"}
    filter_distinct_all = {[*filter_all.keys()][0]: "Будь-який"}
    filter_building_type_all = {[*filter_all.keys()][0]: "Будь-який"}
    filter_num_of_rooms_all = {[*filter_all.keys()][0]: "Будь-яка"}
    filter_floor_all = {[*filter_all.keys()][0]: "Будь-який"}
    filter_price_all = {[*filter_all.keys()][0]: "Будь-яка"}
    nums = {
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
    }
    num_del = {"filter_num_del": "<-"}
    nums_nav = {"0": "0", **num_del}

    submit = {BotCommand.submit: "відправити"}
    cancel = {BotCommand.cancel: "відмінити"}
    edit = {BotCommand.edit: "редагувати"}
    delete = {BotCommand.delete: "видалити"}
    approve = {BotCommand.approve: "затвердити"}


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
    deleted = "🟢 Оголошення видалено."
    approved = "🟢 Затверджено"

    choose_edit_field = "Оберіть поле для редагування"

    text_value_error = "🔴 Будь-ласка введіть текст"
    number_value_error = "🔴 Будь-ласка введіть число"
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
    cant_edit = "🔴 Нажаль, не можна редагувати опубліковані оголошення."
    advert_overview = "Так виглядає ваше оголошення: "
    no_user_adverts_found = "У вас ще немає створених оголошень"
    no_search_adverts_found = "За вашим запитом нічого не знайдено"
    no_pending_adverts_found = "Наразі оголошень для перевірки немає"

    submit_advert = (
        "🟢 Дякую, що подали заявку на публікацію житла. Ми розглянемо Ваше "
        "оголошення й у разі позитивного рішення опублікуємо його у каналі. "
        "Якщо в оголошенні не буде виявлено помилок, воно отримає статус "
        "опубліковано."
    )
    review_command_eror = (
        "🔴 Будь-ласка скористайтесь командами "
        f"/{BotCommand.approve}, /{BotCommand.delete}, "
        f"або введіть /{BotCommand.cancel} для відміни."
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

    @staticmethod
    def filter_msg(data: dict) -> str:

        all_key = [*BotButton.filter_all.keys()][0]

        distinct = BotButton.filter_distinct_all[all_key]
        if data.get("distinct"):
            distinct = ", ".join(data["distinct"])

        building_type = BotButton.filter_building_type_all[all_key]
        if data.get("building_type"):
            building_type = ", ".join(data["building_type"])

        floor = BotButton.filter_floor_all[all_key]
        if data.get("floor"):
            floor = f"від {data['floor'][0]} до {data['floor'][1]}"

        price = BotButton.filter_price_all[all_key]
        if data.get("price"):
            price = f"від {data['price'][0]} до {data['price'][1]}"

        num_of_rooms = BotButton.filter_num_of_rooms_all[all_key]
        if data.get("num_of_rooms"):
            num_of_rooms = (
                f"від {data['num_of_rooms'][0]} до {data['num_of_rooms'][1]}"
            )

        msg = (
            f"<b>Район:</b> {distinct}\n"
            f"<b>Тип будинку:</b> {building_type}\n"
            f"<b>Поверх:</b> {floor}\n"
            f"<b>Ціна:</b> {price}\n"
            f"<b>Кількість кімнат:</b> {num_of_rooms}\n"
        )

        return msg


date_format = "%d.%m.%y"

# aliases
Cmd = BotCommand
Btn = BotButton
Txt = BotText
