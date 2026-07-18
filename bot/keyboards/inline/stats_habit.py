import logging

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


def stats_habits_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора какую статистику вывести.

    Args:
        None.

    Returns:
        Клавиатура с привычками.
    """

    logger.debug("stats_habits_keyboard: building main stats keyboard")

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

    logger.debug(
        "stats_habits_keyboard: buttons created (one, all, clear)",
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

    logger.debug(
        "stats_habits_list_keyboard: building habit list keyboard, habits_count=%s",
        len(habit_statistic),
    )

    kb = InlineKeyboardMarkup()
    for habit in habit_statistic:
        kb.row(
            InlineKeyboardButton(
                text=f"{habit["habit_name"]}",
                callback_data=f"stats_habit_id_{habit["id"]}",
            ),
        )
        logger.debug(
            "stats_habits_list_keyboard: added button habit_id=%s, name=%r",
            habit["id"],
            habit["habit_name"],
        )

    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    logger.debug("stats_habits_list_keyboard: added close button")

    return kb
