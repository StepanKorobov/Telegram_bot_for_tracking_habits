from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def edit_habits_keyboard(habits_list: list[dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура редактирования привычек (содержит привычки).

    Args:
        habits_list: Список привычек.

    Returns:
        Клавиатура с привычками.
    """

    kb = InlineKeyboardMarkup()
    for habit_id, habit in enumerate(habits_list):
        kb.row(
            InlineKeyboardButton(
                text=f"{habit_id + 1}) {habit["name"]}",
                callback_data=f"habit_id_{habit["id"]}_{habit["name"]}",
            )
        )
    kb.row(
        InlineKeyboardButton(
            text="Удалить все привычки",
            callback_data="delete_all_habit",
        ),
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    return kb


def edit_hobit_id_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура редактирования привычек (выбор действия).

    Args:
        habit_id: ID выбранной привычки.

    Returns:
        Клавиатура с выбором действия у привычки
    """

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton(
            text="Редактировать",
            callback_data=f"habit_edit_id_{habit_id}",
        ),
        InlineKeyboardButton(
            text="Удалить",
            callback_data=f"habit_remove_id_{habit_id}",
        ),
    )
    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    return kb


def edit_hobit_id_choice_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура редактирования привычек (выбор действия, что именно редактировать).

    Args:
        habit_id: ID выбранной привычки.

    Returns:
        Клавиатура с выбором действия
    """

    kb = InlineKeyboardMarkup()
    kb.row(
        InlineKeyboardButton(
            text="Всё",
            callback_data=f"habit_choice_id_all_{habit_id}",
        ),
    )
    kb.row(
        InlineKeyboardButton(
            text="Название",
            callback_data=f"habit_choice_id_name_{habit_id}",
        ),
        InlineKeyboardButton(
            text="Описание",
            callback_data=f"habit_choice_id_description_{habit_id}",
        ),
    )
    kb.row(
        InlineKeyboardButton(
            text="Цель",
            callback_data=f"habit_choice_id_goal_{habit_id}",
        ),
        InlineKeyboardButton(
            text="Срок",
            callback_data=f"habit_choice_id_terms_{habit_id}",
        ),
    )
    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    return kb
