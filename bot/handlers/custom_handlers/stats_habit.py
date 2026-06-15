from typing import Dict, List

from telebot.types import Message, CallbackQuery

from api.authentication import get_token, registration_user
from api.habit_client import add_habit_api, get_habit_api
from api.track_habit_client import track_habit_check_api
from database.models import add_user, get_user_by_telegram_id
from loader import bot
from states.stats_habit import StatsState
from utils.password_validation import password_validator
from utils.user_decorator import with_current_user, get_current_user_from_inline_button
from utils.user_decorator import with_current_user
from bot.database.database import User
from bot.keyboards.inline.stats_habit import stats_habits_keyboard, stats_habits_list_keyboard


@bot.message_handler(commands=["habit_stats"])
@with_current_user
def stats_habit(message: Message, current_user: User):
    bot.set_state(message.from_user.id, StatsState.stats, message.chat.id)
    bot.send_message(
        message.chat.id,
        text="Выберете какую статистику вывести:",
        reply_markup=stats_habits_keyboard()
    )
    # habits: Dict[User | None] = get_habit_api(user=current_user)
    # if habits:
    #     habits_list: List[Dict[str: str] | None] = [{"id": i["id"], "name": i["habit_name"]} for i in habits]
    #     bot.send_message(message.chat.id, "отследить привычку",
    #                      reply_markup=track_habits_keyboard(habit_list=habits_list))
    # else:
    #     bot.send_message(message.chat.id, "У Вас пока ещё нет привычек")
    bot.send_message(message.chat.id, "123")


@bot.callback_query_handler(state=StatsState.stats, func=lambda call: call.data == "stats_habit_all")
@get_current_user_from_inline_button
def stats_habit_all(call: CallbackQuery):
    bot.send_message(call.message.chat.id, "Статистика по всем привычкам", call.message.message_id)
    bot.delete_state(call.from_user.id, call.message.chat.id)


@bot.callback_query_handler(state=StatsState.stats, func=lambda call: call.data == "stats_habit_one")
@get_current_user_from_inline_button
def stats_habit_list(call: CallbackQuery):
    bot.set_state(call.message.chat.id, StatsState.stats_one_habit, call.message.chat.id)
    habit_list = [{"habit": 1}]
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="отследить привычку",
        reply_markup=stats_habits_list_keyboard(habit_statistic=habit_list)
    )


@bot.callback_query_handler(state=StatsState.stats_one_habit,
                            func=lambda call: call.data.startswith("stats_habit_name_"))
@get_current_user_from_inline_button
def stats_habit_name(call: CallbackQuery):
    bot.send_message(call.message.chat.id, "Статистика по привычке", call.message.message_id)
    bot.delete_state(call.message.chat.id, call.message.message_id)


# @bot.callback_query_handler(state=TrackState.track, func=lambda call: call.data == "track_habit")
# @get_current_user_from_inline_button
# def track_habit_confirmation(call: CallbackQuery, current_user: User):
#     bot.set_state(call.from_user.id, TrackState.track, call.message.chat.id)
#     habits: Dict[User | None] = get_habit_api(user=current_user)
#     if habits:
#         habits_list: List[Dict[str: str] | None] = [{"id": i["id"], "name": i["habit_name"]} for i in habits]
#         bot.edit_message_text(chat_id=call.message.chat.id,
#                               message_id=call.message.message_id,
#                               text="отследить привычку",
#                               reply_markup=track_habits_keyboard(habit_list=habits_list))
#     else:
#         bot.send_message(call.message.chat.id, "У Вас пока ещё нет привычек")


"""
Вывести статистику по всем привычкам
выводист список по всем привычкаи


вывести по конкретной привычке
выводит список привычек
после выбора привычки выводится детальная статистика

"""

"""
Вывести все привычки
выход из меню

можно зайти в привычку
подтвердить выполнение
назад
выйти из меню

"""

"""
1)
вывести все привычки
- пользователь выбирает привычку
2) конкретная привычка в inline
название привычки
редактировать | удалить

РЕДАКТИРОВАТЬ
Выберете что редактировать: 
название привычки в inline
название | описание | цель | срок | всё

При выборе любого менё кроме Всё
запрашиваем новые данные и обновляем их

При выборе Всё
по очереди идём по всем данным, далее комплексно обновляем


УДАЛИТЬ:
Запрашиваем подтверждение и удаляем



"""
