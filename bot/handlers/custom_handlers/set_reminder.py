from typing import Dict, List
from _io import BytesIO

from telebot.types import Message, CallbackQuery

from api.authentication import get_token, registration_user
from api.habit_client import add_habit_api, get_habit_api
from api.track_habit_client import track_habit_check_api, track_habit_get_stats_all, track_habit_get_stats, \
    track_habit_get_all_api
from database.models import add_user, get_user_by_telegram_id
from loader import bot
from states.stats_habit import StatsState
from states.set_reminder import ReminderState
from utils.password_validation import password_validator
from utils.user_decorator import with_current_user, get_current_user_from_inline_button
from utils.user_decorator import with_current_user
from utils.misc.graphs import get_graphs_habits
from bot.database.database import User
from bot.keyboards.inline.stats_habit import stats_habits_keyboard, stats_habits_list_keyboard
from bot.keyboards.inline.set_reminder import set_reminder_keyboard, set_reminder_hour_keyboard, \
    set_reminder_minute_keyboard


@bot.message_handler(commands=["set_reminder"])
@with_current_user
def stats_habit(message: Message, current_user: User) -> None:
    """
    Запускаем сценарий получения статистики привычек

    :param message: Сообщение с командой /habit_stats
    :type message: Message
    :param current_user: Текущий пользователь
    :type current_user: User
    :return: None
    :rtype: None
    """

    bot.set_state(message.from_user.id, ReminderState.reminder, message.chat.id)
    result = track_habit_get_all_api(user=current_user)
    bot.send_message(
        message.chat.id,
        text="Установить напоминание о привычках:",
        reply_markup=set_reminder_keyboard(habits=result)
    )


@bot.callback_query_handler(state=ReminderState.reminder,
                            func=lambda call: call.data.startswith("habit_reminder_id_"))
@get_current_user_from_inline_button
def stats_habit_all(call: CallbackQuery, current_user: User) -> None:
    """
    Обработчик выбранного действия (вывести график статистики по всем привычкам)

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """
    bot.set_state(call.from_user.id, ReminderState.hour_change, call.message.chat.id)
    habit_id = int(call.data.split("_")[3])

    with bot.retrieve_data(call.from_user.id) as data:
        data["habit_id"] = habit_id

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберете час для уведомления:",
        reply_markup=set_reminder_hour_keyboard()
    )


@bot.callback_query_handler(state=ReminderState.hour_change,
                            func=lambda call: call.data.startswith("habit_reminder_hour_"))
@get_current_user_from_inline_button
def stats_habit_list(call: CallbackQuery, current_user: User) -> None:
    """
    Обработчик выбранного действия (выводит список привычек для выбора)

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

    bot.set_state(call.from_user.id, ReminderState.minute_change, call.message.chat.id)
    hour = int(call.data.split("_")[3])

    with bot.retrieve_data(call.from_user.id) as data:
        data["hour"] = hour

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="отследить привычку",
        reply_markup=set_reminder_minute_keyboard()
    )


@bot.callback_query_handler(state=ReminderState.minute_change,
                            func=lambda call: call.data.startswith("habit_reminder_minute_"))
@get_current_user_from_inline_button
def stats_habit_name(call: CallbackQuery, current_user: User):
    """
    Обработчик выбранного действия (Выводит статистику по конкретной привычке)

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

    minute = int(call.data.split("_")[3])
    with bot.retrieve_data(call.from_user.id) as data:
        data["minute"] = minute
        hour = data.get("hour") if data.get("hour") > 10 else f"0{data.get("hour")}"
        minute = data.get("minute") if data.get("minute") > 10 else f"0{data.get("minute")}"

        text = f"Для привычки установлено время напоминания {hour}:{minute}"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=None
        )

    bot.delete_state(call.from_user.id, call.message.chat.id)


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
