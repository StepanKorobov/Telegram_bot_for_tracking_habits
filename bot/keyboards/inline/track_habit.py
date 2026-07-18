import logging

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


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

    logger.debug(
        "track_habits_keyboard: building keyboard, habits_count=%s",
        len(habit_list),
    )

    kb = InlineKeyboardMarkup()

    for habit in habit_list:
        kb.row(
            InlineKeyboardButton(
                text=f"{habit["name"]}",
                callback_data=f"track_habit_id_{habit["id"]}",
            ),
        )

        logger.debug(
            "track_habits_keyboard: added button habit_id=%s, name=%r",
            habit["id"],
            habit["name"],
        )

    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    logger.debug("track_habits_keyboard: added close button")

    return kb


def track_habits_confirmation_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура отслеживания привычек (запрос подтверждения выполнения привычки).

    Args:
        habit_id: ID выбранной привычки.

    Returns:
        Клавиатура с подтверждением.
    """

    logger.debug(
        "track_habits_confirmation_keyboard: building keyboard for habit_id=%s",
        habit_id,
    )

    kb = InlineKeyboardMarkup()

    kb.row(
        InlineKeyboardButton(
            text="ПОДТВЕРДИТЬ",
            callback_data=f"track_habit_accepted_id_{habit_id}",
        )
    )
    kb.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data="track_habit",
        ),
    )
    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    logger.debug(
        "track_habits_confirmation_keyboard: buttons created for habit_id=%s "
        "(confirm, back, clear)",
        habit_id,
    )

    return kb
