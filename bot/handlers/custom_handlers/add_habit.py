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
def add_hobbit(message: Message) -> None:
    """
    Запускаем сценарий добавления новой привычки

    Args:
        message: Сообщение с данными

    Returns:
        None
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id

    bot.set_state(
        user_id=user_id,
        state=HabitState.name,
        chat_id=chat_id,
    )
    bot.send_message(chat_id=chat_id, text="Введите название новой привычки:")


@bot.message_handler(state=HabitState.name)
def process_habit_name(message: Message) -> None:
    """
    Обработчик названия привычки

    Args:
        message: Сообщение с данными

    Returns:
        None
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    habit_name: str = message.text

    if len(habit_name) <= 50:
        bot.send_message(
            chat_id=chat_id,
            text="Введите описание новой привычки:",
        )
        bot.set_state(
            user_id=user_id,
            state=HabitState.description,
            chat_id=chat_id,
        )

        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data["name"] = habit_name
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Название может содержать не более 50 символов.",
        )


@bot.message_handler(state=HabitState.description)
def process_habit_description(message: Message) -> None:
    """
    Обработчик описания привычки

    Args:
        message: Сообщение с данными

    Returns:
        None
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    hobbit_description = message.text

    if len(hobbit_description) <= 250:
        bot.send_message(
            chat_id=chat_id,
            text="Введите цель новой привычки:",
        )
        bot.set_state(
            user_id=user_id,
            state=HabitState.goal,
            chat_id=chat_id,
        )

        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data["description"] = message.text
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Описание может содержать не более 250 символов.",
        )


@bot.message_handler(state=HabitState.goal)
def process_habit_goal(message: Message) -> None:
    """
    Обработчик цели привычки

    Args:
        message: Сообщение с данными

    Returns:
        None
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    habit_goal: str = message.text

    if len(habit_goal) <= 50:
        current_min_date: date = date.today() + timedelta(days=21)
        max_date: date = date.today() + timedelta(days=21 * 3)
        calendar, step = WMonthTelegramCalendar(
            locale="ru",
            current_date=current_min_date,
            min_date=current_min_date,
            max_date=max_date,
        ).build()

        bot.send_message(
            chat_id=chat_id,
            text=f"Выберете дату выполнения новой привычки:",
            reply_markup=calendar,
        )
        bot.set_state(
            user_id=user_id,
            state=HabitState.terms,
            chat_id=chat_id,
        )

        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data["goal"] = message.text
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Цель может содержать не более 50 символов.",
        )


@bot.callback_query_handler(state=HabitState.terms, func=WMonthTelegramCalendar.func())
@get_current_user_from_inline_button
def cal(call: CallbackQuery, current_user: User) -> None:
    """
    Обработчик inline календаря, так же после выбора даты делает запрос к API

    Args:
        call: Данные с кнопки inline
        current_user: текущий пользователь полученные из БД

    Returns:
        None
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id

    current_min_date: date = date.today() + timedelta(days=21)
    max_date: date = date.today() + timedelta(days=21 * 3)
    result, key, step = WMonthTelegramCalendar(
        locale="ru",
        current_date=current_min_date,
        min_date=current_min_date,
        max_date=max_date,
    ).process(call.data)

    if not result and key:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Выберете дату:",
            reply_markup=key,
        )
    elif result:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=f"Вы выбрали {result}",
        )

        with bot.retrieve_data(call.from_user.id) as data:
            data["terms"] = result

        result: bool = add_habit_api(user=current_user, habit_data=data)
        if result:
            bot.send_message(
                chat_id=chat_id,
                text="Новая привычка успешно добавлена!",
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text="Не удалось добавить привычку.",
            )

        bot.delete_state(
            user_id=user_id,
            chat_id=chat_id,
        )


@bot.message_handler(state=HabitState.terms)
def process_habit_terms(message: Message):
    """
    Когда активен календарь, выводит сообщение пользователю

    Args:
        message: Сообщение с данными

    Returns:
        None
    """

    bot.send_message(
        chat_id=message.chat.id,
        text="Ошибка: Необходимо выбрать дату в меню выше.",
    )
