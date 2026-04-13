from typing import List, Dict
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def edit_habits_keyboard(habits_list: List) -> InlineKeyboardMarkup:
    """
    Клавиатура редактирования привычек

    :param habits_list: Список привычек
    :type habits_list: List
    :return: Клавиатуру
    :rtype: InlineKeyboardMarkup
    """

    kb = InlineKeyboardMarkup()
    for i_id, i_habit in enumerate(habits_list):
        kb.row(InlineKeyboardButton(text=f"{i_id + 1}) {i_habit["name"]}",
                                    callback_data=f"habit_id_{i_habit["id"]}_{i_habit["name"]}"))
    kb.row(InlineKeyboardButton(text="Удалить все привычки", callback_data="delete_all_habit"),
           InlineKeyboardButton(text="Закрыть", callback_data="clear_menu"), )
    return kb


def edit_hobit_id_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text="Редактировать", callback_data=f"habit_edit_id_{habit_id}"),
           InlineKeyboardButton(text="Удалить", callback_data=f"habit_remove_id_{habit_id}"))
    return kb


def edit_hobit_id_choice_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text="Название", callback_data=f"habit_choice_id_name_{habit_id}"))
    kb.row(InlineKeyboardButton(text="Описание", callback_data=f"habit_choice_id_description_{habit_id}"))
    kb.row(InlineKeyboardButton(text="Цель", callback_data=f"habit_choice_id_goal_{habit_id}"))
    kb.row(InlineKeyboardButton(text="Срок", callback_data=f"habit_choice_id_terms_{habit_id}"))
    kb.row(InlineKeyboardButton(text="Всё", callback_data=f"habit_choice_id_all_{habit_id}"))
    return kb
