
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
from performers import performers, performers_callback, performers_search_name

# Включение логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Создание разметки клавиатуры для меню
reply_keyboard = ReplyKeyboardMarkup(
    [["Афиша", "Розыгрыш билетов"], ["Исполнители", "Обратная связь"]]
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

async def admin(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку для входа в админку."""
    # Отправка сообщения пользователю с клавиатурой выбора даты концерта
    global reply_keyboard
    reply_keyboard = ReplyKeyboardMarkup(
        [["Афиша", "Розыгрыш билетов"], ["Исполнители", "Обратная связь", "Выход"]]
    )
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text="вы вошли в админку",
                                   reply_markup=reply_keyboard)
    context.user_data["admin"] = True

async def admin_out(update, context):
    if context.user_data["admin"]:
        global reply_keyboard
        reply_keyboard = ReplyKeyboardMarkup(
            [["Афиша", "Розыгрыш билетов"], ["Исполнители", "Обратная связь"]]
        )
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text="вы вышли из админки",
                                       reply_markup=reply_keyboard)
        context.user_data["admin"] = False


# Определение обработчиков команд. Обычно они принимают два аргумента: update и context.
async def start(update, context):
    """Отправка сообщения, когда пользователь вводит команду /start."""
    user = update.effective_user
    # Отправка сообщения пользователю
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! это бот липецкой филармонии!",
        reply_markup=reply_keyboard,
    )

async def help_command(update, context):
    """Отправка сообщения, когда пользователь вводит команду /help."""
    # Отправка сообщения пользователю с инструкцией, что нужно делать
    await update.message.reply_text("Нужна помощь? помоги себе сам")

async def giveaway(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Розыгрыш билетов'."""
    await update.message.reply_text("какой-то розыгрыш билетов")

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
        MessageHandler(filters.Regex(f"^{settings.PASSWORD}$"), callback=admin)
    )
    application.add_handler(
        MessageHandler(filters.Regex(f"^Выход$"), callback=admin_out)
    )
    application.add_handler(
        MessageHandler(filters.Regex("^Исполнители$"), callback=performers)
    )
    application.add_handler(CallbackQueryHandler(callback=performers_callback, pattern=r"performers_event_\d*"))
    application.add_handler(CallbackQueryHandler(callback=performers_callback, pattern=r"performers_card_\d*"))
    application.add_handler(CallbackQueryHandler(callback=performers_callback, pattern=r"performers_back_\d*"))
    application.add_handler(CallbackQueryHandler(callback=performers_callback, pattern=r"performers_search_\d*"))


    application.add_handler(
        MessageHandler(filters.Regex("^Обратная связь$"), callback=feedback)
    )

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, performers_search_name))
    # Запуск бота и ожидание его завершения пользователем (нажатие Ctrl-C).
    application.run_polling()

if __name__ == "__main__":
    main()