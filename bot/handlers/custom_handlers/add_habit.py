from datetime import date, timedelta

from api.habit_client import add_habit_api
from bot.database.database import User
from loader import bot
from states.add_habit import HabitState
from telebot.types import CallbackQuery, Message
from telegram_bot_calendar import WMonthTelegramCalendar
from utils.user_decorator import (
    check_user_registration,
    get_current_user_from_inline_button,
    with_current_user,
)


@bot.message_handler(commands=["add_habit"])
@check_user_registration
def add_hobbits(message: Message):
    """Запускаем сценарий добавления новой привычки"""

    bot.set_state(message.from_user.id, HabitState.name, message.chat.id)
    bot.send_message(message.from_user.id, "Введите название новой привычки:")


@bot.message_handler(state=HabitState.name)
def process_habit_name(message: Message):
    """Обработчик названия привычки"""

    habit_name = message.text
    if len(habit_name) <= 50:
        bot.send_message(message.from_user.id, "Введите описание новой привычки:")
        bot.set_state(message.from_user.id, HabitState.description, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["name"]: str = habit_name
    else:
        bot.send_message(
            message.from_user.id, "Название может содержать не более 50 символов."
        )


@bot.message_handler(state=HabitState.description)
def process_habit_description(message: Message):
    """Обработчик описания привычки"""

    hobbit_description = message.text
    if len(hobbit_description) <= 250:
        bot.send_message(message.from_user.id, "Введите цель новой привычки:")
        bot.set_state(message.from_user.id, HabitState.goal, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["description"]: str = message.text
    else:
        bot.send_message(
            message.from_user.id, "Описание может содержать не более 250 символов."
        )


@bot.message_handler(state=HabitState.goal)
def process_habit_goal(message: Message):
    """Обработчик цели привычки"""

    habit_goal = message.text
    if len(habit_goal) <= 50:
        current_min_date: date = date.today() + timedelta(days=21)
        calendar, step = WMonthTelegramCalendar(
            locale="ru",
            current_date=current_min_date,
            min_date=current_min_date,
            max_date=date.today() + timedelta(days=21 * 3),
        ).build()

        bot.send_message(
            message.chat.id,
            f"Выберете дату выполнения новой привычки:",
            reply_markup=calendar,
        )
        bot.set_state(message.from_user.id, HabitState.terms, message.chat.id)

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["goal"]: str = message.text
    else:
        bot.send_message(
            message.from_user.id, "Цель может содержать не более 50 символов."
        )


@bot.callback_query_handler(state=HabitState.terms, func=WMonthTelegramCalendar.func())
@get_current_user_from_inline_button
def cal(call: CallbackQuery, current_user: User):
    """Обработчик inline календаря, так же после выбора даты делает запрос к API"""

    current_min_date: date = date.today() + timedelta(days=21)
    result, key, step = WMonthTelegramCalendar(
        locale="ru",
        current_date=current_min_date,
        min_date=current_min_date,
        max_date=date.today() + timedelta(days=21 * 3),
    ).process(call.data)

    if not result and key:
        bot.edit_message_text(
            f"Выберете дату:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=key,
        )
    elif result:
        bot.edit_message_text(
            f"Вы выбрали {result}", call.message.chat.id, call.message.message_id
        )

        with bot.retrieve_data(call.from_user.id) as data:
            data["terms"]: date = result

        result: bool = add_habit_api(user=current_user, habit_data=data)
        if result:
            bot.send_message(call.from_user.id, "Новая привычка успешно добавлена!")
        else:
            bot.send_message(call.from_user.id, "Не удалось добавить привычку.")

        bot.delete_state(call.from_user.id, call.message.chat.id)


@bot.message_handler(state=HabitState.terms)
def process_habit_terms(message: Message):
    """Когда активен календарь, выводит сообщение пользователю"""

    bot.send_message(
        message.from_user.id, "Ошибка: Необходимо выбрать дату в меню выше."
    )
