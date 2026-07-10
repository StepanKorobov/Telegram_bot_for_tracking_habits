from api.track_habit_client import track_habit_get_all_api, track_habit_set_alert_time
from loader import bot
from states.set_reminder import ReminderState
from telebot.types import CallbackQuery, Message
from utils.user_decorator import get_current_user_from_inline_button, with_current_user

from bot.database.database import User
from bot.keyboards.inline.set_reminder import (
    set_reminder_hour_keyboard,
    set_reminder_keyboard,
    set_reminder_minute_keyboard,
)


@bot.message_handler(commands=["set_reminder"])
@with_current_user
def set_reminder_habit(message: Message, current_user: User) -> None:
    """
    Запускаем сценарий установки напоминания выполнения привычек.
    Выводит меню с выбором привычек.

    Args:
        message: Сообщение с данными.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id

    bot.set_state(
        user_id=user_id,
        state=ReminderState.reminder,
        chat_id=chat_id,
    )
    result = track_habit_get_all_api(user=current_user)
    bot.send_message(
        chat_id=chat_id,
        text="Установить напоминание о привычках:",
        reply_markup=set_reminder_keyboard(habits=result),
    )


@bot.callback_query_handler(
    state=ReminderState.reminder,
    func=lambda call: call.data.startswith("habit_reminder_id_"),
)
def set_reminder_change_habit(call: CallbackQuery) -> None:
    """
    Обработчик выбора привычки для установки напоминания.
    Выводит клавиатуру с выбором часа напоминания.

    Args:
        call: Данные с кнопки inline.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    habit_id = int(call.data.split("_")[3])

    bot.set_state(
        user_id=user_id,
        state=ReminderState.hour_change,
        chat_id=chat_id,
    )

    with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
        data["habit_id"] = habit_id

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Выберете час для уведомления:",
        reply_markup=set_reminder_hour_keyboard(),
    )


@bot.callback_query_handler(
    state=ReminderState.hour_change,
    func=lambda call: call.data.startswith("habit_reminder_hour_"),
)
def set_reminder_change_hour(call: CallbackQuery) -> None:
    """
    Обработчик выбора часа для установки напоминания.
    Выводит клавиатуру с выбором минут напоминания.

    Args:
        call: Данные с кнопки inline.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    hour: int = int(call.data.split("_")[3])

    bot.set_state(
        user_id=user_id,
        state=ReminderState.minute_change,
        chat_id=chat_id,
    )

    with bot.retrieve_data(user_id=user_id) as data:
        data["hour"] = hour

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Выберете минуту для уведомления, либо введите в чат:",
        reply_markup=set_reminder_minute_keyboard(),
    )


@bot.callback_query_handler(
    state=ReminderState.minute_change,
    func=lambda call: call.data.startswith("habit_reminder_minute_"),
)
@get_current_user_from_inline_button
def set_reminder_change_minute(call: CallbackQuery, current_user: User) -> None:
    """
    Обработчик выбора минут для установки напоминания.
    Делает запрос к API для установки времени напоминания о выполнении привычки.

    Args:
        call: Данные с кнопки inline.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    minute = int(call.data.split("_")[3])

    with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
        data["minute"] = minute
        hour = data.get("hour") if data.get("hour") > 9 else f"0{data.get("hour")}"
        minute = (
            data.get("minute") if data.get("minute") > 9 else f"0{data.get("minute")}"
        )

    result = track_habit_set_alert_time(
        user=current_user, habit_id=data["habit_id"], hour=hour, minute=minute
    )

    if result:
        text = f"Для привычки установлено время напоминания {hour}:{minute}"
    else:
        text = "Не удалось установить время напоминания"

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=None,
    )

    bot.delete_state(
        user_id=user_id,
        chat_id=chat_id,
    )


@bot.message_handler(state=ReminderState.minute_change)
@get_current_user_from_inline_button
def set_reminder_change_minute(message: Message, current_user: User) -> None:
    """
    Обработчик выбора минут для установки напоминания.
    Делает запрос к API для установки времени напоминания о выполнении привычки.

    Args:
        message: Сообщение с данными.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    minute: str | int = message.text

    if minute.isdigit():
        minute = int(minute)
        if 0 <= minute < 50:
            with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
                data["minute"] = minute
                hour = data.get("hour") if data.get("hour") > 9 else f"0{data.get("hour")}"
                minute = (
                    data.get("minute") if data.get("minute") > 9 else f"0{data.get("minute")}"
                )

            result = track_habit_set_alert_time(
                user=current_user, habit_id=data["habit_id"], hour=hour, minute=minute
            )

            if result:
                text = f"Для привычки установлено время напоминания {hour}:{minute}"
            else:
                text = "Не удалось установить время напоминания"

            bot.send_message(
                chat_id=chat_id,
                text=text,
            )

            bot.delete_state(
                user_id=user_id,
                chat_id=chat_id,
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text="Ошибка: необходимо ввести минуты в диапазоне от 0 до 59."
            )
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Ошибка: Ожидалось число, без символов."
        )
