from typing import Dict

from telebot.types import Message

from api.authentication import get_token, registration_user
from api.habit_client import add_habit_api
from database.models import add_user, get_user_by_telegram_id
from loader import bot
from states.add_habit import HabitState
from utils.password_validation import password_validator
from utils.user_decorator import with_current_user
from bot.database.database import User


@bot.message_handler(commands=["add_habit"])
def add_hobbits(message: Message):
    bot.set_state(message.from_user.id, HabitState.name, message.chat.id)
    bot.send_message(message.from_user.id, "Введите название новой привычки:")


@bot.message_handler(state=HabitState.name)
def process_habit_name(message: Message):
    bot.send_message(message.from_user.id, "Введите описание новой привычки:")
    bot.set_state(message.from_user.id, HabitState.description, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["name"] = message.text


@bot.message_handler(state=HabitState.description)
def process_habit_description(message: Message):
    bot.send_message(message.from_user.id, "Введите цель новой привычки:")
    bot.set_state(message.from_user.id, HabitState.goal, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["description"] = message.text


@bot.message_handler(state=HabitState.goal)
def process_habit_goal(message: Message):
    bot.send_message(message.from_user.id, "Введите сроки выполнения новой привычки:")
    bot.set_state(message.from_user.id, HabitState.terms, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["goal"] = message.text


@bot.message_handler(state=HabitState.terms)
@with_current_user
def process_habit_terms(message: Message, current_user: User):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["terms"] = message.text

    result = add_habit_api(user=current_user, habit_data=data)
    if result:
        bot.send_message(message.from_user.id, "Новая привычка успешно добавлена!")
    else:
        bot.send_message(message.from_user.id, "Не удалось добавить привычку.")

    bot.delete_state(message.from_user.id, message.chat.id)
