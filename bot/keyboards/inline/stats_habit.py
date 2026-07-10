from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def stats_habits_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора какую статистику вывести.

    Args:
        None.

    Returns:
        Клавиатура с привычками.
    """

    kb = InlineKeyboardMarkup()

    kb.row(
        InlineKeyboardButton(
            text="Вывести статистику по отдельной привычке",
            callback_data=f"stats_habit_one",
        ),
    )
    kb.row(
        InlineKeyboardButton(
            text="Вывести статистику по всем привычкам",
            callback_data=f"stats_habit_all",
        ),
    )
    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    return kb


def stats_habits_list_keyboard(habit_statistic: list[dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора привычки (для вывода статистики).

    Args:
        habit_statistic: Список привычек.

    Returns:
        Клавиатура с привычками.
    """

    kb = InlineKeyboardMarkup()
    for i_habit in habit_statistic:
        kb.row(
            InlineKeyboardButton(
                text=f"{i_habit["habit_name"]}",
                callback_data=f"stats_habit_id_{i_habit["id"]}",
            ),
        )

    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    return kb
