from typing import Dict

from telebot.types import Message, CallbackQuery
from api.authentication import get_token, registration_user
from api.habit_client import add_habit_api, get_habit_api
from database.models import add_user, get_user_by_telegram_id
from loader import bot
from states.edit_habit import EditState
from utils.password_validation import password_validator
from utils.user_decorator import with_current_user, get_current_user_from_inline_button
from bot.database.database import User
from bot.keyboards.inline.edit_habit import edit_habits_keyboard, edit_hobit_id_keyboard, edit_hobit_id_choice_keyboard


@bot.message_handler(commands=["edit_habit"])
@with_current_user
def edit_habit(message: Message, current_user: User):
    habits = get_habit_api(user=current_user)
    if habits:
        bot.set_state(message.from_user.id, EditState.edit, message.chat.id)
        habits_list = [{"id": i["id"], "name": i["habit_name"]} for i in habits]
        bot.send_message(message.chat.id, f"Выберете привычку для редактирования:",
                         reply_markup=edit_habits_keyboard(habits_list=habits_list))
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


# @bot.message_handler(state=EditState.remove)
# def process_edit_remove(message: Message):
#     # Процесс удаления привычки
#     bot.send_message("Привычка возможно удалена.")
#     bot.delete_state(message.from_user.id, message.chat.id)

@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data.startswith("habit_id_"))
@get_current_user_from_inline_button
def edit_hobit(call: CallbackQuery, current_user: User):
    """Выбор действия редактировать или удалить"""
    habit_id = int(call.data.split("_")[2])
    habit_name = call.data.split("_")[3]
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"{habit_name}",
        reply_markup=edit_hobit_id_keyboard(habit_id=habit_id)
    )


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data.startswith("habit_edit_id_"))
@get_current_user_from_inline_button
def edit_hobit_id_choice_action(call: CallbackQuery, current_user: User):
    """Выбор того, что именно редактировать в привычке или всё"""
    habit_id = int(call.data.split("_")[3])
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберете, что редактировать:",
        reply_markup=edit_hobit_id_choice_keyboard(habit_id=habit_id)
    )


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data.startswith("habit_choice_id_"))
@get_current_user_from_inline_button
def edit_hobit_id_choice_action_all(call: CallbackQuery, current_user: User):
    """Обработка выбранного действия"""
    habit_action = call.data.split("_")[3]
    habit_id = int(call.data.split("_")[4])
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"{habit_id}, {habit_action}",
        reply_markup=None
    )


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data.startswith("habit_remove_id_"))
@get_current_user_from_inline_button
def delete_habits_id(call: CallbackQuery, current_user: User):
    """Удаление привычки пользователя по id"""
    habit_id = int(call.data.split("_")[3])
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Привычка успешно удалена!",
        reply_markup=None
    )


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data == "delete_all_habit")
@get_current_user_from_inline_button
def delete_all_habits(call: CallbackQuery, current_user: User):
    """Удаление всех привычек пользователя"""
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Все привычки успешно удалены!",
        reply_markup=None
    )
    bot.delete_state(call.from_user.id, call.message.chat.id)


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data == "clear_menu")
def clear_menu(call: CallbackQuery):
    """Убрать меню"""
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=None
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "Клавиатура убрана!")
    bot.delete_state(call.from_user.id, call.message.chat.id)
