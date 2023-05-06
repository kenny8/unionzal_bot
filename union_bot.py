
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
    user = update.effective_user
    print(user.username)
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

async def feedback(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Обратная связь'."""
    admin_in = context.user_data.get("admin")
    if admin_in is not None and context.user_data["admin"]:
        if len(settings.FEEDBACK_USER) > 0:
            text = f"всего отзывов: {len(settings.FEEDBACK_USER)}\n пользователь: {settings.FEEDBACK_USER[0][0]} \n\n {settings.FEEDBACK_USER[0][1]}"
            delete_feedback_button = InlineKeyboardButton(text="удалить", callback_data=f"feedback_delete_0")
            next_feedback_button = InlineKeyboardButton(text=">", callback_data=f"feedback_next_1")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[delete_feedback_button], [next_feedback_button]])
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text=text,
                                           reply_markup=keyboard)
        else:
            text = "отзывов нету"
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text=text)
        print("lol")
    if admin_in is None or admin_in is not None and context.user_data["admin"] is False:
        user = update.effective_user
        print(user.username)
        text = "напишите свой отзыв/проблему с которой столкнулись"
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text=text)
        context.user_data["feedback"] = True

async def feedback_callback(update, context):
    query = update.callback_query
    data = query.data.split("_")
    print(data)
    if data[1] == "delete":
        if len(settings.FEEDBACK_USER) > 0:
            text = f"удалено"
            settings.FEEDBACK_USER[int(data[2])] = None  # заменяем элемент на None
            del settings.FEEDBACK_USER[int(data[2])]  # удаляем элемент None из списка
            if data[2] == 1:
                next_feedback_button = InlineKeyboardButton(text=">",
                                                            callback_data=f"feedback_next_{data[2]}")
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[[next_feedback_button]])
            elif int(data[2]) == len(settings.FEEDBACK_USER) - 1:
                prev_feedback_button = InlineKeyboardButton(text="<",
                                                            callback_data=f"feedback_prev_{data[2]}")
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[[prev_feedback_button]])
            else:
                prev_feedback_button = InlineKeyboardButton(text="<",
                                                            callback_data=f"feedback_prev_{data[2]}")
                next_feedback_button = InlineKeyboardButton(text="<", callback_data=f"feedback_prev_{data[2]}")
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[[prev_feedback_button, next_feedback_button]])
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                reply_markup=keyboard
            )
        else:
            text = f"больше отзывов нету"
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
            )
    elif data[1] == "prev":
        text = f"всего отзывов: {len(settings.FEEDBACK_USER)}\n пользователь: {settings.FEEDBACK_USER[int(data[2])][0]} \n\n {settings.FEEDBACK_USER[int(data[2])][1]}"
        delete_feedback_button = InlineKeyboardButton(text="удалить", callback_data=f"feedback_delete_{data[2]}")
        next_feedback_button = InlineKeyboardButton(text=">",
                                                    callback_data=f"feedback_next_{str(int(data[2]) + 1)}")
        if data[2] == 0:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button], [next_feedback_button]])
        else:
            prev_feedback_button = InlineKeyboardButton(text="<",
                                                        callback_data=f"feedback_prev_{str(int(data[2]) - 1)}")
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button], [prev_feedback_button, next_feedback_button]])
        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard
        )
    elif data[1] == "next":
        text = f"всего отзывов: {len(settings.FEEDBACK_USER)}\n пользователь: {settings.FEEDBACK_USER[int(data[2])][0]} \n\n {settings.FEEDBACK_USER[int(data[2])][1]}"
        delete_feedback_button = InlineKeyboardButton(text="удалить", callback_data=f"feedback_delete_{data[2]}")
        prev_feedback_button = InlineKeyboardButton(text="<", callback_data=f"feedback_prev_{str(int(data[2]) - 1)}")
        if int(data[2]) == len(settings.FEEDBACK_USER) - 1:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button], [prev_feedback_button]])
        else:
            next_feedback_button = InlineKeyboardButton(text=">",
                                                        callback_data=f"feedback_next_{str(int(data[2]) + 1)}")
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button], [prev_feedback_button, next_feedback_button]])
        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard
        )


async def feedback_text(update, context):
    search_query = context.user_data.get("feedback")
    if search_query is not None:
        if context.user_data["feedback"]:
            user = update.effective_user
            print(user.username)
            # Получение введенного пользователем имени
            text_feedback = update.message.text
            text = f"Ваше мнение для нас очень важно, но не очень то и нужно"# незабудь исправить а то лажа будет
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text=text)
            context.user_data["feedback"] = False
            settings.FEEDBACK_USER.append(["@" + str(user.username), text_feedback])

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

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_text))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, giveaway_text))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, performers_search_name))
    # Запуск бота и ожидание его завершения пользователем (нажатие Ctrl-C).
    application.run_polling()

if __name__ == "__main__":
    main()