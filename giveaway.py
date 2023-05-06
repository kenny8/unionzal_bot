
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import random
import settings
import pickle

async def giveaway(update, context):
    """Отправка сообщения, когда пользователь нажимает на кнопку 'Розыгрыш билетов'."""
    admin_in = context.user_data.get("admin")
    if admin_in is not None and context.user_data["admin"]:
        if settings.START_GIVEAWAY[0] is False:
            start_button = InlineKeyboardButton(text="начать", callback_data=f"giveaway_admin_start_0")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[start_button]])
        else:
            stop_button = InlineKeyboardButton(text="завершить без победителя", callback_data=f"giveaway_admin_stop_0")
            stop_win_button = InlineKeyboardButton(text="завершить с победителим",
                                                   callback_data=f"giveaway_admin_stop_1")
            check_button = InlineKeyboardButton(text="кол-во участников",
                                                   callback_data=f"giveaway_admin_stop_2")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[stop_button, stop_win_button], [check_button]])
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text="вы вошли в розыгрыши",
                                       reply_markup=keyboard)
    if admin_in is None or admin_in is not None and context.user_data["admin"] is False:
        print("test")
        if settings.START_GIVEAWAY[0]:
            start_giveaway_button = InlineKeyboardButton(text="участвовать", callback_data=f"giveaway_user_0_0")
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
            text = "введите текст розыгрыша"
            start_giveaway_button = InlineKeyboardButton(text="назад", callback_data=f"giveaway_back_")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[start_giveaway_button]])
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                reply_markup=keyboard)
            query = update.callback_query
            context.user_data["giveaway_Text_start"] = True
            print("qqqqqqqqqqqqqqqqq")
    elif data[1] == "admin" and data[2] == "stop":
        if data[3] == "0":
            settings.START_GIVEAWAY[0] = False
            text = f"розыгрышь закончен по техническим причинам"
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text
            )
            text_stop = "розыгрышь закончен по техническим причинам"
            for participant in settings.START_GIVEAWAY[4]:
                print(participant)
                text = text_stop
                await context.bot.send_message(chat_id=participant[1], text=text)
            with open(settings.GIVEAWAY_TXT, 'wb') as file:
                pickle.dump(settings.START_GIVEAWAY, file)
        elif data[3] == "1":
            print("answer")
            print(settings.START_GIVEAWAY)
            if len(settings.START_GIVEAWAY[4]) > 0:
                winner = random.choice(settings.START_GIVEAWAY[4])
                settings.START_GIVEAWAY[0] = False
                win = "@" + str(winner[0])
                text = f"розыгрышь закончен\n победитель : {win}"
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=text
                )
                text_winner = f"Розыгрыш закончен. Вы победили, обращатся по поводу победы : @{settings.START_GIVEAWAY[3]}"
                text_loser = "К сожалению, вы не выиграли в розыгрыше."
                for participant in settings.START_GIVEAWAY[4]:
                    print(participant)
                    text = text_winner if participant == winner else text_loser
                    await context.bot.send_message(chat_id=participant[1], text=text)
                with open(settings.GIVEAWAY_TXT, 'wb') as file:
                    pickle.dump(settings.START_GIVEAWAY, file)
            else:
                settings.START_GIVEAWAY[0] = False
                text = f"розыгрышь закончен\n участников не было"
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=text
                )
                with open(settings.GIVEAWAY_TXT, 'wb') as file:
                    pickle.dump(settings.START_GIVEAWAY, file)
        if data[3] == "2":
            text = f"количество участников: {len(settings.START_GIVEAWAY[4])}"
            start_giveaway_button = InlineKeyboardButton(text="назад", callback_data=f"giveaway_back_")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[start_giveaway_button]])
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=text,
                reply_markup=keyboard)
    elif data[1] == "user":
        if data[2] == "0":
            user = update.effective_user
            # Получаем ID пользователя и чата
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            user_status = await context.bot.get_chat_member(chat_id='@' + settings.CHAT, user_id=user_id)
            if user_status.status == 'member' or user_status.status == 'creator' or user_status.status == 'administrator':
                user = update.effective_user
                username = user.username
                if username not in [user_n[0] for user_n in settings.START_GIVEAWAY[4]]:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=query.message.message_id,
                        text='вы присоединились к розыгрышу'
                    )
                    settings.START_GIVEAWAY[4].append([user.username, chat_id])
                    with open(settings.GIVEAWAY_TXT, 'wb') as file:
                        pickle.dump(settings.START_GIVEAWAY, file)
                else:
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=query.message.message_id,
                        text='вы уже учавствуете'
                    )
            else:
                if data[3] == "1":
                    text = f"Извените но вы не подписались, подпишитесь на канал t.me/{settings.CHAT}, чтобы принять участие в розыгрыше."
                    check_button = InlineKeyboardButton(text="Проверить", callback_data=f"giveaway_user_0_2")
                else:
                    text = f"Пожалуйста, подпишитесь на канал t.me/{settings.CHAT}, чтобы принять участие в розыгрыше."
                    check_button = InlineKeyboardButton(text="Проверить", callback_data=f"giveaway_user_0_1")
                community_button = InlineKeyboardButton(text="Подписаться", url=f"t.me/{settings.CHAT}")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[community_button, check_button]])
                if data[3] != "2":
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=query.message.message_id,
                        text=text,
                        reply_markup=keyboard)


    if data[1] == "back":
        admin_in = context.user_data.get("admin")
        if admin_in is not None and context.user_data["admin"]:
            if settings.START_GIVEAWAY[0] is False:
                start_button = InlineKeyboardButton(text="начать", callback_data=f"giveaway_admin_start_0")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[start_button]])
            else:
                stop_button = InlineKeyboardButton(text="завершить без победителя",
                                                   callback_data=f"giveaway_admin_stop_0")
                stop_win_button = InlineKeyboardButton(text="завершить с победителим",
                                                       callback_data=f"giveaway_admin_stop_1")
                check_button = InlineKeyboardButton(text="кол-во участников",
                                                    callback_data=f"giveaway_admin_stop_2")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[stop_button, stop_win_button], [check_button]])
            await context.bot.edit_message_text(
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text="вы вошли в розыгрыши",
                reply_markup=keyboard)
            context.user_data["giveaway_Text_start"] = False
        if admin_in is None or admin_in is not None and context.user_data["admin"] is False:
            if settings.START_GIVEAWAY[0]:
                start_giveaway_button = InlineKeyboardButton(text="участвовать", callback_data=f"giveaway_user_0")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[start_giveaway_button]])
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text=settings.START_GIVEAWAY[1],
                    reply_markup=keyboard)
            else:
                await context.bot.edit_message_text(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="пока нет розыгрышей")

async def giveaway_text(update, context):
    if context.user_data is not None:
        search_query = context.user_data.get("giveaway_Text_start")
        if search_query is not None:
            if context.user_data["giveaway_Text_start"]:
                user = update.effective_user
                # Получение введенного пользователем имени
                text_admin = update.message.text
                text = f"розыгрыш начат \n текст: {text_admin}"
                text1 = f"розыгрыш начат \n {text_admin}"
                await context.bot.send_message(chat_id=update.message.chat_id,
                                               text=text)
                context.user_data["giveaway_Text_start"] = False
                settings.START_GIVEAWAY = [True, text_admin, 1, user.username, []]
                for participant in settings.USERS:
                    await context.bot.send_message(chat_id=participant[1], text=text1)
                with open(settings.GIVEAWAY_TXT, 'wb') as file:
                    pickle.dump(settings.START_GIVEAWAY, file)
