import logging

logger = logging.getLogger(__name__)


def displaying_habit(hobit_list: list[dict[str, str | int]]) -> str:
    """
    Формирование строки с привычками

    Args:
        hobit_list: Сообщение с данными

    Returns:
        Строку содержащую привычки
    """

    logger.debug(
        "displaying_habit: building text for habits_list, count=%s",
        len(hobit_list),
    )

    text: str = "Ваши привычки📈\n\n"

    for i_habit in hobit_list:
        habit_name: str = f"**{i_habit.get("habit_name", "Название отсутствует")}**\n"
        habit_description: str = (
            f"{i_habit.get("description", "Описание отсутствует")}\n"
        )
        habit_goal: str = f"📊 Цель: {i_habit.get("goal", "Цель отсутствует")}\n"
        habit_terms_date: str = (
            f"⏰ Срок: {i_habit.get("terms_date", "Дата отсутствует")}\n\n"
        )

        logger.debug(
            "displaying_habit: habit row, name=%r, goal=%r, terms_date=%r",
            i_habit.get("habit_name"),
            i_habit.get("goal"),
            i_habit.get("terms_date"),
        )

        text: str = "".join(
            [text, habit_name, habit_description, habit_goal, habit_terms_date]
        )

    logger.debug(
        "displaying_habit: text built, length=%s",
        len(text),
    )

    return text
