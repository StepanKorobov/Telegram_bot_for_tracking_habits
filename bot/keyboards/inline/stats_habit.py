from typing import List, Dict
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def stats_habits_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()

    kb.row(InlineKeyboardButton(text="Вывести статистику по отдельной привычке", callback_data=f"stats_habit_one"))
    kb.row(InlineKeyboardButton(text="Вывести статистику по всем привычкам", callback_data=f"stats_habit_all"))
    kb.row(InlineKeyboardButton(text="Закрыть", callback_data="clear_menu"))

    return kb


def stats_habits_list_keyboard(habit_statistic: List[Dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for i_habit in habit_statistic:
        kb.row(InlineKeyboardButton(text=f"{i_habit["habit_name"]}", callback_data=f"stats_habit_id_{i_habit["id"]}"))

    return kb
