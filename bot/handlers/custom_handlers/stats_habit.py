from typing import Dict, List
from _io import BytesIO

from telebot.types import Message, CallbackQuery

from api.authentication import get_token, registration_user
from api.habit_client import add_habit_api, get_habit_api
from api.track_habit_client import track_habit_check_api, track_habit_get_stats_all, track_habit_get_stats
from database.models import add_user, get_user_by_telegram_id
from loader import bot
from states.stats_habit import StatsState
from utils.password_validation import password_validator
from utils.user_decorator import with_current_user, get_current_user_from_inline_button
from utils.user_decorator import with_current_user
from utils.misc.graphs import get_graphs_habits
from bot.database.database import User
from bot.keyboards.inline.stats_habit import stats_habits_keyboard, stats_habits_list_keyboard


@bot.message_handler(commands=["habit_stats"])
def stats_habit(message: Message) -> None:
    """
    Запускаем сценарий получения статистики привычек

    :param message: Сообщение с командой /habit_stats
    :type message: Message
    :return: None
    :rtype: None
    """

    bot.set_state(message.from_user.id, StatsState.stats, message.chat.id)
    bot.send_message(
        message.chat.id,
        text="Выберете какую статистику вывести:",
        reply_markup=stats_habits_keyboard()
    )


@bot.callback_query_handler(state=StatsState.stats, func=lambda call: call.data == "stats_habit_all")
@get_current_user_from_inline_button
def stats_habit_all(call: CallbackQuery, current_user: User) -> None:
    """
    Обработчик выбранного действия (вывести график статистики по всем привычкам)

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

    habits: List[Dict] | None = track_habit_get_stats_all(user=current_user)

    if habits:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        img_buffer: BytesIO = get_graphs_habits(data=habits)
        bot.send_photo(call.message.chat.id, img_buffer,
                       caption='Время выполнения ваших привычек по датам 📊')

        img_buffer.close()
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="У Вас пока нет привычек для статистики",
            reply_markup=None
        )

    bot.delete_state(call.from_user.id, call.message.chat.id)


@bot.callback_query_handler(state=StatsState.stats, func=lambda call: call.data == "stats_habit_one")
@get_current_user_from_inline_button
def stats_habit_list(call: CallbackQuery, current_user: User) -> None:
    """
    Обработчик выбранного действия (выводит список привычек для выбора)

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

    bot.set_state(call.message.chat.id, StatsState.stats_one_habit, call.message.chat.id)
    habit_list: List[Dict] = get_habit_api(user=current_user)
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="отследить привычку",
        reply_markup=stats_habits_list_keyboard(habit_statistic=habit_list)
    )


@bot.callback_query_handler(state=StatsState.stats_one_habit,
                            func=lambda call: call.data.startswith("stats_habit_id_"))
@get_current_user_from_inline_button
def stats_habit_name(call: CallbackQuery, current_user: User):
    """
    Обработчик выбранного действия (Выводит статистику по конкретной привычке)

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

    habits: Dict = track_habit_get_stats(user=current_user, habit_id=int(call.data.split("_")[3]))
    habits: List[Dict] = [habits]

    if habits:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        img_buffer: BytesIO = get_graphs_habits(data=habits)
        bot.send_photo(call.message.chat.id, img_buffer,
                       caption='Время выполнения ваших привычек по датам 📊')

        img_buffer.close()
    else:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="У Вас пока нет привычек для статистики",
            reply_markup=None
        )

    bot.delete_state(call.from_user.id, call.message.chat.id)
