from typing import Dict, List

from telebot.types import Message, CallbackQuery

from api.authentication import get_token, registration_user
from api.habit_client import add_habit_api, get_habit_api
from database.models import add_user, get_user_by_telegram_id
from loader import bot
from states.track_habit import TrackState
from utils.password_validation import password_validator
from utils.user_decorator import with_current_user, get_current_user_from_inline_button
from utils.user_decorator import with_current_user
from bot.database.database import User
from bot.keyboards.inline.track_habit import track_habits_keyboard, track_habits_confirmation_keyboard


@bot.message_handler(commands=["track_habit"])
@with_current_user
def track_habit(message: Message, current_user: User):
    bot.set_state(message.from_user.id, TrackState.track, message.chat.id)
    habits: Dict[User | None] = get_habit_api(user=current_user)
    if habits:
        habits_list: List[Dict[str: str] | None] = [{"id": i["id"], "name": i["habit_name"]} for i in habits]
        bot.send_message(message.chat.id, "отследить привычку",
                         reply_markup=track_habits_keyboard(habit_list=habits_list))
    else:
        bot.send_message(message.chat.id, "У Вас пока ещё нет привычек")


@bot.callback_query_handler(state=TrackState.track, func=lambda call: call.data == "track_habit")
@get_current_user_from_inline_button
def track_habit_confirmation(call: CallbackQuery, current_user: User):
    bot.set_state(call.from_user.id, TrackState.track, call.message.chat.id)
    habits: Dict[User | None] = get_habit_api(user=current_user)
    if habits:
        habits_list: List[Dict[str: str] | None] = [{"id": i["id"], "name": i["habit_name"]} for i in habits]
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="отследить привычку",
                              reply_markup=track_habits_keyboard(habit_list=habits_list))
    else:
        bot.send_message(call.message.chat.id, "У Вас пока ещё нет привычек")


@bot.callback_query_handler(state=TrackState.track, func=lambda call: call.data.startswith("track_habit_id_"))
def track_habit_confirmation(call: CallbackQuery):
    bot.set_state(call.from_user.id, TrackState.track, call.message.chat.id)
    habit_id: int = int(call.data.split("_")[3])

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Подтвердите выполнение привычки:",
        reply_markup=track_habits_confirmation_keyboard(habit_id=habit_id)
    )


@bot.callback_query_handler(state=TrackState.track,
                            func=lambda call: call.data.startswith("track_habit_accepted_id_"))
def track_habit_confirmation(call: CallbackQuery):
    habit_id: int = int(call.data.split("_")[4])

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Привычка успешно выполнена",
        reply_markup=None
    )
    bot.delete_state(call.from_user.id, call.message.chat.id)


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
