from datetime import date, timedelta
from typing import List, Dict, Tuple

from telegram_bot_calendar import WMonthTelegramCalendar

from telebot.types import Message, CallbackQuery
from api.habit_client import get_habit_api, remove_habit_api_all, edit_habit_api, edit_habit_api_all, remove_habit_api
from loader import bot
from states.edit_habit import EditState
from utils.password_validation import password_validator
from utils.user_decorator import with_current_user, get_current_user_from_inline_button
from bot.database.database import User
from bot.keyboards.inline.edit_habit import edit_habits_keyboard, edit_hobit_id_keyboard, edit_hobit_id_choice_keyboard


@bot.message_handler(commands=["edit_habit"])
@with_current_user
def edit_habit(message: Message, current_user: User) -> None:
    """
    Запускаем сценарий редактирования привычек

    :param message: Сообщение с командой /edit_habit
    :type message: Message
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

    habits: Dict[User | None] = get_habit_api(user=current_user)

    if habits:
        bot.set_state(message.from_user.id, EditState.edit, message.chat.id)
        habits_list: List[Dict[str: str] | None] = [{"id": i["id"], "name": i["habit_name"]} for i in habits]
        bot.send_message(message.chat.id, f"Выберете привычку для редактирования:",
                         reply_markup=edit_habits_keyboard(habits_list=habits_list))
    else:
        bot.send_message(message.chat.id, "У Вас пока ещё нет привычек")


@bot.message_handler(state=EditState.name)
def process_edit_name(message: Message) -> None:
    """
    Сохраняет название привычки (редактируем всю привычку)

    :param message: Сообщение с командой /edit_habit
    :type message: Message
    :return: None
    :rtype: None
    """

    bot.send_message(message.from_user.id, "Введите новое описание привычки:")
    bot.set_state(message.from_user.id, EditState.description, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["name"]: str = message.text


@bot.message_handler(state=EditState.description)
def process_edit_description(message: Message) -> None:
    """
    Сохраняет описание привычки (редактируем всю привычку)

    :param message: Сообщение с командой /edit_habit
    :type message: Message
    :return: None
    :rtype: None
    """

    bot.send_message(message.from_user.id, "Введите новую цель привычки:")
    bot.set_state(message.from_user.id, EditState.goal, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["description"]: str = message.text


@bot.message_handler(state=EditState.goal)
def process_edit_goal(message: Message) -> None:
    """
    Сохраняет цель привычки (редактируем всю привычку)

    :param message: Сообщение с командой /edit_habit
    :type message: Message
    :return: None
    :rtype: None
    """

    bot.set_state(message.from_user.id, EditState.term_only, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["goal"]: str = message.text

    current_min_date: date = date.today() + timedelta(days=21)
    calendar, step = WMonthTelegramCalendar(
        locale="ru",
        current_date=current_min_date,
        min_date=current_min_date,
        max_date=date.today() + timedelta(days=21 * 3),
    ).build()

    bot.send_message(message.from_user.id, "Введите новые сроки выполнения привычки:", reply_markup=calendar)


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data.startswith("habit_id_"))
def edit_hobit(call: CallbackQuery) -> None:
    """
    Выбор действия редактировать или удалить

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :return: None
    :rtype: None
    """

    habit_id: int = int(call.data.split("_")[2])
    habit_name: str = call.data.split("_")[3]

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"{habit_name}",
        reply_markup=edit_hobit_id_keyboard(habit_id=habit_id)
    )


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data.startswith("habit_edit_id_"))
def edit_hobit_id_choice_action(call: CallbackQuery) -> None:
    """
    Выбор того, что именно редактировать в привычке или всё

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :return: None
    :rtype: None
    """

    habit_id: int = int(call.data.split("_")[3])

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберете, что редактировать:",
        reply_markup=edit_hobit_id_choice_keyboard(habit_id=habit_id)
    )


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data.startswith("habit_choice_id_"))
def edit_hobit_id_choice_action_all(call: CallbackQuery) -> None:
    """
    Обработка выбранного действия

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :return: None
    :rtype: None
    """

    habit_action: str = call.data.split("_")[3]
    habit_id: int = int(call.data.split("_")[4])
    message_text: str = ""
    calendar: WMonthTelegramCalendar | None = None

    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data["habit_id"]: int = habit_id
        data["type"]: str = "only"

        match habit_action:
            case "name":
                bot.set_state(call.from_user.id, EditState.name_desc_goal_only, call.message.chat.id)
                message_text: str = "Введите новое название привычки:"
                data["param"]: str = "habit_name"
            case "description":
                bot.set_state(call.from_user.id, EditState.name_desc_goal_only, call.message.chat.id)
                message_text: str = "Введите новое описание привычки:"
                data["param"]: str = "description"
            case "goal":
                bot.set_state(call.from_user.id, EditState.name_desc_goal_only, call.message.chat.id)
                message_text: str = "Введите новую цель привычки:"
                data["param"]: str = "goal"
            case "terms":
                bot.set_state(call.from_user.id, EditState.term_only, call.message.chat.id)
                message_text: str = "Введите новую дату привычки:"
                data["param"]: str = "terms_date"
                current_min_date: date = date.today() + timedelta(days=21)
                calendar: WMonthTelegramCalendar
                step: str
                calendar, step = WMonthTelegramCalendar(
                    locale="ru",
                    current_date=current_min_date,
                    min_date=current_min_date,
                    max_date=date.today() + timedelta(days=21 * 3),
                ).build()
            case "all":  # тут нужен свой статус для редактирования всего
                bot.set_state(call.from_user.id, EditState.name, call.message.chat.id)
                message_text: str = "Введите новое название привычки:"
                data["type"]: str = "all"
            case _:
                pass

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=message_text,
        reply_markup=calendar
    )


@bot.message_handler(state=EditState.name_desc_goal_only)
@with_current_user
def edit_habit_name(message: Message, current_user: User) -> None:
    """
    Обновляем один выбранный параметр привычки

    :param message: Сообщение с командой /edit_habit
    :type message: Message
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

    value: str = message.text
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        param: str = data.get("param")
        habit_id: int = data.get("habit_id")

    result: bool | None = edit_habit_api(user=current_user, habit_id=habit_id, param=param, value=value)

    if result:
        bot.send_message(message.from_user.id, "Привычка успешно изменена!")
    else:
        bot.send_message(message.from_user.id, "Не удалось обновить привычку.")

    bot.delete_state(message.from_user.id, message.chat.id)


@bot.callback_query_handler(state=EditState.term_only, func=WMonthTelegramCalendar.func())
@get_current_user_from_inline_button
def cal(call: CallbackQuery, current_user: User) -> None:
    """
    Обработчик inline календаря, так же после выбора даты делает запрос к API.

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

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
            data["terms"]: date = result.strftime("%Y-%m-%d")
            habit_id: int = data.get("habit_id")
            param: str = data.get("param")
            value: str = data.get("terms")
            if data.get("type") == "only":
                result: bool | None = edit_habit_api(user=current_user, habit_id=habit_id, param=param, value=value)
            elif data.get("type") == "all":
                result: bool | None = edit_habit_api_all(user=current_user, habit_id=habit_id, habit_data=data)

        if result:
            bot.send_message(call.from_user.id, "Привычка успешно обновлена.")
        else:
            bot.send_message(call.from_user.id, "Не удалось обновить привычку.")

        bot.delete_state(call.from_user.id, call.message.chat.id)


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data.startswith("habit_remove_id_"))
@get_current_user_from_inline_button
def delete_habits_id(call: CallbackQuery, current_user: User) -> None:
    """
    Удаление привычки пользователя по id

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

    habit_id = int(call.data.split("_")[3])
    result: bool | None = remove_habit_api(user=current_user, habit_id=habit_id)

    text: str = "Привычка успешно удалена!"
    if not result:
        text: str = "Не удалось удалить привычку"

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=None
    )

    bot.delete_state(call.from_user.id, call.message.chat.id)


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data == "delete_all_habit")
@get_current_user_from_inline_button
def delete_all_habits(call: CallbackQuery, current_user: User) -> None:
    """
    Удаление всех привычек пользователя

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :param current_user: Данные пользователя из БД
    :type current_user: User
    :return: None
    :rtype: None
    """

    result: bool | None = remove_habit_api_all(user=current_user)
    text: str = "Все привычки успешно удалены!"
    if not result:
        text: str = "Не удалось удалить все привычки"
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=None
    )
    bot.delete_state(call.from_user.id, call.message.chat.id)


@bot.callback_query_handler(state=EditState.edit, func=lambda call: call.data == "clear_menu")
def clear_menu(call: CallbackQuery) -> None:
    """
    Очистка меню - полностью убирает inline клавиатуру

    :param call: CallbackQuery с данными
    :type call: CallbackQuery
    :return: None
    :rtype: None
    """

    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=None
    )
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "Клавиатура убрана!")
    bot.delete_state(call.from_user.id, call.message.chat.id)
