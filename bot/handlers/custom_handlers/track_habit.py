import logging

from api.habit_client import add_habit_api, get_habit_api
from api.track_habit_client import track_habit_check_api
from bot.database.database import User
from bot.keyboards.inline.track_habit import (
    track_habits_confirmation_keyboard,
    track_habits_keyboard,
)
from loader import bot
from states.track_habit import TrackState
from telebot.types import CallbackQuery, Message
from utils.user_decorator import get_current_user_from_inline_button, with_current_user

logger = logging.getLogger(__name__)


@bot.message_handler(commands=["track_habit"])
@with_current_user
def track_habit(message: Message, current_user: User) -> None:
    """
    Запускаем сценарий отслеживания привычки (установка отметки о выполнении).
    Выводит список привычек для выбора.

    Args:
        message: Сообщение с данными.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id

    logger.info(
        "command /track_habit, user_id=%s, chat_id=%s",
        user_id,
        chat_id,
    )

    habits: list[dict | None] = get_habit_api(user=current_user)
    logger.debug(
        "track_habit habit list, user_id=%s, habits_count=%s",
        user_id,
        len(habits) if habits else 0,
    )

    if habits:
        bot.set_state(
            user_id=user_id,
            state=TrackState.track,
            chat_id=chat_id,
        )
        habits_list: list[dict[str, str | int] | None] = [
            {"id": i["id"], "name": i["habit_name"]} for i in habits
        ]
        bot.send_message(
            chat_id=chat_id,
            text="отследить привычку",
            reply_markup=track_habits_keyboard(habit_list=habits_list),
        )
        logger.info(
            "track_habit list shown, user_id=%s, chat_id=%s, habits_count=%s",
            user_id,
            chat_id,
            len(habits_list),
        )
    else:
        logger.info(
            "track_habit no habits, user_id=%s, chat_id=%s",
            user_id,
            chat_id,
        )
        bot.send_message(
            chat_id=chat_id,
            text="У Вас пока ещё нет привычек",
        )


@bot.callback_query_handler(
    state=TrackState.track, func=lambda call: call.data == "track_habit"
)
@get_current_user_from_inline_button
def track_habit_confirmation(call: CallbackQuery, current_user: User) -> None:
    """
    Запускаем сценарий отслеживания привычки (установка отметки о выполнении).
    Выводит список привычек для выбора.

    Args:
        call: Данные с кнопки inline.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id

    logger.info(
        "track_habit list requested again, user_id=%s, chat_id=%s",
        user_id,
        chat_id,
    )

    habits: list[dict | None] = get_habit_api(user=current_user)
    logger.debug(
        "track_habit habit list reload, user_id=%s, habits_count=%s",
        user_id,
        len(habits) if habits else 0,
    )

    if habits:
        bot.set_state(
            user_id=user_id,
            state=TrackState.track,
            chat_id=chat_id,
        )
        habits_list: list[dict[str, str | int] | None] = [
            {"id": i["id"], "name": i["habit_name"]} for i in habits
        ]
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="отследить привычку",
            reply_markup=track_habits_keyboard(habit_list=habits_list),
        )
        logger.info(
            "track_habit list re-shown, user_id=%s, chat_id=%s, habits_count=%s",
            user_id,
            chat_id,
            len(habits),
        )
    else:
        logger.info(
            "track_habit no habits (on re-request), user_id=%s, chat_id=%s",
            user_id,
            chat_id,
        )
        bot.send_message(
            chat_id=chat_id,
            text="У Вас пока ещё нет привычек",
        )


@bot.callback_query_handler(
    state=TrackState.track, func=lambda call: call.data.startswith("track_habit_id_")
)
def track_habit_confirmation(call: CallbackQuery):
    """
    Обработчик выбора действия (запрос подтверждения отметки о выполнении привычки).

    Args:
        call: Данные с кнопки inline.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    habit_id: int = int(call.data.split("_")[3])

    logger.info(
        "track_habit habit selected, user_id=%s, chat_id=%s, habit_id=%s",
        user_id,
        chat_id,
        habit_id,
    )
    logger.debug(
        "track_habit habit callback data=%r, user_id=%s",
        call.data,
        user_id,
    )

    bot.set_state(
        user_id=user_id,
        state=TrackState.track,
        chat_id=chat_id,
    )
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Подтвердите выполнение привычки:",
        reply_markup=track_habits_confirmation_keyboard(habit_id=habit_id),
    )


@bot.callback_query_handler(
    state=TrackState.track,
    func=lambda call: call.data.startswith("track_habit_accepted_id_"),
)
@get_current_user_from_inline_button
def track_habit_confirmation(call: CallbackQuery, current_user: User):
    """
    Обработчик подтверждения выбранной привычки.
    Обновляет выполнение выбранной привычки в API.

    Args:
        call: Данные с кнопки inline.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    habit_id: int = int(call.data.split("_")[4])

    logger.info(
        "track_habit completion confirmed, user_id=%s, chat_id=%s, habit_id=%s",
        user_id,
        chat_id,
        habit_id,
    )

    try:
        result: bool = track_habit_check_api(user=current_user, habit_id=habit_id)
        logger.debug(
            "track_habit_check_api result, user_id=%s, habit_id=%s, result=%s",
            user_id,
            habit_id,
            result,
        )
    except Exception as exc:
        logger.exception(
            "track_habit_check_api error, user_id=%s, habit_id=%s, exc=%r",
            user_id,
            habit_id,
            exc,
        )
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="Ошибка: не удалось обновить выполнение привычки.",
            reply_markup=None,
        )

    text: str = (
        "Привычка успешно выполнена"
        if result
        else "Привычка уже была выполнена сегодня"
    )

    if result:
        logger.info(
            "habit marked as done, user_id=%s, habit_id=%s",
            user_id,
            habit_id,
        )
    else:
        logger.info(
            "habit already done today, user_id=%s, habit_id=%s",
            user_id,
            habit_id,
        )

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
