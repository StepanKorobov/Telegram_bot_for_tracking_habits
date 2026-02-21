from typing import Dict, List


def displaying_habit(hobit_list: List[Dict]) -> str:
    """
    Функция для формирования строки с привычками

    :param hobit_list: Список словарей с привычками
    :type hobit_list: List[Dict]
    :return: Строку с оформлением привычек
    :rtype: str
    """

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
        text: str = "".join(
            [text, habit_name, habit_description, habit_goal, habit_terms_date]
        )

    return text
