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
import settings
from afisha_ import afisha_callback, more_info_callback, read_more_callback, prev_callback, next_callback, afisha
from performers import performers, performers_callback, performers_search_name
from giveaway import giveaway, giveaway_callback, giveaway_text
from feedback import feedback, feedback_callback, feedback_text
from admin import admin_out, admin
from datetime import datetime
import pickle

# Включение логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Декоратор для логирования вызова функции
def log_user_action(func):
    def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        logger.info(f"Пользователь {user.username} вызвал функцию {func.__name__}")
        return func(update, context, *args, **kwargs)
    return wrapper

# Создание разметки клавиатуры для меню
reply_keyboard = ReplyKeyboardMarkup(
    [["Афиша", "Розыгрыш билетов"], ["Исполнители", "Обратная связь"]],
    resize_keyboard=True, # изменить размер клавиатуры
)


# Определение обработчиков команд. Обычно они принимают два аргумента: update и context.
# Функция обработки команды /start с декоратором логирования
@log_user_action
async def start(update, context):
    """Отправка сообщения, когда пользователь вводит команду /start."""
    user = update.effective_user
    # Отправка сообщения пользователю
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! это бот липецкой филармонии!",
        reply_markup=reply_keyboard,
    )
    if update.effective_chat.id not in [chat[1] for chat in settings.USERS]:
        settings.USERS.append([user.username, update.effective_chat.id])
    else:
        index = [chat[1] for chat in settings.USERS].index(update.effective_chat.id)
        settings.USERS[index] = [user.username, update.effective_chat.id]
    with open(settings.USERS_TXT, 'wb') as file:
        pickle.dump(settings.USERS, file)
    vk = InlineKeyboardButton(text="vk", url="https://vk.com/unionzal")
    dzen = InlineKeyboardButton(text="dzen", url="https://dzen.ru/id/623981f3b6c1bf4924ba9525")
    tg = InlineKeyboardButton(text="tg", url="https://t.me/filarmonia48")
    ok = InlineKeyboardButton(text="ok", url="https://ok.ru/group54024261795965")
    union = InlineKeyboardButton(text="union", url="https://unionzal.ru")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[tg, vk, ok ], [dzen, union]])
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text="вот наши социалки",
                                   reply_markup=keyboard)
# Функция обработки команды /help с декоратором логирования
@log_user_action
async def help_command(update, context):
    """Отправка сообщения, когда пользователь вводит команду /help."""
    # Отправка сообщения пользователю с инструкцией, что нужно делать
    admin_in = context.user_data.get("admin")
    if admin_in is not None and context.user_data["admin"]:
        text = "сейчас вы под админкой\n в розыгрышах можно настроить сам конкурс и обьявить об его окончании\n в отзывах можно посмотреть что написали люди"
    if admin_in is None or admin_in is not None and context.user_data["admin"] is False:
        text = "в афиши можно посмотреть ближайшие концерты\n в исполнителях узнать какие музыканты есть в нашей филармонии\n в розыгрышах можно выйграть билет на концерт\n в отзывах написать что отзывы"
    await update.message.reply_text(text)

async def text_reader(update, context):
    await giveaway_text(update, context)
    await feedback_text(update, context)
    await performers_search_name(update, context)

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

    application.add_handler(CallbackQueryHandler(callback=giveaway_callback, pattern=r"giveaway_admin_start_\d*"))
    application.add_handler(CallbackQueryHandler(callback=giveaway_callback, pattern=r"giveaway_admin_stop_\d*"))
    application.add_handler(CallbackQueryHandler(callback=giveaway_callback, pattern=r"giveaway_user_\d*"))
    application.add_handler(CallbackQueryHandler(callback=giveaway_callback, pattern=r"giveaway_back_\d*"))
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
    application.add_handler(CallbackQueryHandler(callback=feedback_callback, pattern=r"feedback_delete_\d+"))
    application.add_handler(CallbackQueryHandler(callback=feedback_callback, pattern=r"feedback_prev_\d+"))
    application.add_handler(CallbackQueryHandler(callback=feedback_callback, pattern=r"feedback_next_\d+"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_reader))
    # Запуск бота и ожидание его завершения пользователем (нажатие Ctrl-C).
    application.run_polling()

if __name__ == "__main__":
    main()