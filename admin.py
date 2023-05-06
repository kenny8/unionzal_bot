
from telegram import ReplyKeyboardMarkup

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