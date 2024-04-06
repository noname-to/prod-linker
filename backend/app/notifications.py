import locale
from telebot import TeleBot

from app import TG_BOT_TOKEN
from app.data import models
from app.data.locations import addr_from_coords

locale.setlocale(locale.LC_ALL, '')
bot = TeleBot(token=TG_BOT_TOKEN)


async def send_new_meeting_notification(receiver: int, meeting: models.Meeting) -> None:
    meeting_time = meeting.start_time.strftime("%d %B в %H:%M")
    address = await addr_from_coords(coords=meeting.meeting_location)
    product = meeting.product.title
    representative_name = meeting.representative.first_name
    representative_phone = meeting.representative.phone_number

    confidant = meeting.confidant
    if confidant is not None:
        confidant_string = (
            "\n"
            f"На встрече должен присутствовать <b>{confidant.last_name} {confidant.first_name} {confidant.middle_name}</b>"
        )
    else:
        confidant_string = ""

    specialists = meeting.product.specialists
    
    if len(specialists) == 0:
        specialist_string = ''
    else:
        necessary_specialists_list_string = "\n".join(['- ' + occupation for occupation in specialists])
        
        specialist_string = (
            "\n\n"
            "Также необходимо пригласить на встречу:\n"
            f"{necessary_specialists_list_string}"
        )

    documents = meeting.product.documents
    if len(documents) == 0:
        documents_string = ''
    else:
        documents_list_string = "\n".join(['- ' + document.title for document in documents])
        documents_string = (
            "\n\n"
            "Необходимые для встречи документы:\n"
            f"{documents_list_string}"
        )

    if address is None:
        address = 'не указано'

    bot.send_message(
        receiver,
        f"<b>{meeting_time}</b> приедет представитель <b>{representative_name}</b>, {representative_phone}"
        "\n"
        f"<b>Место встречи:</b> {address}"
        f"{confidant_string}"
        f"{specialist_string}"
        f"{documents_string}"
        "\n\n"
        f"<b>Предмет встречи:</b> {product}",
        parse_mode="HTML"
    )


def send_meeting_finished_notification(receiver: int, meeting: models.Meeting) -> None:
    
    link = f'https://noname.to/rate/{meeting.id}'
    
    bot.send_message(
        receiver,
        f"Встреча по продукту <b>{meeting.product.title}</b> завершена\n"
        f"Пожалуйста, оцените качество работы представителя по ссылке: {link}",
        parse_mode="HTML"
    )
