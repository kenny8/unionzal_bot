import logging
from telegram import ReplyKeyboardMarkup
import settings
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
    global reply_keyboard
    reply_keyboard = ReplyKeyboardMarkup(
        [["Афиша", "Розыгрыш билетов"], ["Исполнители", "Обратная связь", "Выход"]],
        resize_keyboard=True,  # изменить размер клавиатуры
    )
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text=f"вы вошли в админку\nинтересный факт, столько пользователей пользуютя ботом: {len(settings.USERS)}",
                                   reply_markup=reply_keyboard)
    context.user_data["admin"] = True
    admin_status = context.user_data.get("admin", False)
    logger.info(
        f"Пользователь {update.effective_user.username} вызвал функцию {admin.__name__}. Статус админа: {admin_status}")

async def admin_out(update, context):
    if context.user_data is not None:
        search_query = context.user_data.get("admin")
        if search_query is not None:
            if context.user_data["admin"]:
                global reply_keyboard
                reply_keyboard = ReplyKeyboardMarkup(
                    [["Афиша", "Розыгрыш билетов"], ["Исполнители", "Обратная связь"]],
                    resize_keyboard=True,  # изменить размер клавиатуры
                )
                await context.bot.send_message(chat_id=update.message.chat_id,
                                               text="вы вышли из админки",
                                               reply_markup=reply_keyboard)
                context.user_data["admin"] = False
                admin_status = context.user_data.get("admin", False)
                logger.info(
                    f"Пользователь {update.effective_user.username} вызвал функцию {admin_out.__name__}. Статус админа: {admin_status}")
