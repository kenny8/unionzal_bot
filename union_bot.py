
import logging
from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Включение логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[["Главная", "Афиша"], ["Исполнители", "Билеты"]]
)


# Определение обработчиков команд. Обычно они принимают два аргумента: update и context.
"""async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """"""Отправка сообщения, когда пользователь вводит команду /start.""""""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка сообщения, когда пользователь вводит команду /start."""
    user = update.effective_user
    reply_keyboard = ReplyKeyboardMarkup(
        [["главная", "афиша"], ["исполнители", "билеты"]]
    )
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}!",
        reply_markup=reply_keyboard,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка сообщения, когда пользователь вводит команду /help."""
    await update.message.reply_text("Нужна помощь? помоги себе сам")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Эхо-ответ на сообщение пользователя."""
    await update.message.reply_text(update.message.text)


def main() -> None:
    """Запуск бота."""
    # Создание приложения и передача ему токена вашего бота.
    application = Application.builder().token("6241891253:AAEtTI5Ma8z34FM3fOusBJoLqI7xtRGLnTU").build()

    # Назначение обработчиков на различные команды в Telegram.
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Обработка любых сообщений, кроме команд.
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запуск бота и ожидание его завершения пользователем (нажатие Ctrl-C).
    application.run_polling()


if __name__ == "__main__":
    main()