import logging

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)


def set_reminder_keyboard(habits: list[dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура выбора какой привычке установить напоминание.
    Выводит привычки для выбора.

    Args:
        Список привычек.

    Returns:
        Клавиатура с привычками.
    """

    logger.debug(
        "set_reminder_keyboard: building keyboard, habits_count=%s",
        len(habits),
    )

    kb = InlineKeyboardMarkup()

    for habit in habits:
        name: str = habit["habit_name"]
        alert_time: str = habit["habit_tracking"]["alert_time"]
        text: str = (
            f"*{name}* - {alert_time}"
            if alert_time
            else f"*{name}* - Напоминание не установлено"
        )

        kb.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"habit_reminder_id_{habit['id']}",
            ),
        )

        logger.debug(
            "set_reminder_keyboard: added button habit_id=%s, name=%r, alert_time=%r",
            habit["id"],
            name,
            alert_time,
        )

    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    logger.debug("set_reminder_keyboard: added close button")

    return kb


def set_reminder_hour_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора часа для установки напоминания.

    Args:
        None.

    Returns:
        Клавиатура с выбором часа.
    """

    logger.debug("set_reminder_hour_keyboard: building hour keyboard")

    kb = InlineKeyboardMarkup()

    for i_hour in range(0, 24, 4):
        kb.row(
            InlineKeyboardButton(
                text=f"{i_hour}",
                callback_data=f"habit_reminder_hour_{i_hour}",
            ),
            InlineKeyboardButton(
                text=f"{i_hour + 1}",
                callback_data=f"habit_reminder_hour_{i_hour + 1}",
            ),
            InlineKeyboardButton(
                text=f"{i_hour + 2}",
                callback_data=f"habit_reminder_hour_{i_hour + 2}",
            ),
            InlineKeyboardButton(
                text=f"{i_hour + 3}",
                callback_data=f"habit_reminder_hour_{i_hour + 3}",
            ),
        )

        logger.debug(
            "set_reminder_hour_keyboard: added row [%s, %s, %s, %s]",
            i_hour,
            i_hour + 1,
            i_hour + 2,
            i_hour + 3,
        )

    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    logger.debug("set_reminder_hour_keyboard: added close button")

    return kb


def set_reminder_minute_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора минуты для установки напоминания.
    Выводит привычки для выбора

    Args:
        None.

    Returns:
        Клавиатура с выбором минут.
    """

    logger.debug("set_reminder_minute_keyboard: building minute keyboard")

    kb = InlineKeyboardMarkup()

    for i_minute in range(0, 60, 15):
        kb.row(
            InlineKeyboardButton(
                text=f"{i_minute}",
                callback_data=f"habit_reminder_minute_{i_minute}",
            ),
            InlineKeyboardButton(
                text=f"{i_minute + 5}",
                callback_data=f"habit_reminder_minute_{i_minute + 5}",
            ),
            InlineKeyboardButton(
                text=f"{i_minute + 10}",
                callback_data=f"habit_reminder_minute_{i_minute + 10}",
            ),
        )

        logger.debug(
            "set_reminder_minute_keyboard: added row [%s, %s, %s]",
            i_minute,
            i_minute + 5,
            i_minute + 10,
        )

    kb.row(
        InlineKeyboardButton(
            text="Закрыть",
            callback_data="clear_keyboard",
        ),
    )

    logger.debug("set_reminder_minute_keyboard: added close button")

    return kb
