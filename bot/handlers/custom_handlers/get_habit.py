from typing import Dict

from telebot.types import Message

from api.authentication import get_token, registration_user
from api.habit_client import get_habit_api
from database.models import add_user, get_user_by_telegram_id
from loader import bot
from states.add_habit import HabitState
from utils.password_validation import password_validator
from utils.user_decorator import with_current_user
from bot.database.database import User


@bot.message_handler(commands=["habit"])
@with_current_user
def get_habit(message: Message, current_user: User):
    habits = get_habit_api(user=current_user)
    if habits:
        bot.send_message(message.from_user.id, f"Ваши привычки:\n{habits}")
    else:
        bot.send_message(message.from_user.id, "У Вас пока ещё нет привычек")
