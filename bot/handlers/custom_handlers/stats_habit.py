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

    habits: list[dict] | None = track_habit_get_stats_all(user=current_user)

    if habits:
        bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
        img_buffer: BytesIO = get_graphs_habits(data=habits)
        bot.send_photo(
            chat_id=chat_id,
            photo=img_buffer,
            caption="Время выполнения ваших привычек по датам 📊",
        )

        img_buffer.close()
    else:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=chat_id,
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

    bot.set_state(
        user_id=user_id,
        state=StatsState.stats_one_habit,
        chat_id=chat_id,
    )
    habit_list: list[dict] = get_habit_api(user=current_user)
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
    habits: list[dict] = track_habit_get_stats(
        user=current_user, habit_id=int(call.data.split("_")[3])
    )
    habits: list[dict] = habits

    if habits:
        bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
        img_buffer: BytesIO = get_graphs_habits(data=habits)
        bot.send_photo(
            chat_id=chat_id,
            photo=img_buffer,
            caption="Время выполнения ваших привычек по датам 📊",
        )

        img_buffer.close()
    else:
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
