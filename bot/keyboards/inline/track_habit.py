from typing import List, Dict
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def track_habits_keyboard(habit_list: List[Dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()

    for i_habit in habit_list:
        kb.row(InlineKeyboardButton(text=f"{i_habit["name"]}", callback_data=f"track_habit_id_{i_habit["id"]}"))

    kb.row(InlineKeyboardButton(text="Закрыть", callback_data=f"clear_menu"))

    return kb


def track_habits_confirmation_keyboard(habit_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()

    kb.row(InlineKeyboardButton(text="ПОДТВЕРДИТЬ", callback_data=f"track_habit_accepted_id_{habit_id}"))
    kb.row(InlineKeyboardButton(text="Назад", callback_data="track_habit"))
    kb.row(InlineKeyboardButton(text="Закрыть", callback_data="clear_menu"))

    return kb
