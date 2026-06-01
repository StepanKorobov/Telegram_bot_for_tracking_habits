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


@bot.message_handler(commands=["habit_stats"])
@with_current_user
def habit_stats(message: Message, current_user: User):
    bot.set_state(message.from_user.id, TrackState.track, message.chat.id)
    habits: Dict[User | None] = get_habit_api(user=current_user)
    if habits:
        habits_list: List[Dict[str: str] | None] = [{"id": i["id"], "name": i["habit_name"]} for i in habits]
        bot.send_message(message.chat.id, "отследить привычку",
                         reply_markup=track_habits_keyboard(habit_list=habits_list))
    else:
        bot.send_message(message.chat.id, "У Вас пока ещё нет привычек")