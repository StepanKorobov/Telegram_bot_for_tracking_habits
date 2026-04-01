from typing import Dict

from telebot.types import Message

from api.authentication import get_token, registration_user
from api.habit_client import add_habit_api, get_habit_api
from database.models import add_user, get_user_by_telegram_id
from loader import bot
from states.edit_habit import EditState
from utils.password_validation import password_validator
from utils.user_decorator import with_current_user
from bot.database.database import User


@bot.message_handler(commands=["track_habit"])
def track_habit(message: Message):
    bot.send_message(message.chat.id, "отследить привычку")


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
