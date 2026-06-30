from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def track_habits_keyboard(
    habit_list: list[dict[str, str | int]],
) -> InlineKeyboardMarkup:
    """
    Клавиатура отслеживания привычек (содержит привычки).

    Args:
        habit_list: Список привычек.

    Returns:
        Клавиатура с привычками.
    """

    kb = InlineKeyboardMarkup()

    for i_habit in habit_list:
        kb.row(
            InlineKeyboardButton(
                text=f"{i_habit["name"]}",
                callback_data=f"track_habit_id_{i_habit["id"]}",
            )
        )

    kb.row(
        InlineKeyboardButton(text="Закрыть", callback_data=f"clear_menu"),
    )

    return kb


def track_habits_confirmation_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура отслеживания привычек (запрос подтверждения выполнения привычки).

    Args:
        habit_id: ID выбранной привычки.

    Returns:
        Клавиатура с подтверждением.
    """

    kb = InlineKeyboardMarkup()

    kb.row(
        InlineKeyboardButton(
            text="ПОДТВЕРДИТЬ",
            callback_data=f"track_habit_accepted_id_{habit_id}",
        )
    )
    kb.row(
        InlineKeyboardButton(text="Назад", callback_data="track_habit"),
    )
    kb.row(
        InlineKeyboardButton(text="Закрыть", callback_data="clear_menu"),
    )

    return kb
