
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
from json_parser import json_afisha

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
        rf"Привет, {user.mention_html()}!",
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


async def afisha(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Афиша'."""
    afisha_card = json_afisha()#загрузка json
    # Создание кнопки выбора даты концерта
    keyboard_buttons = [
        [InlineKeyboardButton(text=event[2][0], callback_data=f"event_{event[2][0]}")]
        for event in afisha_card
    ]
    # Создание клавиатуры с кнопками выбора даты концерта
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    # Отправка сообщения пользователю с клавиатурой выбора даты концерта
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text="Выберите дату концерта",
        reply_markup=keyboard,
    )
    # Сохранение данных афиши в пользовательскую базу данных бота
    context.user_data["afisha_card"] = afisha_card


async def afisha_callback(update, context):
    """Отправка сообщения с заголовком и текстом события, выбранного пользователем."""
    query = update.callback_query
    await query.answer()
    print(query.data.split("_")[1])
    # Получение выбранного события
    selected_event = [event for event in context.user_data["afisha_card"] if event[2][0] == query.data.split("_")[1]][0]
    # Отправка фото
    await context.bot.send_photo(chat_id=query.message.chat_id, photo=selected_event[4])
    # Создание кнопок
    buy_button = InlineKeyboardButton(text="Купить билет", url=selected_event[5])
    more_info_button = InlineKeyboardButton(text="Подробнее", callback_data=f"more_info_{selected_event[2][0]}")
    prev_button = InlineKeyboardButton(text="<", callback_data=f"prev_{selected_event[2][0]}")
    next_button = InlineKeyboardButton(text=">", callback_data=f"next_{selected_event[2][0]}")
    # Создание разметки с кнопками
    keyboard = [[buy_button, more_info_button], [prev_button, next_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Создание текста сообщения
    text = f"{selected_event[0]}\n\n{selected_event[2][1]} - {selected_event[3][1]}"
    # Отправка сообщения
    await context.bot.send_message(chat_id=query.message.chat_id, text=text, reply_markup=markup)
    #media = InputMediaPhoto(media=selected_event[4], caption=text)
    #await query.edit_message_media(media=media, reply_markup=markup)


async def more_info_callback(update, context):
    """Редактирование сообщения, добавление подробной информации о выбранном событии."""
    query = update.callback_query
    print(query.data.split("_"))
    await query.answer()
    # Получение выбранного события
    selected_event = [event for event in context.user_data["afisha_card"] if event[2][0] == query.data.split("_")[2]][0]
    # Создание кнопок
    buy_button = InlineKeyboardButton(text="Купить билет", url=selected_event[5])
    prev_button = InlineKeyboardButton(text="<", callback_data=f"prev_{selected_event[2][0]}")
    next_button = InlineKeyboardButton(text=">", callback_data=f"next_{selected_event[2][0]}")
    # Создание разметки с кнопками
    keyboard = [[buy_button], [prev_button, next_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Редактирование сообщения
    text = f"{selected_event[0]}\n\n{selected_event[2][1]} - {selected_event[3][1]}\n\n{selected_event[1]}"
    await query.edit_message_text(text=text, reply_markup=markup)

async def prev_callback(update, context):
    """Переход к предыдущему событию в списке afisha_card."""
    query = update.callback_query
    await query.answer()
    print(query.data.split("_"))
    # Получение выбранного события
    selected_event = [event for event in context.user_data["afisha_card"] if event[2][0] == query.data.split("_")[1]][0]
    # Поиск индекса выбранного события в списке
    index = context.user_data["afisha_card"].index(selected_event)
    # Выбор предыдущего события в списке (если есть)
    if index > 0:
        prev_event = context.user_data["afisha_card"][index - 1]
        # Создание кнопок
        buy_button = InlineKeyboardButton(text="Купить билет", url=prev_event[5])
        more_info_button = InlineKeyboardButton(text="Подробнее", callback_data=f"more_info_{prev_event[2][0]}")
        prev_button = InlineKeyboardButton(text="<", callback_data=f"prev_{prev_event[2][0]}")
        next_button = InlineKeyboardButton(text=">", callback_data=f"next_{prev_event[2][0]}")
        # Создание разметки с кнопками
        keyboard = [[buy_button, more_info_button], [prev_button, next_button]]
        markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        # Создание текста сообщения
        text = f"{prev_event[0]}\n\n{prev_event[2][1]} - {prev_event[3][1]}"
        # Редактирование сообщения с новым событием и новыми кнопками
        await query.message.edit_text(text=text, reply_markup=markup)
    else:
        # Если выбранное событие первое в списке, то просто отправляем сообщение без изменений
        await query.message.answer(text="Вы находитесь на первом событии.")

async def next_callback(update, context):
    """Обработка нажатия на кнопку 'Следующее событие'."""
    query = update.callback_query
    await query.answer()
    print(query.data.split("_"))
    # Получение списка всех событий
    events = context.user_data["afisha_card"]
    # Получение индекса текущего события
    current_index = [i for i, event in enumerate(events) if event[2][0] == query.data.split("_")[1]][0]
    # Получение индекса следующего события
    next_index = current_index + 1 if current_index < len(events) - 1 else 0
    # Получение следующего события
    next_event = events[next_index]
    # Создание кнопок
    buy_button = InlineKeyboardButton(text="Купить билет", url=next_event[5])
    more_info_button = InlineKeyboardButton(text="Подробнее", callback_data=f"more_info_{next_event[2][0]}")
    prev_button = InlineKeyboardButton(text="<", callback_data=f"prev_{next_event[2][0]}")
    next_button = InlineKeyboardButton(text=">", callback_data=f"next_{next_event[2][0]}")
    # Создание разметки с кнопками
    keyboard = [[buy_button, more_info_button], [prev_button, next_button]]
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Создание текста сообщения
    text = f"{next_event[0]}\n\n{next_event[2][1]} - {next_event[3][1]}"
    # Редактирование сообщения
    await context.bot.edit_message_text(chat_id=query.message.chat_id, message_id=query.message.message_id,
                                       text=text, reply_markup=markup)


async def giveaway(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Розыгрыш билетов'."""
    await update.message.reply_text("какой-то розыгрыш билетов")


async def performers(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Исполнители'."""
    await update.message.reply_text("список исполнителей")


async def feedback(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Обратная связь'."""
    await update.message.reply_text("напишите нам на почту")


def main():
    """Запуск бота."""
    # Создание приложения и передача ему токена вашего бота.
    application = Application.builder().token("6241891253:AAEtTI5Ma8z34FM3fOusBJoLqI7xtRGLnTU").build()
    # Назначение обработчиков на различные команды в Telegram.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    # Добавление обработчиков для каждой кнопки
    application.add_handler(
        MessageHandler(filters.Regex("^Афиша$"), callback=afisha)
    )
    #application.add_handler(
    #    CallbackQueryHandler(callback=afisha_callback)
    #)

    # Регистрация обработчиков
    application.add_handler(CallbackQueryHandler(callback=afisha_callback, pattern=r"event_\d+"))
    application.add_handler(CallbackQueryHandler(callback=more_info_callback, pattern=r"more_info_\d+"))
    application.add_handler(CallbackQueryHandler(callback=prev_callback, pattern=r"prev_\d+"))
    application.add_handler(CallbackQueryHandler(callback=next_callback, pattern=r"next_\d+"))

    application.add_handler(
        MessageHandler(filters.Regex("^Розыгрыш билетов$"), callback=giveaway)
    )
    application.add_handler(
        MessageHandler(filters.Regex("^Исполнители$"), callback=performers)
    )
    application.add_handler(
        MessageHandler(filters.Regex("^Обратная связь$"), callback=feedback)
    )
    # Запуск бота и ожидание его завершения пользователем (нажатие Ctrl-C).
    application.run_polling()

if __name__ == "__main__":
    main()