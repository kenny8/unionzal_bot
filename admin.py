import logging
from telegram import ReplyKeyboardMarkup
import settings
import pickle
# Включение логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def admin(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку для входа в админку."""
    # Отправка сообщения пользователю с клавиатурой выбора даты концерта
    user = update.effective_user
    reply_keyboard = ReplyKeyboardMarkup(
        [["Афиша", "Розыгрыш билетов"], ["Исполнители", "Обратная связь", "Выход"]],
        resize_keyboard=True,  # изменить размер клавиатуры
    )
    context.user_data["admin"] = True
    admin_status = context.user_data.get("admin", False)
    admin = "@" + str(user.username)
    if admin in [i[0] for i in settings.ADMIN_STATUS]:
        for i, item in enumerate(settings.ADMIN_STATUS):
            if item[0] == admin:
                settings.ADMIN_STATUS[i][1] = True
                break
    else:
        settings.ADMIN_STATUS.append([admin, True])
    with open(settings.ADMIN_TXT, 'wb') as file:
        pickle.dump(settings.ADMIN_STATUS, file)

    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=f"вы вошли в админку\nинтересный факт, столько пользователей пользуютя ботом: {len(settings.USERS)}",
                                   reply_markup=reply_keyboard)
    logger.info(
        f"Пользователь {update.effective_user.username} вызвал функцию admin. Статус админа: {admin_status}")

async def admin_out(update, context):
    user = update.effective_user
    if context.user_data is not None:
        search_query = context.user_data.get("admin")
        if search_query is not None:
            if context.user_data["admin"]:
                reply_keyboard = ReplyKeyboardMarkup(
                    [["Афиша", "Розыгрыш билетов"], ["Исполнители", "Обратная связь"]],
                    resize_keyboard=True,  # изменить размер клавиатуры
                )
                admin = "@" + str(user.username)
                if admin in [i[0] for i in settings.ADMIN_STATUS]:
                    for i, item in enumerate(settings.ADMIN_STATUS):
                        if item[0] == admin:
                            settings.ADMIN_STATUS[i][1] = False
                            break
                with open(settings.ADMIN_TXT, 'wb') as file:
                    pickle.dump(settings.ADMIN_STATUS, file)
                await context.bot.send_message(chat_id=update.message.chat_id,
                                               text="вы вышли из админки",
                                               reply_markup=reply_keyboard)
                context.user_data["admin"] = False
                admin_status = context.user_data.get("admin", False)
                logger.info(
                    f"Пользователь {update.effective_user.username} вызвал функцию {admin_out.__name__}. Статус админа: {admin_status}")

async def update_admin_status(update, context):
    user = update.effective_user
    admin = "@" + str(user.username)
    if admin in [i[0] for i in settings.ADMIN_STATUS]:
        for i, item in enumerate(settings.ADMIN_STATUS):
            if item[0] == admin:
                context.user_data["admin"] = settings.ADMIN_STATUS[i][1]
                break
        else:
            context.user_data["admin"] = False
