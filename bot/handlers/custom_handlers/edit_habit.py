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


@bot.message_handler(commands=["edit_habit"])
@with_current_user
def edit_habit(message: Message, current_user: User):
    habits = get_habit_api(user=current_user)
    if habits:
        bot.set_state(message.from_user.id, EditState.edit, message.chat.id)
        habits_list = [f"ID: {i["id"]}, name: {i["habit_name"]}" for i in habits]
        habits = "\n".join(habits_list)
        bot.send_message(message.chat.id, f"Введите ID привычки для редактирования:\n{habits}")
    else:
        bot.send_message(message.chat.id, "У Вас пока ещё нет привычек")


@bot.message_handler(state=EditState.edit)
def process_edit_habit(message: Message):
    bot.send_message(message.chat.id, "Выберете действие:\nРедактировать\nУдалить")
    bot.set_state(message.from_user.id, EditState.option, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["habit_id"] = message.text


@bot.message_handler(state=EditState.option)
def process_edit_option(message: Message):
    option = message.text
    if option == "Редактировать":
        bot.send_message(message.from_user.id, "Введите новое название привычки:")
        bot.set_state(message.from_user.id, EditState.name, message.chat.id)
    elif option == "Удалить":
        bot.set_state(message.from_user.id, EditState.remove, message.chat.id)


@bot.message_handler(state=EditState.name)
def process_edit_name(message: Message):
    bot.send_message(message.from_user.id, "Введите новое описание привычки:")
    bot.set_state(message.from_user.id, EditState.description, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["name"] = message.text


@bot.message_handler(state=EditState.description)
def process_edit_description(message: Message):
    bot.send_message(message.from_user.id, "Введите новую цель привычки:")
    bot.set_state(message.from_user.id, EditState.goal, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["description"] = message.text


@bot.message_handler(state=EditState.goal)
def process_edit_goal(message: Message):
    bot.send_message(message.from_user.id, "Введите новые сроки выполнения привычки:")
    bot.set_state(message.from_user.id, EditState.terms, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["goal"] = message.text


@bot.message_handler(state=EditState.terms)
def process_edit_terms(message: Message):
    bot.send_message(message.from_user.id, "Сохранил.")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["terms"] = message.text
        print(data)

    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=EditState.remove)
def process_edit_remove(message: Message):
    # Процесс удаления привычки
    bot.send_message("Привычка возможно удалена.")
    bot.delete_state(message.from_user.id, message.chat.id)
