
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
import random
from telegram import InputMediaPhoto
import asyncio
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

async def giveaway(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Розыгрыш билетов'."""
    admin_in = context.user_data.get("admin")
    if admin_in is not None:
        if context.user_data["admin"]:
            if settings.START_GIVEAWAY[0] is False:
                start_button = InlineKeyboardButton(text="начать", callback_data=f"giveaway_admin_start_0")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[start_button]])
            else:
                stop_button = InlineKeyboardButton(text="завершить", callback_data=f"giveaway_admin_stop_")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[stop_button]])
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text="вы вошли в розыгрыши",
                                           reply_markup=keyboard)
    elif admin_in is None or admin_in is not None and context.user_data["admin"] is False:
        if settings.START_GIVEAWAY[0]:
            start_giveaway_button = InlineKeyboardButton(text="учавствовать", callback_data=f"giveaway_user_0")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[start_giveaway_button]])
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text=settings.START_GIVEAWAY[1],
                                           reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text="пока нет розыгрышей")

async def giveaway_callback(update, context):
    query = update.callback_query
    data = query.data.split("_")
    print(data)
    if data[1] == "admin" and data[2] == "start":
        if data[3] == "0":
            text = "Выберите длительность розыгрыша:"
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("1 день", callback_data=f"giveaway_admin_start_1_1")],
                [InlineKeyboardButton("2 дня", callback_data=f"giveaway_admin_start_1_2")],
                [InlineKeyboardButton("5 дней", callback_data=f"giveaway_admin_start_1_5")],
                [InlineKeyboardButton("7 дней", callback_data=f"giveaway_admin_start_1_7")]
            ])
            await context.bot.send_message(chat_id=query.message.chat_id,
                                           text=text,
                                           reply_markup=reply_markup)
        if data[3] == "1":
            text = "введите текст розыгрыша"
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("назад", callback_data=f"giveaway_admin_start_0_")]])
            await context.bot.send_message(chat_id=query.message.chat_id,
                                           text=text,
                                           reply_markup=reply_markup)

            query = update.callback_query
            context.user_data["giveaway_Text_start"] = True
            context.user_data["giveaway_time_start"] = int(data[4])
    elif data[1] == "admin" and data[2] == "stop":
        settings.START_GIVEAWAY[0] = False
        text = "розыгрышь завершен"
        await context.bot.send_message(chat_id=query.message.chat_id,
                                       text=text)
    elif data[1] == "user":
        if data[2] == "0":
            user = update.effective_user
            # Получаем ID пользователя и чата
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            user_status = await context.bot.get_chat_member(chat_id='@' + settings.CHAT, user_id=user_id)
            print(user_status.status)
            if user_status.status == 'member' or user_status.status == 'creator' or user_status.status == 'administrator':
                await context.bot.send_message(chat_id=chat_id,
                                               text='вы присоединились к розыгрышу')
                user = update.effective_user
                print(user.username)
                settings.START_GIVEAWAY[4].append(user.username)
            else:
                community_button = InlineKeyboardButton(text="Подписаться", url=f"t.me/{settings.CHAT}")
                check_button = InlineKeyboardButton(text="Проверить", callback_data=f"giveaway_user_0_")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[community_button, check_button]])
                await context.bot.send_message(chat_id=chat_id,
                                               text=f"Пожалуйста, подпишитесь на канал t.me/{settings.CHAT}, чтобы принять участие в розыгрыше.",
                                               reply_markup=keyboard)

async def giveaway_text(update, context):
    search_query = context.user_data.get("giveaway_Text_start")
    if search_query is not None:
        if context.user_data["giveaway_Text_start"]:
            user = update.effective_user
            print(user.username)
            # Получение введенного пользователем имени
            text_admin = update.message.text
            time = str(context.user_data["giveaway_time_start"])
            text = f"розыгрыш начат \n текст: {text_admin} \n время: {time} дней"
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text=text)
            context.user_data["giveaway_Text_start"] = False
            settings.START_GIVEAWAY = [True, text_admin, int(time), user.username, []]

async def choose_winner(context):
    if settings.START_GIVEAWAY[0]:
        if len(settings.START_GIVEAWAY[4]) > 0:
            winner = random.choice(settings.START_GIVEAWAY[4])
            return winner
    return None

async def end_giveaway(context):
    winner = await choose_winner(context)
    print("lollllllllllllll")
    if winner is not None:
        await context.bot.send_message(chat_id='@' + settings.CHAT, text=f'Победитель розыгрыша: {winner}!')
    else:
        await context.bot.send_message(chat_id='@' + settings.CHAT, text='Розыгрыш окончен, но нет победителя :(')

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

    application.add_handler(CallbackQueryHandler(callback=giveaway_callback, pattern=r"giveaway_admin_start_\d*"))
    application.add_handler(CallbackQueryHandler(callback=giveaway_callback, pattern=r"giveaway_admin_stop_\d*"))
    application.add_handler(CallbackQueryHandler(callback=giveaway_callback, pattern=r"giveaway_user_\d*"))
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, giveaway_text))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, performers_search_name))
    # запустить функцию через 5 минут после начала розыгрыша
    loop = asyncio.get_event_loop()
    loop.call_later(300, asyncio.ensure_future, end_giveaway(context))
    # Запуск бота и ожидание его завершения пользователем (нажатие Ctrl-C).
    application.run_polling()

if __name__ == "__main__":
    main()