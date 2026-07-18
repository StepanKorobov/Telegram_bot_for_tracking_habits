import logging

from _io import BytesIO
from api.habit_client import add_habit_api, get_habit_api
from api.track_habit_client import (
    track_habit_check_api,
    track_habit_get_stats,
    track_habit_get_stats_all,
)
from bot.database.database import User
from bot.keyboards.inline.stats_habit import (
    stats_habits_keyboard,
    stats_habits_list_keyboard,
)
from loader import bot
from states.stats_habit import StatsState
from telebot.types import CallbackQuery, Message
from utils.misc.graphs import get_graphs_habits
from utils.user_decorator import get_current_user_from_inline_button, with_current_user

logger = logging.getLogger(__name__)


@bot.message_handler(commands=["habit_stats"])
def stats_habit(message: Message) -> None:
    """
    Запускаем сценарий получения статистики привычек.
    Выводит меню с выбором статистики (по 1 привычки, либо по всем).

    Args:
        message: Сообщение с данными.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id

    logger.info(
        "command /habit_stats, user_id=%s, chat_id=%s",
        user_id,
        chat_id,
    )

    bot.set_state(user_id=user_id, state=StatsState.stats, chat_id=message.chat.id)
    bot.send_message(
        chat_id=chat_id,
        text="Выберете какую статистику вывести:",
        reply_markup=stats_habits_keyboard(),
    )


@bot.callback_query_handler(
    state=StatsState.stats, func=lambda call: call.data == "stats_habit_all"
)
@get_current_user_from_inline_button
def stats_habit_all(call: CallbackQuery, current_user: User) -> None:
    """
    Обработчик выбранного действия (вывести график статистики по всем привычкам).
    Делает запрос к API для получения статистики.

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
        "stats_habit_all selected, user_id=%s, chat_id=%s",
        user_id,
        chat_id,
    )

    habits: list[dict] | None = track_habit_get_stats_all(user=current_user)
    logger.debug(
        "stats_habit_all API result, user_id=%s, habits_count=%s",
        user_id,
        len(habits) if habits else 0,
    )

    if habits:
        try:
            bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
            img_buffer: BytesIO = get_graphs_habits(data=habits)
            logger.debug(
                "graph generated for all habits, user_id=%s, data_points=%s",
                user_id,
                len(habits),
            )

            bot.send_photo(
                chat_id=chat_id,
                photo=img_buffer,
                caption="Время выполнения ваших привычек по датам 📊",
            )
            logger.info(
                "stats graph sent for all habits, user_id=%s, chat_id=%s",
                user_id,
                chat_id,
            )

            img_buffer.close()
        except Exception as exc:
            logger.exception(
                "error while generating/sending stats graph for all habits, user_id=%s",
                user_id,
            )
            bot.send_message(
                chat_id=chat_id,
                text="Произошла ошибка при построении статистики.",
            )
    else:
        logger.info(
            "no habits for stats (all), user_id=%s, chat_id=%s",
            user_id,
            chat_id,
        )
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="У Вас пока нет привычек для статистики",
            reply_markup=None,
        )

    bot.delete_state(
        user_id=user_id,
        chat_id=chat_id,
    )


@bot.callback_query_handler(
    state=StatsState.stats, func=lambda call: call.data == "stats_habit_one"
)
@get_current_user_from_inline_button
def stats_habit_list(call: CallbackQuery, current_user: User) -> None:
    """
    Обработчик выбранного действия (выводит список привычек для выбора)
    Делает запрос к API для получения списка привычек.

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
        "stats_habit_one selected, user_id=%s, chat_id=%s",
        user_id,
        chat_id,
    )

    bot.set_state(
        user_id=user_id,
        state=StatsState.stats_one_habit,
        chat_id=chat_id,
    )
    habit_list: list[dict] = get_habit_api(user=current_user)
    logger.debug(
        "habit list loaded for stats_one, user_id=%s, habits_count=%s",
        user_id,
        len(habit_list),
    )

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="отследить привычку",
        reply_markup=stats_habits_list_keyboard(habit_statistic=habit_list),
    )


@bot.callback_query_handler(
    state=StatsState.stats_one_habit,
    func=lambda call: call.data.startswith("stats_habit_id_"),
)
@get_current_user_from_inline_button
def stats_habit_name(call: CallbackQuery, current_user: User):
    """
    Обработчик выбранного действия (Выводит статистику по конкретной привычке)
    Делает запрос к API для получения статистики по ID привычки.

    Args:
        call: Данные с кнопки inline.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    habit_id: int = int(call.data.split("_")[3])

    logger.info(
        "stats_habit_id selected, user_id=%s, chat_id=%s, habit_id=%s",
        user_id,
        chat_id,
        habit_id,
    )
    logger.debug(
        "stats_habit_id callback data=%r, user_id=%s",
        call.data,
        user_id,
    )

    habits: list[dict] = track_habit_get_stats(
        user=current_user,
        habit_id=habit_id,
    )
    logger.debug(
        "stats_habit_id API result, user_id=%s, habit_id=%s, data_points=%s",
        user_id,
        habit_id,
        len(habits) if habits else 0,
    )

    if habits:
        try:
            bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
            img_buffer: BytesIO = get_graphs_habits(data=habits)
            logger.debug(
                "graph generated for habit, user_id=%s, habit_id=%s, data_points=%s",
                user_id,
                habit_id,
                len(habits),
            )

            bot.send_photo(
                chat_id=chat_id,
                photo=img_buffer,
                caption="Время выполнения ваших привычек по датам 📊",
            )
            logger.info(
                "stats graph sent for habit, user_id=%s, habit_id=%s",
                user_id,
                habit_id,
            )

            img_buffer.close()
        except Exception as exc:
            logger.exception(
                "error while generating/sending stats graph for habit, user_id=%s, habit_id=%s, exc=%r",
                user_id,
                habit_id,
                exc,
            )
            bot.send_message(
                chat_id=chat_id,
                text="Произошла ошибка при построении статистики.",
            )
    else:
        logger.info(
            "no stats data for habit, user_id=%s, habit_id=%s",
            user_id,
            habit_id,
        )
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text="У Вас пока нет привычек для статистики",
            reply_markup=None,
        )

    bot.delete_state(
        user_id=user_id,
        chat_id=chat_id,
    )
