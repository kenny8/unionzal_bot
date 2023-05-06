from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import settings
import pickle
async def feedback(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Обратная связь'."""
    admin_in = context.user_data.get("admin")
    if admin_in is not None and context.user_data["admin"]:
        if len(settings.FEEDBACK_USER) > 0:
            text = f"всего отзывов: {len(settings.FEEDBACK_USER)}\n пользователь: {settings.FEEDBACK_USER[0][0]} \n\n {settings.FEEDBACK_USER[0][1]}"
            delete_feedback_button = InlineKeyboardButton(text="удалить", callback_data=f"feedback_delete_0")
            next_feedback_button = InlineKeyboardButton(text=">", callback_data=f"feedback_next_1")
            if len(settings.FEEDBACK_USER) == 1:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[])
            else:
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
    elif data[1] == "prev":
        text = f"всего отзывов: {len(settings.FEEDBACK_USER)}\n пользователь: {settings.FEEDBACK_USER[int(data[2])][0]} \n\n {settings.FEEDBACK_USER[int(data[2])][1]}"
        delete_feedback_button = InlineKeyboardButton(text="удалить", callback_data=f"feedback_delete_{data[2]}")
        next_feedback_button = InlineKeyboardButton(text=">",
                                                    callback_data=f"feedback_next_{int(data[2]) + 1}")  # Изменить значение data[2] для следующей карточки
        prev_feedback_button = InlineKeyboardButton(text="<",
                                                    callback_data=f"feedback_prev_{int(data[2]) - 1}")  # Изменить значение data[2] для предыдущей карточки
        if data[2] == "0":
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button], [next_feedback_button]])
        elif len(settings.FEEDBACK_USER) == 1:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button]])
        else:
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
        next_feedback_button = InlineKeyboardButton(text=">",
                                                    callback_data=f"feedback_next_{int(data[2]) + 1}")  # Изменить значение data[2] для следующей карточки
        prev_feedback_button = InlineKeyboardButton(text="<",
                                                    callback_data=f"feedback_prev_{int(data[2]) - 1}")  # Изменить значение data[2] для предыдущей карточки
        if len(settings.FEEDBACK_USER) == 1:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button]])
        elif data[2] == str(len(settings.FEEDBACK_USER)-1):
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button], [prev_feedback_button]])
        elif data[2] == "0":
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button], [next_feedback_button]])
        else:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[delete_feedback_button], [prev_feedback_button, next_feedback_button]])

        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=text,
            reply_markup=keyboard
        )


async def feedback_text(update, context):
    if context.user_data is not None:
        search_query = context.user_data.get("feedback")
        if search_query is not None:
            if context.user_data["feedback"]:
                user = update.effective_user
                print(user.username)
                # Получение введенного пользователем имени
                text_feedback = update.message.text
                text = f"Ваше мнение для нас очень важно, но не очень то и нужно"  # незабудь исправить а то лажа будет
                await context.bot.send_message(chat_id=update.message.chat_id,
                                               text=text)
                context.user_data["feedback"] = False
                settings.FEEDBACK_USER.append(["@" + str(user.username), text_feedback])
                with open(settings.FEEDBACK_TXT, 'wb') as file:
                    pickle.dump(settings.FEEDBACK_USER, file)