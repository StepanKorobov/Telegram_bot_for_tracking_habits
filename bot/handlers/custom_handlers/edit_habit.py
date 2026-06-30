from datetime import date, timedelta

from api.habit_client import (
    edit_habit_api,
    edit_habit_api_all,
    get_habit_api,
    remove_habit_api,
    remove_habit_api_all,
)
from bot.database.database import User
from bot.keyboards.inline.edit_habit import (
    edit_habits_keyboard,
    edit_hobit_id_choice_keyboard,
    edit_hobit_id_keyboard,
)
from loader import bot
from states.edit_habit import EditState
from telebot.types import CallbackQuery, Message
from telegram_bot_calendar import WMonthTelegramCalendar
from utils.user_decorator import get_current_user_from_inline_button, with_current_user


@bot.message_handler(commands=["edit_habit"])
@with_current_user
def edit_habit(message: Message, current_user: User) -> None:
    """
    Запускаем сценарий редактирования привычек.
    Выводит меню с выбором привычек.

    Args:
        message: Сообщение с данными.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id

    habits: list[dict[str, str | int]] | None = get_habit_api(user=current_user)

    if habits:
        bot.set_state(
            user_id=user_id,
            state=EditState.edit,
            chat_id=chat_id,
        )
        habits_list: list[dict[str:str] | None] = [
            {"id": i["id"], "name": i["habit_name"]} for i in habits
        ]
        bot.send_message(
            chat_id=chat_id,
            text=f"Выберете привычку для редактирования:",
            reply_markup=edit_habits_keyboard(habits_list=habits_list),
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text="У Вас пока ещё нет привычек",
        )


@bot.callback_query_handler(
    state=EditState.edit, func=lambda call: call.data.startswith("habit_id_")
)
def edit_hobit(call: CallbackQuery) -> None:
    """
    Обработчик вызываемый после выбора привычки.
    Выбор действия редактировать или удалить.

    Args:
        call: Данные с кнопки inline.

    Returns:
        None.
    """

    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    habit_id: int = int(call.data.split("_")[2])
    habit_name: str = call.data.split("_")[3]

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"{habit_name}",
        reply_markup=edit_hobit_id_keyboard(habit_id=habit_id),
    )


@bot.callback_query_handler(
    state=EditState.edit, func=lambda call: call.data.startswith("habit_edit_id_")
)
def edit_hobit_id_choice_action(call: CallbackQuery) -> None:
    """
    Обработчик вызываемый после выбора пункта "редактировать".
    Выбор действия, что именно редактировать (отдельный пункт или всю привычку).

    Args:
        call: Данные с кнопки inline.

    Returns:
        None.
    """

    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    habit_id: int = int(call.data.split("_")[3])

    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Выберете, что редактировать:",
        reply_markup=edit_hobit_id_choice_keyboard(habit_id=habit_id),
    )


@bot.callback_query_handler(
    state=EditState.edit, func=lambda call: call.data.startswith("habit_choice_id_")
)
def edit_hobit_id_choice_action_all(call: CallbackQuery) -> None:
    """
    Обработчик вызываемый после выбора одного из пунктов (что именно редактировать в привычке).
    В зависимости от выбранного пункта выводит сообщение / запрашивает действия

    Args:
        call: Данные с кнопки inline.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.message.chat.id
    message_id: int = call.message.message_id
    habit_action: str = call.data.split("_")[3]
    habit_id: int = int(call.data.split("_")[4])
    message_text: str = ""
    calendar: WMonthTelegramCalendar | None = None

    with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
        data["habit_id"] = habit_id
        data["type"] = "only"

        match habit_action:
            case "name":
                bot.set_state(
                    user_id=user_id,
                    state=EditState.name_desc_goal_only,
                    chat_id=chat_id,
                )
                message_text: str = "Введите новое название привычки:"
                data["param"] = "habit_name"
            case "description":
                bot.set_state(
                    user_id=user_id,
                    state=EditState.name_desc_goal_only,
                    chat_id=chat_id,
                )
                message_text: str = "Введите новое описание привычки:"
                data["param"] = "description"
            case "goal":
                bot.set_state(
                    user_id=user_id,
                    state=EditState.name_desc_goal_only,
                    chat_id=chat_id,
                )
                message_text: str = "Введите новую цель привычки:"
                data["param"] = "goal"
            case "terms":
                bot.set_state(
                    user_id=user_id,
                    state=EditState.term_only,
                    chat_id=chat_id,
                )
                message_text: str = "Введите новую дату привычки:"
                data["param"] = "terms_date"
                current_min_date: date = date.today() + timedelta(days=21)
                max_date: date = date.today() + timedelta(days=21 * 3)

                calendar: WMonthTelegramCalendar
                step: str
                calendar, step = WMonthTelegramCalendar(
                    locale="ru",
                    current_date=current_min_date,
                    min_date=current_min_date,
                    max_date=max_date,
                ).build()
            case "all":
                bot.set_state(
                    user_id=user_id,
                    state=EditState.name,
                    chat_id=chat_id,
                )
                message_text: str = "Введите новое название привычки:"
                data["type"] = "all"
            case _:
                pass

    bot.edit_message_text(
        chat_id=chat_id, message_id=message_id, text=message_text, reply_markup=calendar
    )


@bot.message_handler(state=EditState.name)
def process_edit_name(message: Message) -> None:
    """
    Запускаем сценарий редактирования привычки (после выбора пункта "редактировать всё").
    Обрабатывает название привычки.

    Args:
        message: Сообщение с данными.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    habit_name: str = message.text

    if len(habit_name) <= 50:
        bot.send_message(
            chat_id=chat_id,
            text="Введите новое описание привычки:",
        )
        bot.set_state(
            user_id=user_id,
            state=EditState.description,
            chat_id=chat_id,
        )

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["name"] = message.text
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Название может содержать не более 50 символов.",
        )


@bot.message_handler(state=EditState.description)
def process_edit_description(message: Message) -> None:
    """
    Сценарий редактирования привычки (после выбора пункта "редактировать всё").
    Обрабатывает описание привычки.

    Args:
        message: Сообщение с данными.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    habit_description: str = message.text

    if len(habit_description) <= 250:
        bot.send_message(
            chat_id=chat_id,
            text="Введите новую цель привычки:",
        )
        bot.set_state(
            user_id=user_id,
            state=EditState.goal,
            chat_id=chat_id,
        )

        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data["description"] = message.text
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Описание может содержать не более 250 символов.",
        )


@bot.message_handler(state=EditState.goal)
def process_edit_goal(message: Message) -> None:
    """
    Сценарий редактирования привычки (после выбора пункта "редактировать всё").
    Обрабатывает цель привычки.

    Args:
        message: Сообщение с данными.

    Returns:
        None.
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
            text="Введите новые сроки выполнения привычки:",
            reply_markup=calendar,
        )
        bot.set_state(
            user_id=user_id,
            state=EditState.term_only,
            chat_id=chat_id,
        )
        with bot.retrieve_data(user_id=user_id, chat_id=chat_id) as data:
            data["goal"] = message.text
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Цель может содержать не более 50 символов.",
        )


@bot.message_handler(state=EditState.name_desc_goal_only)
@with_current_user
def edit_habit_name(message: Message, current_user: User) -> None:
    """
    Сценарий редактирования привычки (после выбора пункта "Название/описание/цель").
    Обновляет в API выбранный параметр.

    Args:
        message: Сообщение с данными.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = message.from_user.id
    chat_id: int = message.chat.id
    value: str = message.text
    validate_error: bool = False
    text_error: str = ""

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        param: str = data.get("param")
        habit_id: str = data.get("habit_id")

    if param == "habit_name" and len(value) > 50:
        text_error: str = "Название может содержать не более 50 символов."
        validate_error: bool = True
    elif param == "description" and len(value) > 250:
        text_error: str = "Описание может содержать не более 250 символов."
        validate_error: bool = True
    elif param == "goal" and len(value) > 50:
        text_error: str = "берете дату выполнения новой привычки"
        validate_error: bool = True
    else:
        result: bool | None = edit_habit_api(
            user=current_user, habit_id=habit_id, param=param, value=value
        )

        if result:
            bot.send_message(
                chat_id=chat_id,
                text="Привычка успешно изменена!",
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text="Не удалось обновить привычку.",
            )

        bot.delete_state(
            user_id=user_id,
            chat_id=chat_id,
        )

    if validate_error:
        bot.send_message(
            chat_id=chat_id,
            text=text_error,
        )


@bot.callback_query_handler(
    state=EditState.term_only, func=WMonthTelegramCalendar.func()
)
@get_current_user_from_inline_button
def cal(call: CallbackQuery, current_user: User) -> None:
    """
    Сценарий редактирования привычки (дата выполнения привычки).
    Обрабатывает как одиночный выбор редактирования даты, так и цепочку редактирования всей привычки.
    Обновляет в API выбранный параметр.

    Args:
        call: Данные с кнопки inline.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
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
            data["terms"] = result.strftime("%Y-%m-%d")
            habit_id: int = data.get("habit_id")
            param: str = data.get("param")
            value: str = data.get("terms")

            if data.get("type") == "only":
                result: bool | None = edit_habit_api(
                    user=current_user, habit_id=habit_id, param=param, value=value
                )
            elif data.get("type") == "all":
                result: bool | None = edit_habit_api_all(
                    user=current_user, habit_id=habit_id, habit_data=data
                )

        if result:
            bot.send_message(
                chat_id=chat_id,
                text="Привычка успешно обновлена.",
            )
        else:
            bot.send_message(
                chat_id=chat_id,
                text="Не удалось обновить привычку.",
            )

        bot.delete_state(
            user_id=user_id,
            chat_id=chat_id,
        )


@bot.callback_query_handler(
    state=EditState.edit, func=lambda call: call.data.startswith("habit_remove_id_")
)
@get_current_user_from_inline_button
def delete_habits_id(call: CallbackQuery, current_user: User) -> None:
    """
    Сценарий редактирования привычки (удаление привычки).
    Обрабатывает удаление одной привычки по ID из API.

    Args:
        call: Данные с кнопки inline.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.from_user.id
    message_id: int = call.message.message_id
    habit_id: int = int(call.data.split("_")[3])
    result: bool | None = remove_habit_api(user=current_user, habit_id=habit_id)

    text: str = "Привычка успешно удалена!"
    if not result:
        text: str = "Не удалось удалить привычку"

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


@bot.callback_query_handler(
    state=EditState.edit, func=lambda call: call.data == "delete_all_habit"
)
@get_current_user_from_inline_button
def delete_all_habits(call: CallbackQuery, current_user: User) -> None:
    """
    Сценарий редактирования привычки (удаление всех привычек).
    Обрабатывает удаление всех привычек пользователя из API.

    Args:
        call: Данные с кнопки inline.
        current_user: текущий пользователь полученные из БД.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.from_user.id
    message_id: int = call.message.message_id

    result: bool | None = remove_habit_api_all(user=current_user)

    text: str = "Все привычки успешно удалены!"
    if not result:
        text: str = "Не удалось удалить все привычки"

    bot.edit_message_text(
        chat_id=chat_id, message_id=message_id, text=text, reply_markup=None
    )
    bot.delete_state(
        user_id=user_id,
        message_id=message_id,
    )


@bot.callback_query_handler(
    state=EditState.edit, func=lambda call: call.data == "clear_menu"
)
def clear_menu(call: CallbackQuery) -> None:
    """
    Очистка меню - полностью убирает inline клавиатуру

    Args:
        call: Данные с кнопки inline.

    Returns:
        None.
    """

    user_id: int = call.from_user.id
    chat_id: int = call.from_user.id
    message_id: int = call.message.message_id

    bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=None
    )
    bot.delete_message(
        chat_id=chat_id,
        message_id=message_id,
    )
    bot.answer_callback_query(callback_query_id=call.id, text="Клавиатура убрана!")
    bot.delete_state(
        user_id=user_id,
        chat_id=chat_id,
    )
