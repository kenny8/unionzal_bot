
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
        [InlineKeyboardButton(text=event[2][0], callback_data=event[2][0])]
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
    await query.edit_message_text(text=f"Вы выбрали: {query.data}")
    print("looooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooool")


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
    application.add_handler(
        CallbackQueryHandler(callback=afisha_callback)
    )
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