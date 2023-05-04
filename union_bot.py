
import logging
from telegram import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from telegram import InputMediaPhoto
from json_parser import json_persons
import settings
from afisha_ import afisha_callback, more_info_callback, read_more_callback, prev_callback, next_callback, afisha

# Включение логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Создание разметки клавиатуры для меню
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Главная", "Афиша"], ["Исполнители", "Билеты"]]
)

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


# Определение обработчиков команд. Обычно они принимают два аргумента: update и context.
async def start(update, context):
    """Отправка сообщения, когда пользователь вводит команду /start."""
    user = update.effective_user
    # Создание новой клавиатуры с кнопками выбора действия для пользователя
    reply_keyboard = ReplyKeyboardMarkup(
        [["Афиша", "Розыгрыш билетов"], ["Исполнители", "Обратная связь"]]
    )
    # Отправка сообщения пользователю
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! это бот липецкой филармонии!",
        reply_markup=reply_keyboard,
    )


async def help_command(update, context):
    """Отправка сообщения, когда пользователь вводит команду /help."""
    # Отправка сообщения пользователю с инструкцией, что нужно делать
    await update.message.reply_text("Нужна помощь? помоги себе сам")


async def echo(update, context):
    """Эхо-ответ на сообщение пользователя."""
    # Отправка сообщения пользователю, которое повторяет его входящее сообщение
    await update.message.reply_text(update.message.text)

async def giveaway(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Розыгрыш билетов'."""
    await update.message.reply_text("какой-то розыгрыш билетов")


async def performers(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Исполнители'."""
    persons_card = json_persons() # загрузка json
    # Создание кнопок выбора выбора вида исполнителя
    #print(persons_card)
    persons = list(set(event[2] for event in persons_card))
    #persons.insert(0, "Поиск")
    # Создание кнопок выбора выбора вида исполнителя
    keyboard_buttons = [[InlineKeyboardButton(text=per, callback_data=f"performers_event_{per}")] for per in persons]
    # Создание клавиатуры с кнопками выбора вида исполнителя
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    # Отправка сообщения пользователю с клавиатурой выбора вида исполнителя
    await context.bot.send_photo(chat_id=update.message.chat_id, photo=settings.MAIN_WALLPAPERS, caption="Выберите:", reply_markup=keyboard)
    # Сохранение данных персоналий в пользовательскую базу данных бота
    context.user_data["persons_card"] = persons_card


async def performers_callback(update, context):
    query = update.callback_query
    data = query.data.split("_")

    if data[1] == "event":
        # Получение карточек исполнителей из пользовательских данных
        persons_card = context.user_data.get("persons_card")

        # Фильтрация карточек исполнителей по выбранному типу
        persons = [card for card in persons_card if card[2] == data[2]]

        buttons = [InlineKeyboardButton(text=str(i + 1), callback_data=f"performers_card_{data[2]}_{i}") for i, _ in
                   enumerate(persons)]

        keyboard = InlineKeyboardMarkup(inline_keyboard=build_menu(buttons, n_cols=3))

        # Отправка сообщения с номерами исполнителей и кнопкой назад
        text = f"Выберите номер {data[2]}:\n"
        text += "\n".join([f"{i + 1}. {p[0]}" for i, p in enumerate(persons)])

        # keyboard.add(InlineKeyboardButton(text="Назад", callback_data="performers_back"))

        await context.bot.edit_message_media(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                             media=InputMediaPhoto(settings.MAIN_WALLPAPERS, caption=text),
                                             reply_markup=keyboard)
    elif data[1] == "card":
        # Изменение клавиатуры для карточки исполнителя
        persons_card = context.user_data.get("persons_card")
        persons = [card for card in persons_card if card[2] == data[2]]
        #print(card)
        print(persons[int(data[3])])
        # Вывод картинки, текста и кнопки ссылки на исполнителя
        button = InlineKeyboardButton(text="Ссылка", url=persons[int(data[3])][3])
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
        text = f"{persons[int(data[3])][0]}\n {persons[int(data[3])][1]}\n"
        await context.bot.edit_message_media(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                             media=InputMediaPhoto(persons[int(data[3])][4], caption=text),
                                             reply_markup=keyboard)


async def feedback(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Обратная связь'."""
    await update.message.reply_text("напишите нам на почту")


def main():
    """Запуск бота."""
    # Создание приложения и передача ему токена вашего бота.
    application = Application.builder().token(settings.TOKEN_BOT).build()
    # Назначение обработчиков на различные команды в Telegram.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    # Добавление обработчиков для каждой кнопки
    application.add_handler(
        MessageHandler(filters.Regex("^Афиша$"), callback=afisha)
    )
    # Регистрация обработчиков афиши
    application.add_handler(CallbackQueryHandler(callback=afisha_callback, pattern=r"afisha_event_\d+"))
    application.add_handler(CallbackQueryHandler(callback=read_more_callback, pattern=r"afisha_read_more_\d+"))
    application.add_handler(CallbackQueryHandler(callback=more_info_callback, pattern=r"afisha_more_info_\d+"))
    application.add_handler(CallbackQueryHandler(callback=prev_callback, pattern=r"afisha_prev_\d+"))
    application.add_handler(CallbackQueryHandler(callback=next_callback, pattern=r"afisha_next_\d+"))

    application.add_handler(
        MessageHandler(filters.Regex("^Розыгрыш билетов$"), callback=giveaway)
    )
    application.add_handler(
        MessageHandler(filters.Regex("^Исполнители$"), callback=performers)
    )
    application.add_handler(CallbackQueryHandler(callback=performers_callback, pattern=r"performers_event_\d*"))
    application.add_handler(CallbackQueryHandler(callback=performers_callback, pattern=r"performers_card_\d*"))
    application.add_handler(
        MessageHandler(filters.Regex("^Обратная связь$"), callback=feedback)
    )
    # Запуск бота и ожидание его завершения пользователем (нажатие Ctrl-C).
    application.run_polling()

if __name__ == "__main__":
    main()