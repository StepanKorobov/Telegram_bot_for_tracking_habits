from telebot.handler_backends import State, StatesGroup


class ReminderState(StatesGroup):
    """Состояния для установки напоминаний привычки."""

    reminder = State()
    hour_change = State()
    minute_change = State()
