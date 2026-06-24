from typing import List, Dict
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def set_reminder_keyboard(habits: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()

    for i_habit in habits:
        kb.row(InlineKeyboardButton(
            text=f"*{i_habit["habit_name"]}* - {i_habit["habit_tracking"]["alert_time"] if i_habit["habit_tracking"]["alert_time"] else "Напоминание не установлено"}",
            callback_data=f"habit_reminder_id_{i_habit["id"]}"))

    kb.row(InlineKeyboardButton(text="Закрыть", callback_data="clear_menu"))

    return kb


def set_reminder_hour_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()

    for i_hour in range(0, 24, 4):
        kb.row(InlineKeyboardButton(text=f"{i_hour}", callback_data=f"habit_reminder_hour_{i_hour}"),
               InlineKeyboardButton(text=f"{i_hour + 1}", callback_data=f"habit_reminder_hour_{i_hour + 1}"),
               InlineKeyboardButton(text=f"{i_hour + 2}", callback_data=f"habit_reminder_hour_{i_hour + 2}"),
               InlineKeyboardButton(text=f"{i_hour + 3}", callback_data=f"habit_reminder_hour_{i_hour + 3}"),
               )

    return kb


def set_reminder_minute_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()

    for i_minute in range(0, 60, 15):
        kb.row(InlineKeyboardButton(text=f"{i_minute}", callback_data=f"habit_reminder_minute_{i_minute}"),
               InlineKeyboardButton(text=f"{i_minute + 5}", callback_data=f"habit_reminder_minute_{i_minute + 5}"),
               InlineKeyboardButton(text=f"{i_minute + 10}", callback_data=f"habit_reminder_minute_{i_minute + 10}"),
               )

    return kb
