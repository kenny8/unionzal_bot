from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import settings
import pickle
import logging
import functools
from admin import update_admin_status

# Включение логгирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def log_user_action(func):
    def wrapper(update, context, *args, **kwargs):
        user = update.effective_user
        logger.info(f"Пользователь {user.username} вызвал функцию {func.__name__}")
        return func(update, context, *args, **kwargs)
    return wrapper

@log_user_action
async def feedback(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Обратная связь'."""
    await update_admin_status(update, context)
    admin_in = context.user_data.get("admin")
    if admin_in is not None and context.user_data["admin"]:
        if len(settings.FEEDBACK_USER) > 0:
            max_len = False
            text = f"всего отзывов: {len(settings.FEEDBACK_USER)}\n "
            for i, feedback in enumerate(settings.FEEDBACK_USER):
                read_status = "прочитано" if feedback[2] else "не прочитано"
                text += f"{i + 1}. Статус: {read_status}\n"
                if len(text) >= settings.MAX_MESSAGE_LENGTH:
                    max_len = True
                    break
            buttons = []
            for i in range(1, len(settings.FEEDBACK_USER) + 1):
                buttons.append(InlineKeyboardButton(text=str(i), callback_data=f"feedback_prev_{1}"))
            if max_len:
                buttons.append(InlineKeyboardButton(text="дальше", callback_data=f"feedback_more_{i-1}"))
            keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text=text,
                                           reply_markup=keyboard)
        else:
            text = "отзывов нету"
            await context.bot.send_message(chat_id=update.message.chat_id,
                                           text=text)
    if admin_in is None or admin_in is not None and context.user_data["admin"] is False:
        user = update.effective_user
        text = "напишите свой отзыв/проблему с которой столкнулись"
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text=text)
        context.user_data["feedback"] = True


@log_user_action
async def feedback_callback(update, context):
    query = update.callback_query
    data = query.data.split("_")
    if data[1] == "delete":
        if len(settings.FEEDBACK_USER) > 0:
            settings.FEEDBACK_USER[int(data[2])] = None  # заменяем элемент на None
            del settings.FEEDBACK_USER[int(data[2])]  # удаляем элемент None из списка
            next_feedback_button = InlineKeyboardButton(text="вернутся",
                                                        callback_data=f"feedback_next_0")  # Изменить значение data[2] для следующей карточки
            if len(settings.FEEDBACK_USER) == 0:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[])
            else:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[[next_feedback_button]])
            text1 = f"удалено"
            text2 =  f"больше отзывов нету"
            if len(settings.FEEDBACK_USER) == 0:
                text = text2
            else:
                text = text1
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                reply_markup=keyboard
            )
            with open('feedback_fl.txt', 'wb') as file:
                pickle.dump(settings.FEEDBACK_USER, file)

        else:
            text = f"больше отзывов нету"
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
            )
    elif data[1] == "read":
        text = "уже отмеченно" if settings.FEEDBACK_USER[int(data[2])][2] else "отмеченно как прочитаное"
        settings.FEEDBACK_USER[int(data[2])][2] = False
        await context.bot.answer_callback_query(callback_query_id=query.id, text=text)
        with open('feedback_fl.txt', 'wb') as file:
            pickle.dump(settings.FEEDBACK_USER, file)
    elif data[1] == "prev":
        read_status = "прочитано" if settings.FEEDBACK_USER[int(data[2])][2] else "не прочитано"
        text = f"всего отзывов: {len(settings.FEEDBACK_USER)}\n пользователь: {settings.FEEDBACK_USER[int(data[2])][0]} \n" \
               f" {read_status}\n {settings.FEEDBACK_USER[int(data[2])][1]}"
        delete_feedback_button = InlineKeyboardButton(text="удалить", callback_data=f"feedback_delete_{data[2]}")
        next_feedback_button = InlineKeyboardButton(text=">",
                                                    callback_data=f"feedback_next_{int(data[2]) + 1}")  # Изменить значение data[2] для следующей карточки
        prev_feedback_button = InlineKeyboardButton(text="<",
                                                    callback_data=f"feedback_prev_{int(data[2]) - 1}")  # Изменить значение data[2] для предыдущей карточки
        read_feedback_button = InlineKeyboardButton(text="прочитать",
                                                    callback_data=f"feedback_read_{int(data[2])}")  # Изменить значение data[2] для предыдущей карточки
        if data[2] == "0":
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button, read_feedback_button], [next_feedback_button]])
        elif len(settings.FEEDBACK_USER) == 1:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button, read_feedback_button]])
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button, read_feedback_button], [prev_feedback_button, next_feedback_button]])
        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard
        )
    elif data[1] == "next":
        read_status = "прочитано" if settings.FEEDBACK_USER[int(data[2])][2] else "не прочитано"
        text = f"всего отзывов: {len(settings.FEEDBACK_USER)}\n пользователь: {settings.FEEDBACK_USER[int(data[2])][0]} \n" \
               f" {read_status}\n {settings.FEEDBACK_USER[int(data[2])][1]}"
        delete_feedback_button = InlineKeyboardButton(text="удалить", callback_data=f"feedback_delete_{data[2]}")
        next_feedback_button = InlineKeyboardButton(text=">",
                                                    callback_data=f"feedback_next_{int(data[2]) + 1}")  # Изменить значение data[2] для следующей карточки
        prev_feedback_button = InlineKeyboardButton(text="<",
                                                    callback_data=f"feedback_prev_{int(data[2]) - 1}")  # Изменить значение data[2] для предыдущей карточки
        read_feedback_button = InlineKeyboardButton(text="прочитать",
                                                    callback_data=f"feedback_read_{int(data[2])}")  # Изменить значение data[2] для предыдущей карточки
        if len(settings.FEEDBACK_USER) == 1:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button, read_feedback_button]])
        elif data[2] == str(len(settings.FEEDBACK_USER)-1):
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button, read_feedback_button], [prev_feedback_button]])
        elif data[2] == "0":
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button, read_feedback_button], [next_feedback_button]])
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button, read_feedback_button], [prev_feedback_button, next_feedback_button]])

        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard
        )


@log_user_action
async def feedback_text(update, context):
    if context.user_data is not None:
        search_query = context.user_data.get("feedback")
        if search_query is not None:
            if context.user_data["feedback"]:
                user = update.effective_user
                # Получение введенного пользователем имени
                text_feedback = update.message.text
                text = f"Ваше мнение для нас очень важно" #, но не очень то и нужно"  # незабудь исправить а то лажа будет
                await context.bot.send_message(chat_id=update.message.chat_id,
                                               text=text)
                context.user_data["feedback"] = False
                settings.FEEDBACK_USER.append(["@" + str(user.username), text_feedback, False])
                with open(settings.FEEDBACK_TXT, 'wb') as file:
                    pickle.dump(settings.FEEDBACK_USER, file)