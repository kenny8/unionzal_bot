import admin
import settings
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InputMediaPhoto
from datetime import datetime
from json_parser import json_afisha
from admin import update_admin_status
import logging

# Включение логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def log_user_action(func):
    def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        logger.info(f"Пользователь {user.username} вызвал функцию {func.__name__}")
        return func(update, context, *args, **kwargs)
    return wrapper

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    """
    Создает меню с кнопками.
    :param buttons: список кнопок
    :param n_cols: количество столбцов
    :param header_buttons: список кнопок для шапки
    :param footer_buttons: список кнопок для подвала
    :return: InlineKeyboardMarkup
    """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


@log_user_action
async def afisha(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Афиша'."""
    # Получаем текущее время
    now = datetime.now()
    time_diff = now - settings.AFISHA_CARD_TIME
    hours_diff = time_diff.seconds // 3600
    if hours_diff >= 12:
        print("обновились афиши")
        settings.AFISHA_CARD = json_afisha()
        settings.AFISHA_CARD_TIME = now
    afisha_card = settings.AFISHA_CARD # загрузка json
    # Создание кнопок выбора даты концерта
    buttons = [InlineKeyboardButton(text=event[2][0], callback_data=f"afisha_event_{event[2][0]}")
                             for event in afisha_card]
    keyboard = InlineKeyboardMarkup(inline_keyboard=build_menu(buttons, n_cols=2))
    # Отправка сообщения пользователю с клавиатурой выбора даты концерта
    await context.bot.send_photo(chat_id=update.message.chat_id, photo=settings.MAIN_WALLPAPERS, caption="Выберите дату концерта", reply_markup=keyboard)
    # Сохранение данных афиши в пользовательскую базу данных бота
    context.user_data["afisha_card"] = afisha_card

@log_user_action
async def afisha_callback(update, context):
    """Отправка сообщения с заголовком и текстом события, выбранного пользователем."""
    query = update.callback_query
    await query.answer()
    # Получение выбранного события
    selected_event = [event for event in context.user_data["afisha_card"] if event[2][0] == query.data.split("_")[2]][0]
    # Создание кнопок
    buy_button = InlineKeyboardButton(text="Купить билет", url=selected_event[5])
    more_info_button = InlineKeyboardButton(text="Подробнее", callback_data=f"afisha_more_info_{selected_event[2][0]}")
    prev_button = InlineKeyboardButton(text="<", callback_data=f"afisha_prev_{selected_event[2][0]}")
    next_button = InlineKeyboardButton(text=">", callback_data=f"afisha_next_{selected_event[2][0]}")
    # Создание разметки с кнопками
    keyboard = [[buy_button, more_info_button], [prev_button, next_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Создание текста сообщения
    text = f"{selected_event[0]}\n\n{selected_event[2][1]} - {selected_event[3][1]} - {selected_event[2][0]}"
    # Отправка сообщения
    await context.bot.edit_message_media(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                         media=InputMediaPhoto(selected_event[4], caption=text),
                                         reply_markup=markup)

@log_user_action
async def more_info_callback(update, context):
    """Редактирование сообщения, добавление подробной информации о выбранном событии."""
    query = update.callback_query
    await query.answer()
    # Получение выбранного события
    selected_event = [event for event in context.user_data["afisha_card"] if event[2][0] == query.data.split("_")[3]][0]
    txt = split_text(selected_event[1])
    # Создание кнопок
    buy_button = InlineKeyboardButton(text="Купить билет", url=selected_event[5])
    prev_button = InlineKeyboardButton(text="<", callback_data=f"afisha_prev_{selected_event[2][0]}")
    next_button = InlineKeyboardButton(text=">", callback_data=f"afisha_next_{selected_event[2][0]}")
    if len(txt) > 1:
        read_more = InlineKeyboardButton(text="дальше", callback_data=f"afisha_read_more_{selected_event[2][0]}")
        keyboard = [[buy_button, read_more], [prev_button, next_button]]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        # Редактирование сообщения
        text = f"{selected_event[0]}\n\n{selected_event[2][1]} - {selected_event[3][1]} - {selected_event[2][0]}\n\n{txt[0]}"
    else:
        # Создание разметки с кнопками
        keyboard = [[buy_button], [prev_button, next_button]]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        # Редактирование сообщения
        text = f"{selected_event[0]}\n\n{selected_event[2][1]} - {selected_event[3][1]} - {selected_event[2][0]}\n\n{selected_event[1]}"
    #await query.edit_message_text(text=text, reply_markup=markup)
    await context.bot.edit_message_media(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                         media=InputMediaPhoto(selected_event[4], caption=text),
                                         reply_markup=markup)

@log_user_action
async def read_more_callback(update, context):
    """Редактирование сообщения, добавление подробной информации о выбранном событии."""
    query = update.callback_query
    await query.answer()
    # Получение выбранного события
    selected_event = [event for event in context.user_data["afisha_card"] if event[2][0] == query.data.split("_")[3]][0]
    txt = split_text(selected_event[1])
    # Создание кнопок
    buy_button = InlineKeyboardButton(text="Купить билет", url=selected_event[5])
    prev_button = InlineKeyboardButton(text="<", callback_data=f"afisha_prev_{selected_event[2][0]}")
    next_button = InlineKeyboardButton(text=">", callback_data=f"afisha_next_{selected_event[2][0]}")
    keyboard = [[buy_button], [prev_button, next_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Редактирование сообщения
    text = f"{selected_event[0]}\n\n{selected_event[2][1]} - {selected_event[3][1]} - {selected_event[2][0]}\n\n{txt[1]}"
    #await query.edit_message_text(text=text, reply_markup=markup)
    await context.bot.edit_message_media(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                         media=InputMediaPhoto(selected_event[4], caption=text),
                                         reply_markup=markup)

@log_user_action
async def prev_callback(update, context):
    """Переход к предыдущему событию в списке afisha_card."""
    query = update.callback_query
    await query.answer()
    # Получение выбранного события
    selected_event = [event for event in context.user_data["afisha_card"] if event[2][0] == query.data.split("_")[2]][0]
    # Поиск индекса выбранного события в списке
    index = context.user_data["afisha_card"].index(selected_event)
    # Выбор предыдущего события в списке (если есть)
    if index > 0:
        prev_event = context.user_data["afisha_card"][index - 1]
        # Создание кнопок
        buy_button = InlineKeyboardButton(text="Купить билет", url=prev_event[5])
        more_info_button = InlineKeyboardButton(text="Подробнее", callback_data=f"afisha_more_info_{prev_event[2][0]}")
        prev_button = InlineKeyboardButton(text="<", callback_data=f"afisha_prev_{prev_event[2][0]}")
        next_button = InlineKeyboardButton(text=">", callback_data=f"afisha_next_{prev_event[2][0]}")
        # Создание разметки с кнопками
        if index == 1:
            keyboard = [[buy_button, more_info_button], [next_button]]
        else:
            keyboard = [[buy_button, more_info_button], [prev_button, next_button]]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        # Создание текста сообщения
        text = f"{prev_event[0]}\n\n{prev_event[2][1]} - {prev_event[3][1]} - {prev_event[2][0]}"
        # Редактирование сообщения с новым событием и новыми кнопками
        #await query.message.edit_text(text=text, reply_markup=markup)
        await context.bot.edit_message_media(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                             media=InputMediaPhoto(prev_event[4], caption=text),
                                             reply_markup=markup)
    else:
        # Если выбранное событие первое в списке, то просто отправляем сообщение без изменений
        await query.message.answer(text="Вы находитесь на первом событии.")

@log_user_action
async def next_callback(update, context):
    """Обработка нажатия на кнопку 'Следующее событие'."""
    query = update.callback_query
    await query.answer()
    # Получение списка всех событий
    events = context.user_data["afisha_card"]
    # Получение индекса текущего события
    current_index = [i for i, event in enumerate(events) if event[2][0] == query.data.split("_")[2]][0]
    # Получение текущего события
    current_event = events[current_index]
    # Получение следующего события
    for next_index in range(current_index + 1, len(events)):
        next_event = events[next_index]
        if next_event[2][0] != current_event[2][0]:
            break
    else:
        next_index = 0
        next_event = events[0]
    # Создание текста сообщения
    text = f"{next_event[0]}\n\n{next_event[2][1]} - {next_event[3][1]} - {next_event[2][0]}"
    # Создание кнопок
    buy_button = InlineKeyboardButton(text="Купить билет", url=next_event[5])
    more_info_button = InlineKeyboardButton(text="Подробнее", callback_data=f"afisha_more_info_{next_event[2][0]}")
    prev_button = InlineKeyboardButton(text="<", callback_data=f"afisha_prev_{next_event[2][0]}")
    next_button = InlineKeyboardButton(text=">", callback_data=f"afisha_next_{next_event[2][0]}")
    # Создание разметки с кнопками
    keyboard = [[buy_button, more_info_button], [prev_button, next_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    if current_event[2][0] != next_event[2][0]:
        # Редактирование сообщения
        await context.bot.edit_message_media(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                             media=InputMediaPhoto(next_event[4], caption=text),
                                             reply_markup=markup)
    else:
        await context.bot.send_photo(chat_id=query.message.chat_id, photo=next_event[4],
                                     caption=text, reply_markup=markup)


def split_text(text):
    if len(text) < settings.MAX_MESSAGE_LENGTH:
        return [text]
    # Разделяем текст на подстроки по пробелам
    substrings = text.split(' ')
    result = []
    current_substring = ''
    for substring in substrings:
        if len(current_substring) + len(substring) < settings.MAX_MESSAGE_LENGTH:
            current_substring += ' ' + substring
        else:
            result.append(current_substring.strip())
            current_substring = substring
    result.append(current_substring.strip())
    return result